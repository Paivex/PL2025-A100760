import ply.lex as lex

# Exemplo de consulta
test_query = """# DBPedia: obras de Chuck Berry
select ?nome ?desc where {
?s a dbo:MusicalArtist.
?s foaf:name "Chuck Berry"@en .
?w dbo:artist ?s.
?w foaf:name ?nome.
?w dbo:abstract ?desc
} LIMIT 1000"""

# Definição dos tokens
tokens = (
    "COMMENT",  # Comentário
    "NUMBER",   # Número
    "IDENTIFIER",
    "LBRACE",
    "RBRACE",
    "PREFIX",
    "DOT",
    "VARIABLE",
    "SELECT",
    "LIMIT",
    "WHERE",
    "OTHER"
)

def t_NUMBER(t):
    r"\d+"
    t.value = int(t.value)
    return t

t_ignore = " \t"

def t_error(t):
    print(f"Caractere inválido encontrado: {t.value[0]}")
    t.lexer.skip(1)

def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)

t_COMMENT = r"\#.*"
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_PREFIX = r"(dbo|foaf):\w+"
t_DOT = r"\."
t_VARIABLE = r"\?\w+"
t_IDENTIFIER = r'"[^"]+"@\w+'
t_SELECT = r"select"
t_LIMIT = r"LIMIT"
t_WHERE = r"where"
t_OTHER = r"\w+"

# Criar o analisador léxico
lexer = lex.lex()

# Alimentar o lexer com a query de teste
lexer.input(test_query)

# Ler e imprimir tokens
token = lexer.token()
while token:
    print(token)
    token = lexer.token()
