## Overview

We use [MkDocs](https://www.mkdocs.org/) to manage our generated documentation, and [Material for
MkDocs](https://squidfunk.github.io/mkdocs-material/getting-started/) for theming, plugins, and
extensions.

We'll call out a few cool features:

- A fully-featured search bar for our documentation using [search.suggest and
  search.highlight](https://squidfunk.github.io/mkdocs-material/setup/setting-up-site-search/#search-suggestions).
- Add "Copy to Clipboard" functionality with
  [content.code.copy](https://squidfunk.github.io/mkdocs-material/reference/code-blocks/#code-copy-button)
- We can reference code in `.py` python files directly from markdown using the following syntax:

        ```python
        {!> ../samples/path/to/code.py!}
        ```

- Lots more! Check out material for mkdocs
  [setup](https://squidfunk.github.io/mkdocs-material/setup/changing-the-colors/) and
  [reference](https://squidfunk.github.io/mkdocs-material/reference) for more ideas!

You can see the status of [documentation deployments
here](https://github.com/groundlight/python-sdk/actions/workflows/pages/pages-build-deployment). The
docs are deployed by a [github action]() that publishes changes to a `gh-pages` git branch.

## Using MkDocs

For full documentation visit [mkdocs.org](https://www.mkdocs.org).

### Commands

- `mkdocs new [dir-name]` - Create a new project.
- `mkdocs serve` - Start the live-reloading docs server.
- `mkdocs build` - Build the documentation site.
- `mkdocs -h` - Print help message and exit.

### Project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.
