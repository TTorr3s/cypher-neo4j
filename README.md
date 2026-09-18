# Cypher (Neo4j 4.4) — Zed extension

Syntax highlighting **and offline diagnostics** for the
[Cypher](https://opencypher.org/) query language in [Zed](https://zed.dev),
tuned for **Neo4j 4.4 Community Edition**.

Recognizes `.cypher`, `.cql` and `.cyp` files and highlights them using a
[tree-sitter grammar](https://github.com/TTorr3s/tree-sitter-cypher-neo4j)
maintained in a companion repository. It also launches the `cypher-lsp`
language server from the [`cypher-neo4j-lsp`](https://github.com/TTorr3s/cypher-neo4j-lsp)
workspace, which reports undefined variables, UNION column mismatches,
unaliased `WITH` expressions, aggregation misuse and syntax errors — all
without a live database.

> Status: work in progress. This is a fork being adapted to the Neo4j 4.4 CE
> dialect (keywords, clauses and functions). Highlighting coverage is still
> being extended.

## Install as a dev extension

1. Clone this repository.
2. Build the language server (once), so the extension has a binary to launch:
   ```sh
   git clone https://github.com/TTorr3s/cypher-neo4j-lsp
   cd cypher-neo4j-lsp && cargo build --release
   ```
   The extension looks for `cypher-lsp` on `PATH` first, then falls back to
   `cypher-neo4j-lsp/target/release/cypher-lsp` (see [`src/lib.rs`](src/lib.rs)).
   Put the binary on `PATH`, or keep that workspace at the sibling path.
3. Open Zed → **Extensions** → **Install Dev Extension**.
4. Point it at this cloned folder.

Zed fetches and builds the grammar declared in [`extension.toml`](extension.toml)
and compiles the Rust extension to WASM on install (needs the `wasm32-wasip1`
Rust target). No prebuilt binary is committed to this repo.

To confirm the server is running, open a `.cypher` file and check
**`dev: open language server logs`** from the command palette.

## Layout

| Path | Purpose |
| --- | --- |
| `extension.toml` | Extension manifest, pinned grammar source, language server |
| `Cargo.toml` / `src/lib.rs` | Rust WASM extension that launches `cypher-lsp` |
| `languages/cypher/config.toml` | Language config (suffixes, comments, brackets) |
| `languages/cypher/highlights.scm` | Tree-sitter highlighting queries |

## Credits

- Original Zed extension by Hari Bantwal — <https://github.com/pupli/cypher>
- Grammar: [`TTorr3s/tree-sitter-cypher-neo4j`](https://github.com/TTorr3s/tree-sitter-cypher-neo4j),
  forked from [`pupli/tree-sitter-cypher`](https://github.com/pupli/tree-sitter-cypher)
- [openCypher](https://opencypher.org/) project for the language reference

## License

This extension is released under the [MIT License](LICENSE). It began as a fork
of the original (unlicensed) `pupli/cypher` extension; the highlighting queries
are being rewritten for Neo4j 4.4, and the MIT license covers this project's own
code. The bundled `tree-sitter-cypher` grammar is fetched as an external build
dependency and keeps its own upstream terms.
