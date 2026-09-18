# scripts

Tooling to regenerate the Zed snippet completions in
[`../snippets/cypher.json`](../snippets/cypher.json).

## `generate_snippets.py`

Builds the full snippet catalog (APOC 4.4 + native Cypher builtins) from three
CSV exports taken from a live Neo4j 4.4 database. Re-running with the same CSVs
reproduces `snippets/cypher.json` byte-for-byte.

```bash
python3 scripts/generate_snippets.py --data path/to/csvs
# defaults: --data scripts/data  --out snippets/cypher.json
```

- **APOC** entries come from `apoc.help()`, which carries a typed signature, so
  parameters become tab stops (with signature defaults) and procedures get a
  final `YIELD` tab stop listing their return columns.
- **Native** functions/procedures have no typed signature in the `SHOW *`
  exports, so they use a generic `name(${1})` body. List predicates
  (`all/any/none/single/reduce`) and zero-arg builtins get tailored bodies.

Map-typed defaults are dropped (a literal `{}` inside a placeholder would break
Zed's snippet parser).

## Regenerating the CSV exports

Run these against the target Neo4j 4.4 instance and export each result to CSV
(the header row must match the column names below).

```cypher
// apoc-help.csv   -> type,name,text,signature,roles,writes,core
CALL apoc.help('') YIELD type, name, text, signature, roles, writes, core
RETURN type, name, text, signature, roles, writes, core
ORDER BY name;

// show-functions.csv  -> name,category,description
SHOW FUNCTIONS YIELD name, category, description
RETURN name, category, description
ORDER BY name;

// show-procedures.csv -> name,description,mode,worksOnSystem
SHOW PROCEDURES YIELD name, description, mode, worksOnSystem
RETURN name, description, mode, worksOnSystem
ORDER BY name;
```

> Native `SHOW FUNCTIONS` / `SHOW PROCEDURES` also expose a `signature` column.
> If you export it, the generator can be extended to give native builtins the
> same typed parameter tab stops as APOC.
