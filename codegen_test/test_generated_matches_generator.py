"""Checks that the checked-in ``generated/`` tree is exactly what ``make generate`` produces.

``generated/`` is excluded from ``LINT_PATHS``, so nothing in CI notices when generated code gets
hand-edited instead of regenerated. The cost of that is paid by the next person to run
``make generate``: they get a large unexplained diff mixed into their own PR. These checks
regenerate into a scratch directory and diff against the committed tree, so the drift is caught in
the PR that introduces it.

This module lives outside ``test/`` on purpose. ``test/conftest.py`` constructs a ``Groundlight``
client inside ``pytest_configure``, so the whole ``test/`` tree aborts before collection unless
``GROUNDLIGHT_API_TOKEN`` is set. These checks need no API access at all, and a check that only
runs for people holding a token is a check that mostly does not run.

Run them on their own with ``make test-codegen``; ``make test`` includes them too.

What these checks do **not** catch: files that are committed under ``generated/`` but that the
generator no longer produces at all, because a schema was removed from the spec. The
openapi-generator half seeds its scratch directory with a copy of the committed tree (it has to --
see ``test_openapi_client_matches_openapi_generator``), so a stale file is copied into the
comparison tree as well and shows up on both sides. This is not hypothetical: generating into an
empty directory instead shows roughly two dozen such files in ``generated/`` today, and #491 had to
delete three orphaned ``InlineResponse2002`` files by hand for exactly this reason -- the generator
drops a removed model from ``FILES`` and ``models/__init__.py`` but cannot delete its files.
Catching that needs a separate check and a cleanup of the existing backlog; it is deliberately not
in scope here.
"""

import difflib
import importlib.util
import os
import re
import shutil
import subprocess  # nosec - we only run the project's own code generators
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, List, Optional, Sequence, Set

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATED_DIR = REPO_ROOT / "generated"
PYPROJECT = REPO_ROOT / "pyproject.toml"
MAKEFILE = REPO_ROOT / "Makefile"
SPEC = "spec/public-api.yaml"

OPENAPI_GENERATOR_CLI = REPO_ROOT / "node_modules" / ".bin" / "openapi-generator-cli"

# openapi-generator-cli 2.34 loads an ESM-only proxy-agent from CommonJS, which only works on node
# versions that support require(esm). On older node it dies with ERR_REQUIRE_ESM and a page of
# minified javascript, so check the version up front and say so plainly instead.
MIN_NODE_MAJOR = 22

# Set this in CI. The openapi-generator half of the check needs node, so it skips when node is
# missing -- but a check that silently skips everywhere reads as coverage without being any. With
# this set, an unavailable generator is a failure instead of a skip.
REQUIRE_GENERATOR_ENV = "CODEGEN_CHECK_REQUIRE_GENERATOR"

# datamodel-code-generator stamps its own run time into the file header, so it differs on every
# run and has to be normalized away before comparing.
TIMESTAMP_RE = re.compile(r"^#\s+timestamp:.*$", re.MULTILINE)

# How much diff to show before truncating. Enough to see what went wrong, not so much that the
# real message scrolls away.
MAX_DIFF_LINES = 400

# Ceiling on any single generator command. openapi-generator-cli downloads its JAR from Maven
# Central the first time it runs, so a blocked or stalled network gives an indefinite hang rather
# than an error; without this the test worker just sits there. Generous, because a cold JAR
# download on a slow link is legitimately slow -- this is a hang breaker, not a performance budget.
SUBPROCESS_TIMEOUT = 600

# `node --version` is local and immediate; it only needs enough time to cover process startup.
NODE_VERSION_TIMEOUT = 30

FIX_HINT = (
    "Fix it by running `make generate` and committing the result -- do not hand-edit files under"
    " generated/.\nIf you did run `make generate` and still see this, your generator toolchain"
    " differs from the one that produced the committed tree: check the versions of black and"
    " datamodel-code-generator (pyproject.toml, and note that poetry.lock is not committed) and of"
    " openapi-generator (openapitools.json)."
)


def _datamodel_codegen_args(output: str) -> List[str]:
    """The datamodel-codegen arguments used by the `generate` Makefile target."""
    return [
        "--input",
        SPEC,
        "--output",
        output,
        "--strict-nullable",
        "--use-schema-description",
        "--output-model-type",
        "pydantic_v2.BaseModel",
        "--use-subclass-enum",
        "--output-datetime-class",
        "datetime",
    ]


def _openapi_generator_args(output: str) -> List[str]:
    """The openapi-generator-cli arguments used by the `generate` Makefile target."""
    return [
        "generate",
        "-i",
        SPEC,
        "-g",
        "python",
        "-o",
        output,
        "--additional-properties=packageName=groundlight_openapi_client",
    ]


def _skip_or_fail(reason: str) -> None:
    """Skip, unless we're somewhere (like CI) that has declared the generator must be available."""
    if os.environ.get(REQUIRE_GENERATOR_ENV):
        pytest.fail(f"{reason}\n{REQUIRE_GENERATOR_ENV} is set, so this may not be skipped.")
    pytest.skip(reason)


def _python_tool(script: str, module: str) -> List[str]:
    """Resolve a python-based tool to a command, preferring the one in the running interpreter.

    `sys.executable -m` on purpose, rather than the console script on PATH. `make generate` runs
    these tools through `poetry run`, so the versions that produced the committed tree are the ones
    in the project venv -- and pytest is running from that same venv. Resolving via PATH instead
    picks up whatever happens to be installed globally whenever the venv is not activated (running
    `pytest codegen_test` directly, or from an IDE). Both tools reformat their output, so a version
    difference shows up as formatting diffs across the whole tree that look like generated-code
    drift and are not.
    """
    if importlib.util.find_spec(module) is not None:
        return [sys.executable, "-m", module]
    found = shutil.which(script)
    if found:
        return [found]
    _skip_or_fail(f"neither `{sys.executable} -m {module}` nor a `{script}` on PATH is available.")
    raise AssertionError("unreachable")  # _skip_or_fail always raises


def _tail(output: str, keep: int = 30) -> str:
    """The last few lines of command output. Generators can emit a lot of unhelpful noise."""
    lines = output.splitlines()
    if len(lines) <= keep:
        return output
    return "\n".join([f"... {len(lines) - keep} earlier lines suppressed ..."] + lines[-keep:])


def _run(cmd: Sequence[str]) -> None:
    """Run a generator command from the repo root, failing the test with its output if it errors."""
    printable = " ".join(str(part) for part in cmd)
    try:
        result = subprocess.run(  # nosec
            cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=False, timeout=SUBPROCESS_TIMEOUT
        )
    except subprocess.TimeoutExpired:
        pytest.fail(
            f"`{printable}` did not finish within {SUBPROCESS_TIMEOUT}s and was killed.\n"
            "openapi-generator-cli downloads its JAR from Maven Central on first use, so the usual"
            " cause is a stalled or blocked download rather than a problem with generated/."
        )
    if result.returncode != 0:
        pytest.fail(
            f"`{printable}` failed with exit code {result.returncode}\n"
            f"--- stdout ---\n{_tail(result.stdout)}\n--- stderr ---\n{_tail(result.stderr)}"
        )


def _node_major_version() -> Optional[int]:
    """The major version of node on PATH, or None if node isn't installed or isn't answering."""
    if shutil.which("node") is None:
        return None
    try:
        result = subprocess.run(  # nosec
            ["node", "--version"], capture_output=True, text=True, check=False, timeout=NODE_VERSION_TIMEOUT
        )
    except subprocess.TimeoutExpired:
        return None
    match = re.match(r"v(\d+)\.", result.stdout.strip())
    return int(match.group(1)) if match else None


@contextmanager
def _scratch_dir() -> Iterator[Path]:
    """A temporary directory inside the repo, cleaned up afterwards.

    Inside the repo on purpose, and `--config` on our own black call is not a substitute -- the
    problem is a black run we do not control. datamodel-code-generator formats its output by
    calling black itself, and that internal call discovers configuration by walking up from the
    `--output` path. Point `--output` at /tmp and it finds no pyproject.toml, so it formats at
    black's default 88 columns instead of this project's 120.

    The damage is not repairable afterwards. Wrapping a call across lines at 88 columns leaves a
    magic trailing comma behind, and black treats that comma as an explicit instruction to keep the
    construct exploded -- so the later `black --config` pass at 120 columns leaves those lines
    alone. Measured on the current spec: generating into /tmp and then running our `--config` pass
    still differs from the committed tree by 135 lines, and adding `--skip-magic-trailing-comma`
    takes that to 0, which is what identifies the mechanism.

    Non-hidden on purpose too, since black skips dot-directories.
    """
    path = Path(tempfile.mkdtemp(prefix="codegen-check-tmp-", dir=REPO_ROOT))
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def _black(paths: Sequence[Path]) -> None:
    """Run black over `paths` the way `make generate`'s trailing `black .` would."""
    cmd = _python_tool("black", "black") + ["--quiet", "--config", str(PYPROJECT)]
    _run(cmd + [str(path) for path in paths])


def _normalize(text: str) -> str:
    return TIMESTAMP_RE.sub("#   timestamp: <normalized>", text)


def _read(path: Path) -> Optional[str]:
    """Read a file as normalized text, or None if it isn't text."""
    try:
        return _normalize(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        return None


def _tree_files(root: Path) -> List[str]:
    """Relative paths of every comparable file under `root`, ignoring python bytecode."""
    files = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if "__pycache__" in relative.parts or relative.suffix == ".pyc":
            continue
        files.append(relative.as_posix())
    return sorted(files)


def _truncate(lines: List[str]) -> List[str]:
    if len(lines) <= MAX_DIFF_LINES:
        return lines
    return lines[:MAX_DIFF_LINES] + [
        f"... {len(lines) - MAX_DIFF_LINES} more diff lines suppressed. Run `make generate` to see"
        " the whole diff in git."
    ]


def _file_diff(committed: Path, regenerated: Path, label: str) -> List[str]:
    """A unified diff of one file, or a note that it differs but isn't text."""
    old, new = _read(committed), _read(regenerated)
    if old is None or new is None:
        return [f"{label}: binary files differ"]
    return list(
        difflib.unified_diff(
            old.splitlines(),
            new.splitlines(),
            fromfile=f"{label} (committed)",
            tofile=f"{label} (regenerated)",
            lineterm="",
        )
    )


def _tree_diff(committed_root: Path, regenerated_root: Path, ignore: Set[str]) -> str:
    """Compare two trees. Returns "" when they agree, otherwise a report of how they differ."""
    committed_files = [name for name in _tree_files(committed_root) if name not in ignore]
    regenerated_files = [name for name in _tree_files(regenerated_root) if name not in ignore]

    missing = sorted(set(regenerated_files) - set(committed_files))
    unexpected = sorted(set(committed_files) - set(regenerated_files))
    lines: List[str] = []
    if missing:
        lines.append("The generator produces these files, but they are not committed:")
        lines += [f"  + generated/{name}" for name in missing]
    if unexpected:
        lines.append("These files are committed, but the generator does not produce them:")
        lines += [f"  - generated/{name}" for name in unexpected]

    for name in sorted(set(committed_files) & set(regenerated_files)):
        diff = _file_diff(committed_root / name, regenerated_root / name, f"generated/{name}")
        if diff:
            lines += [""] + diff
    return "\n".join(_truncate(lines))


def test_model_py_matches_datamodel_codegen() -> None:
    """`generated/model.py` must be what datamodel-codegen produces from the committed spec.

    This half of `make generate` is pure python and already a dev dependency, so it always runs.
    """
    with _scratch_dir() as scratch:
        regenerated = scratch / "model.py"
        _run(_python_tool("datamodel-codegen", "datamodel_code_generator") + _datamodel_codegen_args(str(regenerated)))
        _black([regenerated])

        diff = _file_diff(GENERATED_DIR / "model.py", regenerated, "generated/model.py")
        assert not diff, (
            "generated/model.py is not what datamodel-codegen produces from spec/public-api.yaml.\n"
            + "\n".join(_truncate(diff))
            + f"\n\n{FIX_HINT}"
        )


def test_openapi_client_matches_openapi_generator() -> None:
    """The openapi-generator half of `generated/` must be what openapi-generator-cli produces.

    Skipped when the generator isn't available -- it needs node and a JRE, neither of which is
    guaranteed on a contributor's machine. CI sets `CODEGEN_CHECK_REQUIRE_GENERATOR` so that a
    missing generator fails there instead of quietly skipping.
    """
    node_major = _node_major_version()
    if node_major is None:
        _skip_or_fail("node is not installed, so openapi-generator-cli cannot run.")
    elif node_major < MIN_NODE_MAJOR:
        _skip_or_fail(
            f"node {node_major} is too old for openapi-generator-cli, which needs node"
            f" >= {MIN_NODE_MAJOR}. `make generate` does not work on this node either."
        )
    if not OPENAPI_GENERATOR_CLI.exists():
        _skip_or_fail(f"{OPENAPI_GENERATOR_CLI.relative_to(REPO_ROOT)} is missing. Run `make install-generator`.")
    if shutil.which("java") is None:
        _skip_or_fail("java is not installed, and openapi-generator-cli needs a JRE to run.")

    with _scratch_dir() as scratch:
        regenerated = scratch / "generated"
        # Seed the scratch directory with the committed tree rather than generating into an empty
        # one, because that is what `make generate` actually does. The generator leaves files it
        # considers user-editable (generated/test/*.py) alone when they already exist, and the
        # FILES manifest it writes lists only the files it actually wrote -- so generating into an
        # empty directory produces a legitimately different manifest.
        shutil.copytree(GENERATED_DIR, regenerated, ignore=shutil.ignore_patterns("__pycache__"))
        _run([str(OPENAPI_GENERATOR_CLI)] + _openapi_generator_args(str(regenerated)))
        _black(sorted(regenerated.rglob("*.py")))

        # model.py belongs to the datamodel-codegen half, checked by the test above.
        # The FILES manifest is excluded because it is not a function of the spec: the generator
        # lists only the files it actually wrote, and it refuses to overwrite an existing
        # generated/test/*.py. So the manifest produced when a schema is first added (test file
        # absent, therefore written and listed) differs from the one produced by every run after
        # that (test file present, therefore skipped and unlisted) -- `make generate` is not
        # idempotent in this one file. Comparing it would fail every PR that adds a schema.
        diff = _tree_diff(GENERATED_DIR, regenerated, ignore={"model.py", ".openapi-generator/FILES"})
        assert not diff, f"generated/ is not what openapi-generator-cli produces.\n{diff}\n\n{FIX_HINT}"


def test_generate_target_matches_this_check() -> None:
    """The commands checked here must stay the same ones `make generate` runs.

    Without this, someone can change `make generate` and leave the checks above silently
    validating a command nobody runs any more.
    """
    recipe: List[str] = []
    in_target = False
    for line in MAKEFILE.read_text(encoding="utf-8").splitlines():
        if line.startswith("generate:"):
            in_target = True
            continue
        if not in_target:
            continue
        if line.startswith("#"):  # a comment doesn't end a recipe
            continue
        if line and not line.startswith("\t"):
            break
        recipe.append(line.rstrip("\\"))  # unwrap line continuations
    assert recipe, "could not find the `generate` target in the Makefile"
    flattened = " ".join(" ".join(recipe).split())

    for expected in (
        " ".join(_datamodel_codegen_args("generated/model.py")),
        " ".join(_openapi_generator_args("./generated")),
        "black .",  # these checks reformat their scratch output because `make generate` does
    ):
        assert expected in flattened, (
            f"`make generate` no longer runs:\n  {expected}\nIt runs:\n  {flattened}\n"
            f"Update {Path(__file__).relative_to(REPO_ROOT)} to match, so these checks keep"
            " checking the real generate command."
        )
