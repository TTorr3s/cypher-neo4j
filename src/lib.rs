//! Zed extension glue for the offline Cypher (Neo4j 4.4) language server.
//!
//! The extension itself carries no analysis logic: it only tells Zed how to
//! launch the `cypher-lsp` binary from the sibling `cypher-neo4j-lsp` workspace.
//! The binary speaks LSP over stdio, so no args or env are needed.

use zed_extension_api::{self as zed, Command, LanguageServerId, Result, Worktree};

/// Local release build of the language server, used when `cypher-lsp` is not on
/// PATH. This is a personal/dev wiring; publishing the extension would instead
/// download a released binary here.
const RELEASE_BINARY: &str =
    "/Users/jesus/sources/personal/cypher-neo4j-lsp/target/release/cypher-lsp";

struct CypherExtension;

impl zed::Extension for CypherExtension {
    fn new() -> Self {
        Self
    }

    fn language_server_command(
        &mut self,
        _language_server_id: &LanguageServerId,
        worktree: &Worktree,
    ) -> Result<Command> {
        // Prefer a `cypher-lsp` on PATH; fall back to the local release build.
        let command = worktree
            .which("cypher-lsp")
            .unwrap_or_else(|| RELEASE_BINARY.to_string());
        Ok(Command {
            command,
            args: vec![],
            env: vec![],
        })
    }
}

zed::register_extension!(CypherExtension);
