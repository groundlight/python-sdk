# Documentation

We use [MkDocs](https://www.mkdocs.org/) to manage our generated documentation, and [Material for
MkDocs](https://squidfunk.github.io/mkdocs-material/getting-started/) for theming, plugins, and
extensions.

We'll call out a few cool features:

- We can reference code in `.py` python files directly from markdown using the following syntax. That way, we (a) don't have to
  duplicate code in markdown, and (b) since the code is in `.py` files, we can run unit tests over
  all of the code that is included in our docs!

        ```python
        \{!> ../samples/path/to/code.py!}
        ```

- Add "copy to Clipboard" functionality with
  [content.code.copy](https://squidfunk.github.io/mkdocs-material/reference/code-blocks/#code-copy-button)
- Lots more! Check out material for mkdocs
  [setup](https://squidfunk.github.io/mkdocs-material/setup/changing-the-colors/) and
  [reference](https://squidfunk.github.io/mkdocs-material/reference) for more ideas!
