; Cypher highlighting for Zed — targets the tree-sitter-cypher grammar
; (openCypher core as understood by Neo4j 4.4). Only node types and tokens
; that the grammar actually produces are referenced here.

; --- Comments -------------------------------------------------------------
(comment) @comment

; --- Literals -------------------------------------------------------------
(string_literal) @string
(escaped_char) @string.escape
(number_literal) @number
(boolean_literal) @boolean
"null" @constant.builtin

; --- Identifiers ----------------------------------------------------------
(variable) @variable
(parameter) @variable.special            ; $param, $0

; Schema names
(label_name) @type                       ; node label   :Person
(rel_type_name) @type                    ; rel type      :KNOWS
(property_key_name) @property            ; map / property keys
(procedure_result_field) @property       ; YIELD fields

; Calls
(function_invocation (function_name) @function)
(procedure_name) @function               ; db.labels, apoc.*

; --- Keywords -------------------------------------------------------------
[
  "profile"
  "explain"
  "match"
  "optional"
  "foreach"
  "unwind"
  "as"
  "merge"
  "on"
  "create"
  "set"
  "detach"
  "delete"
  "remove"
  "call"
  "yield"
  "with"
  "return"
  "union"
  "all"
  "where"
  "order"
  "by"
  "skip"
  "limit"
  "distinct"
  "asc"
  "ascending"
  "desc"
  "descending"
  "case"
  "when"
  "then"
  "else"
  "end"
  "exists"
  "any"
  "none"
  "single"

  ; LOAD CSV
  "load" "csv" "headers" "from" "fieldterminator"
  ; USING hints
  "using" "index" "indexes" "seek" "scan" "join"
  ; SHOW commands
  "show" "constraint" "constraints" "function" "functions"
  "procedure" "procedures" "database" "databases"
  "transaction" "transactions" "brief" "verbose" "output"
  "executable" "current" "user" "built" "defined" "populated"
  "default" "home"
  ; Schema DDL (CREATE/DROP INDEX | CONSTRAINT)
  "for" "require" "assert" "if" "drop"
  "unique" "node" "relationship" "rel" "key" "property"
  "existence" "exist"
  "btree" "fulltext" "lookup" "range" "text" "point"
] @keyword

; Boolean / predicate operators that are spelled as words
[
  "and"
  "or"
  "xor"
  "not"
  "in"
  "is"
  "starts"
  "ends"
  "contains"
] @keyword.operator

; --- Operators ------------------------------------------------------------
[
  "="
  "+="
  "<>"
  "<"
  ">"
  "<="
  ">="
  "+"
  "-"
  "*"
  "/"
  "%"
  "^"
  ".."
] @operator

; Relationship arrows / connectors
[
  (left_arrow_head)
  (right_arrow_head)
  (dash)
] @operator

; --- Punctuation ----------------------------------------------------------
[
  "("
  ")"
  "["
  "]"
  "{"
  "}"
] @punctuation.bracket

[
  ","
  "."
  ":"
  ";"
  "|"
] @punctuation.delimiter
