"""Checks that the committed `generated/` tree is exactly what `make generate` produces.

`generated/` is excluded from linting (see `LINT_PATHS` in the Makefile), so nothing in CI
notices when generated code is hand-edited instead of regenerated. Nothing is usually
functionally wrong when that happens -- the cost is that the next person to run
`make generate` gets a large unexplained diff mixed into their own PR. These tests re-run
the generators into a scratch tree and diff the result against what is committed.

They live outside `test/` on purpose: `test/conftest.py` constructs a `Groundlight()` client
in `pytest_configure`, so everything under `test/` needs a GROUNDLIGHT_API_TOKEN before
collection even starts. These checks need no API access, and putting them where a token is
required would mean they never ran.
"""

import difflib
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, Iterator, List, Optional

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
GENERATED_DIR = REPO_ROOT / "generated"
MAKEFILE = REPO_ROOT / "Makefile"
OPENAPI_GENERATOR_CLI = REPO_ROOT / "node_modules" / ".bin" / "openapi-generator-cli"

# Set this (CI does) to turn "openapi-generator-cli is not available here" from a skip into a
# failure. A check that quietly skips everywhere is worse than no check, because it reads as
# coverage.
REQUIRE_GENERATOR_ENV_VAR = "REQUIRE_OPENAPI_GENERATOR"

FIX_HINT = "Run `make generate` and commit the result, rather than hand-editing `generated/`."

# datamodel-codegen stamps the time of the run into its file header, so this one line
# legitimately differs on every run and has to be normalized away.
CODEGEN_TIMESTAMP_RE = re.compile(r"^#\s+timestamp:.*$", re.MULTILINE)

# Failure messages carry the real diff, but a whole-tree regeneration diff can be enormous.
MAX_DIFF_LINES = 400


def _generate_recipe_commands() -> List[str]:
    """The shell commands in the Makefile's `generate` target, with continuations joined.

    These are parsed out of the Makefile rather than duplicated here so that changing how the
    SDK is generated cannot leave these tests silently checking the old way of generating it.
    """
    lines = MAKEFILE.read_text().splitlines()
    starts = [i for i, line in enumerate(lines) if re.match(r"^generate:", line)]
    assert len(starts) == 1, f"expected exactly one `generate:` target in {MAKEFILE}, found {len(starts)}"

    commands: List[str] = []
    for line in lines[starts[0] + 1 :]:
        if line.startswith("#"):  # a comment column-0 inside a recipe does not end it
            continue
        if not line.startswith("\t"):  # first non-recipe line ends the recipe
            break
        body = line.lstrip("\t").strip()
        if commands and commands[-1].endswith("\\"):
            commands[-1] = f"{commands[-1][:-1].strip()} {body}"
        else:
            commands.append(body)
    assert commands, f"found no commands in the `generate` target of {MAKEFILE}"
    return commands


def _recipe_command(tool: str) -> List[str]:
    """The `make generate` command line that runs `tool`, split into argv."""
    matches = [command for command in _generate_recipe_commands() if tool in command]
    assert len(matches) == 1, f"expected exactly one `{tool}` command in `make generate`, found {matches}"
    return shlex.split(matches[0])


def _retarget(command: List[str], old: str, new: str) -> List[str]:
    """Point a generator command at the scratch tree instead of the committed one."""
    assert old in command, f"expected `{old}` as an argument in `make generate`'s command: {command}"
    return [new if argument == old else argument for argument in command]


def _venv_command(command: List[str]) -> List[str]:
    """Rewrite `poetry run <tool> ...` to call `<tool>` from the environment running these tests.

    We are already inside the poetry environment, so this runs the same versions `make generate`
    would while avoiding a nested `poetry run`.
    """
    if command[:2] == ["poetry", "run"]:
        command = command[2:]
    executable = Path(sys.executable).parent / command[0]
    if not executable.exists():
        found = shutil.which(command[0])
        assert found, f"`{command[0]}` is not installed in this environment -- run `make install`"
        executable = Path(found)
    return [str(executable), *command[1:]]


def _run(command: List[str], what: str) -> None:
    result = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        pytest.fail(
            f"Could not run {what} (exit {result.returncode}), so we cannot tell whether `generated/` is"
            f" up to date.\ncommand: {shlex.join(command)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


def _run_black(paths: List[Path]) -> None:
    """Format `paths` the way `make generate`'s final `black .` would."""
    if not paths:
        return
    command = _venv_command(_recipe_command("black"))
    assert command[-1] == ".", f"expected `make generate` to end with `black .`, got {command}"
    # Files are passed explicitly instead of handing black the scratch directory: black skips
    # gitignored paths when it walks a directory, and the scratch directory is gitignored.
    _run([*command[:-1], *(str(path) for path in paths)], "black")


@pytest.fixture(name="scratch_dir")
def fixture_scratch_dir() -> Iterator[Path]:
    """A scratch directory for generator output, inside the repo.

    It has to be inside the repo: both datamodel-codegen (which formats its own output) and
    black find the project's `[tool.black]` settings by walking up from the paths they write, so
    generating into /tmp silently produces black's default 88-column style and every comparison
    below fails for the wrong reason.
    """
    with tempfile.TemporaryDirectory(dir=REPO_ROOT, prefix="codegen-scratch-") as scratch:
        yield Path(scratch)


def _normalize(source: str) -> str:
    return CODEGEN_TIMESTAMP_RE.sub("#   timestamp: <normalized by test_codegen>", source)


def _file_diff(relative_path: str, committed: str, regenerated: str) -> List[str]:
    return list(
        difflib.unified_diff(
            committed.splitlines(),
            regenerated.splitlines(),
            fromfile=f"generated/{relative_path} (committed)",
            tofile=f"generated/{relative_path} (freshly generated)",
            lineterm="",
        )
    )


def _truncated(diff_lines: List[str]) -> str:
    if len(diff_lines) <= MAX_DIFF_LINES:
        return "\n".join(diff_lines)
    hidden = len(diff_lines) - MAX_DIFF_LINES
    return "\n".join([*diff_lines[:MAX_DIFF_LINES], f"... {hidden} more diff lines suppressed ..."])


def _tree_contents(root: Path) -> Dict[str, str]:
    return {
        path.relative_to(root).as_posix(): path.read_text(errors="replace")
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }


def test_generated_model_matches_datamodel_codegen(scratch_dir: Path) -> None:
    """`generated/model.py` must be exactly what `make generate`'s datamodel-codegen call writes.

    This half of the generator is pure Python and already a project dependency, so it always runs.
    """
    regenerated = scratch_dir / "model.py"
    command = _retarget(_venv_command(_recipe_command("datamodel-codegen")), "generated/model.py", str(regenerated))
    _run(command, "datamodel-codegen")
    _run_black([regenerated])

    committed_text = _normalize((GENERATED_DIR / "model.py").read_text())
    regenerated_text = _normalize(regenerated.read_text())
    if committed_text != regenerated_text:
        diff = _truncated(_file_diff("model.py", committed_text, regenerated_text))
        pytest.fail(
            "generated/model.py is not what datamodel-codegen produces -- it looks hand-edited."
            f" {FIX_HINT}\n(The `timestamp:` header line is normalized out, so it is not the"
            f" cause of this diff.)\n\n{diff}"
        )


def _openapi_generator_unavailable_reason() -> Optional[str]:
    """Why the openapi-generator half cannot run here, or None if it can."""
    if not shutil.which("node"):
        return "node is not installed, and openapi-generator-cli needs it"
    if not OPENAPI_GENERATOR_CLI.exists():
        return f"{OPENAPI_GENERATOR_CLI.relative_to(REPO_ROOT)} is missing -- run `make install-generator`"
    if not shutil.which("java"):
        return "openapi-generator-cli runs a Java jar, and `java` is not on PATH"
    return None


def test_generated_client_matches_openapi_generator(scratch_dir: Path) -> None:
    """Everything openapi-generator owns under `generated/` must match a fresh run.

    Skipped when node/java/the generator CLI are unavailable, since neither is guaranteed on a
    contributor's machine -- but CI sets REQUIRE_OPENAPI_GENERATOR so that it cannot skip there.
    """
    reason = _openapi_generator_unavailable_reason()
    if reason:
        if os.environ.get(REQUIRE_GENERATOR_ENV_VAR):
            pytest.fail(f"{REQUIRE_GENERATOR_ENV_VAR} is set, so this check is not allowed to skip here, but {reason}.")
        pytest.skip(f"{reason}. (Set {REQUIRE_GENERATOR_ENV_VAR}=1 to make this a failure instead of a skip.)")

    # Regenerate over a *copy* of the committed tree rather than into an empty directory:
    # openapi-generator leaves already-existing files alone (the per-model stubs under
    # generated/test/, for instance) and records only the files it wrote in
    # .openapi-generator/FILES, so generating from empty yields a legitimately different
    # manifest. Copying first reproduces what `make generate` actually does.
    regenerated_dir = scratch_dir / "generated"
    shutil.copytree(GENERATED_DIR, regenerated_dir, ignore=shutil.ignore_patterns("__pycache__"))
    _run(_retarget(_recipe_command("openapi-generator-cli"), "./generated", str(regenerated_dir)), "openapi-generator")
    _run_black(sorted(regenerated_dir.rglob("*.py")))

    committed = _tree_contents(GENERATED_DIR)
    regenerated = _tree_contents(regenerated_dir)
    # model.py comes from datamodel-codegen, not from openapi-generator; the test above owns it.
    committed.pop("model.py", None)
    regenerated.pop("model.py", None)

    missing = sorted(set(regenerated) - set(committed))
    differing = sorted(path for path in regenerated if path in committed and committed[path] != regenerated[path])
    if not missing and not differing:
        return

    report = ["generated/ is not what openapi-generator produces -- it looks hand-edited.", FIX_HINT, ""]
    if missing:
        report += ["Files the generator produces that are not committed:", *(f"  generated/{p}" for p in missing), ""]
    if differing:
        report += ["Committed files that differ from a fresh run:", *(f"  generated/{p}" for p in differing), ""]
    diff_lines: List[str] = []
    for relative_path in differing:
        diff_lines += _file_diff(relative_path, committed[relative_path], regenerated[relative_path])
    report.append(_truncated(diff_lines))
    pytest.fail("\n".join(report))
