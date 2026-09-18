#!/usr/bin/env python3
"""Generate snippets/cypher.json (Zed snippet completions) from Neo4j 4.4 CSV exports.

Sources (see scripts/README.md for the Cypher used to produce them):
  - apoc-help.csv        : CALL apoc.help('')            -> typed APOC signatures
  - show-functions.csv   : SHOW FUNCTIONS                -> native Cypher functions
  - show-procedures.csv  : SHOW PROCEDURES               -> native Cypher procedures

APOC entries get parameter tab stops from their typed signature, plus a final
YIELD tab stop listing a procedure's return columns. Native builtins carry no
typed signature in these exports, so they use a generic `name(${1})` body, with
tailored bodies for the list predicates and zero-arg builtins.

Usage:
  python3 scripts/generate_snippets.py [--data DIR] [--out FILE]

Deterministic: re-running with the same CSVs reproduces the file byte-for-byte.
"""
import argparse
import csv
import json
import os
import re

# --- native builtin bodies (no typed signature available in SHOW * exports) ---
SPECIAL = {
    "all":    "all(${1:x} IN ${2:list} WHERE ${3:predicate})",
    "any":    "any(${1:x} IN ${2:list} WHERE ${3:predicate})",
    "none":   "none(${1:x} IN ${2:list} WHERE ${3:predicate})",
    "single": "single(${1:x} IN ${2:list} WHERE ${3:predicate})",
    "reduce": "reduce(${1:acc} = ${2:init}, ${3:x} IN ${4:list} | ${5:expr})",
    "exists": "exists(${1:pattern})",
}
ZERO_ARG_FUNC = {"pi", "rand", "e", "timestamp", "randomUUID"}
ZERO_ARG_PROC = {
    "db.labels", "db.relationshipTypes", "db.propertyKeys", "db.constraints",
    "db.indexes", "db.schema.visualization", "dbms.components", "dbms.procedures",
    "dbms.functions",
}


# --- signature parsing (APOC) -------------------------------------------------
def split_top(s):
    """Split by top-level commas, respecting (), {}, []."""
    parts, depth, cur = [], 0, ""
    for ch in s:
        if ch in "({[":
            depth += 1
            cur += ch
        elif ch in ")}]":
            depth -= 1
            cur += ch
        elif ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur)
    return [p.strip() for p in parts if p.strip()]


def match_paren(s, open_idx):
    """Return index of the ) matching the ( at open_idx."""
    depth = 0
    for i in range(open_idx, len(s)):
        if s[i] in "({[":
            depth += 1
        elif s[i] in ")}]":
            depth -= 1
            if depth == 0:
                return i
    return -1


def parse_signature(sig):
    """-> (name, params, yield_cols). params: list of (pname, default, is_string)."""
    op = sig.find("(")
    if op == -1:
        return sig.strip(), [], []
    name = sig[:op].strip()
    cp = match_paren(sig, op)
    if cp == -1:
        return name, [], []
    params = []
    for raw in split_top(sig[op + 1:cp]):
        m = re.match(r"^(.*?)\s*::\s*(.+)$", raw)
        left = m.group(1).strip() if m else raw.strip()
        typ = m.group(2).strip() if m else ""
        if "=" in left:
            pname, default = [x.strip() for x in left.split("=", 1)]
        else:
            pname, default = left.strip(), ""
        params.append((pname, default, "STRING" in typ))
    yields = []
    rest = sig[cp + 1:]
    rop = rest.find("(")
    if rop != -1:
        rcp = match_paren(rest, rop)
        if rcp != -1:
            for raw in split_top(rest[rop + 1:rcp]):
                m = re.match(r"^(.*?)\s*::", raw)
                col = m.group(1).strip() if m else raw.strip()
                if col and "::" in raw:
                    yields.append(col)
    return name, params, yields


def placeholder(pname, default, is_string):
    # braces/$ in a default would break snippet placeholder parsing -> use the name
    if default and not any(c in default for c in "{}$"):
        if is_string and not (default.startswith("'") or default.startswith('"')):
            return f"'{default}'"
        return default
    return pname


def clean(text):
    t = re.sub(r"\s+", " ", (text or "").strip())
    return t if len(t) <= 160 else t[:157] + "..."


# --- builders -----------------------------------------------------------------
def add_apoc(snips, path):
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            name = (r.get("name") or "").strip()
            sig = (r.get("signature") or "").strip()
            if not name or not sig:
                continue
            _, params, yields = parse_signature(sig)
            stops = [f"${{{i}:{placeholder(*p)}}}" for i, p in enumerate(params, 1)]
            body = f"{name}({', '.join(stops)})"
            if (r.get("type") or "").strip() == "procedure":
                if yields:
                    body += " YIELD ${%d:%s}" % (len(params) + 1, ", ".join(yields))
                tag = "APOC proc"
            else:
                tag = "APOC func"
            desc = clean(r.get("text"))
            snips[name] = {
                "prefix": name,
                "body": body,
                "description": f"[{tag}] {desc}" if desc else f"[{tag}] {name}",
            }


def add_native(snips, path, tag, body_fn):
    seen = set()
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            name = (r.get("name") or "").strip()
            if not name or name.startswith("apoc.") or name in seen:
                continue
            seen.add(name)
            if name in snips:
                continue
            desc = clean(r.get("description"))
            snips[name] = {
                "prefix": name,
                "body": body_fn(name),
                "description": f"[{tag}] {desc}" if desc else f"[{tag}] {name}",
            }


def func_body(name):
    if name in SPECIAL:
        return SPECIAL[name]
    if name in ZERO_ARG_FUNC:
        return f"{name}()"
    return f"{name}(${{1}})"


def proc_body(name):
    if name in ZERO_ARG_PROC:
        return f"{name}()"
    return f"{name}(${{1}})"


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", default=os.path.join(here, "data"),
                    help="directory holding the three CSV exports (default: scripts/data)")
    ap.add_argument("--out", default=os.path.join(root, "snippets", "cypher.json"),
                    help="output snippets file (default: snippets/cypher.json)")
    args = ap.parse_args()

    snips = {}
    add_apoc(snips, os.path.join(args.data, "apoc-help.csv"))
    n_apoc = len(snips)
    add_native(snips, os.path.join(args.data, "show-functions.csv"), "fn", func_body)
    n_fn = len(snips) - n_apoc
    add_native(snips, os.path.join(args.data, "show-procedures.csv"), "proc", proc_body)
    n_proc = len(snips) - n_apoc - n_fn

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(snips, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {len(snips)} snippets -> {args.out}")
    print(f"  APOC: {n_apoc} | native functions: {n_fn} | native procedures: {n_proc}")


if __name__ == "__main__":
    main()
