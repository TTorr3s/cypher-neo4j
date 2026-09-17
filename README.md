# Cypher (Neo4j 4.4) — Zed extension

Syntax highlighting for the [Cypher](https://opencypher.org/) query language in
[Zed](https://zed.dev), tuned for **Neo4j 4.4 Community Edition**.

Recognizes `.cypher`, `.cql` and `.cyp` files and highlights them using the
[`tree-sitter-cypher`](https://github.com/pupli/tree-sitter-cypher) grammar.

> Status: work in progress. This is a fork being adapted to the Neo4j 4.4 CE
> dialect (keywords, clauses and functions). Highlighting coverage is still
> being extended.

## Install as a dev extension

1. Clone this repository.
2. Open Zed → **Extensions** → **Install Dev Extension**.
3. Point it at the cloned folder.

Zed fetches and builds the grammar declared in [`extension.toml`](extension.toml)
on first load, so no prebuilt binary is committed to this repo.

## Layout

| Path | Purpose |
| --- | --- |
| `extension.toml` | Extension manifest and pinned grammar source |
| `languages/cypher/config.toml` | Language config (suffixes, comments, brackets) |
| `languages/cypher/highlights.scm` | Tree-sitter highlighting queries |

## Credits

- Original Zed extension by Hari Bantwal — <https://github.com/pupli/cypher>
- Grammar: [`pupli/tree-sitter-cypher`](https://github.com/pupli/tree-sitter-cypher)
- [openCypher](https://opencypher.org/) project for the language reference

## License

See the upstream project for licensing of the original extension and grammar.
