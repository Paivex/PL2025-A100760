import ply.lex as lex
import re

# ---------------------------------------------------
# Lista de tokens (incluindo WRITE e todos os keywords)
# ---------------------------------------------------
tokens = [
    # 1) Keywords
    'PROGRAM', 'VAR', 'BEGIN', 'END',
    'FUNCTION', 'PROCEDURE',
    'IF', 'THEN', 'ELSE',
    'WHILE', 'DO',
    'AND', 'OR',
    'FOR', 'TO', 'DOWNTO',
    'WRITELN', 'WRITE', 'READLN',
    'INTEGER', 'BOOLEAN', 'STRING', 'REAL',
    'TRUE', 'FALSE',
    'DIV', 'MOD',
    'ARRAY', 'OF',

    # 2) Identificadores e literais
    'ID', 'NUMBER', 'STRING_LITERAL',

    # 3) Operadores e símbolos
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'EQUAL', 'NE', 'LT', 'LE', 'GT', 'GE',
    'ASSIGN',  # :=
    'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET',
    'COLON', 'SEMICOLON', 'COMMA',
    'DOT', 'DOTDOT'
]

# ---------------------------------------------------
# 1) Definição de cada keyword (REGEX antes de ID)
#    Usaremos re.IGNORECASE ao construir o lexer para case-insensitive
# ---------------------------------------------------

def t_PROGRAM(t):
    r'\bprogram\b'
    return t

def t_VAR(t):
    r'\bvar\b'
    return t

def t_BEGIN(t):
    r'\bbegin\b'
    return t

def t_END(t):
    r'\bend\b'
    return t

def t_FUNCTION(t):
    r'\bfunction\b'
    return t

def t_PROCEDURE(t):
    r'\bprocedure\b'
    return t

def t_IF(t):
    r'\bif\b'
    return t

def t_THEN(t):
    r'\bthen\b'
    return t

def t_ELSE(t):
    r'\belse\b'
    return t

def t_WHILE(t):
    r'\bwhile\b'
    return t

def t_DO(t):
    r'\bdo\b'
    return t

def t_AND(t):
    r'\band\b'
    return t

def t_OR(t):
    r'\bor\b'
    return t

def t_FOR(t):
    r'\bfor\b'
    return t

def t_TO(t):
    r'\bto\b'
    return t

def t_DOWNTO(t):
    r'\bdownto\b'
    return t

def t_WRITELN(t):
    r'\bwriteln\b'
    return t

def t_WRITE(t):
    r'\bwrite\b'
    return t

def t_READLN(t):
    r'\breadln\b'
    return t

def t_INTEGER(t):
    r'\binteger\b'
    return t

def t_BOOLEAN(t):
    r'\bboolean\b'
    return t

def t_STRING(t):
    r'\bstring\b'
    return t

def t_REAL(t):
    r'\breal\b'
    return t

def t_TRUE(t):
    r'\btrue\b'
    t.value = True
    return t

def t_FALSE(t):
    r'\bfalse\b'
    t.value = False
    return t

def t_DIV(t):
    r'\bdiv\b'
    return t

def t_MOD(t):
    r'\bmod\b'
    return t

def t_ARRAY(t):
    r'\barray\b'
    return t

def t_OF(t):
    r'\bof\b'
    return t

# ---------------------------------------------------
# 2) Identificador (ID): tudo que não bate em uma keyword
# ---------------------------------------------------
def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    return t

# ---------------------------------------------------
# 3) Número inteiro
# ---------------------------------------------------
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# ---------------------------------------------------
# 4) String literal entre aspas simples
# ---------------------------------------------------
def t_STRING_LITERAL(t):
    r"'([^\\']|\\.)*'"
    t.value = t.value[1:-1]  # remove as aspas
    return t

# ---------------------------------------------------
# 5) Operadores e símbolos
#    Repare na ordem: DOTDOT antes de DOT
# ---------------------------------------------------
t_DOTDOT     = r'\.\.'
t_DOT        = r'\.'
t_PLUS       = r'\+'
t_MINUS      = r'-'
t_TIMES      = r'\*'
t_DIVIDE     = r'/'
t_EQUAL      = r'='
t_NE         = r'<>'
t_LE         = r'<='
t_LT         = r'<'
t_GE         = r'>='
t_GT         = r'>'
t_ASSIGN     = r':='
t_LPAREN     = r'\('
t_RPAREN     = r'\)'
t_LBRACKET   = r'\['
t_RBRACKET   = r'\]'
t_COLON      = r':'
t_SEMICOLON  = r';'
t_COMMA      = r','
# (t_DOT e t_DOTDOT já definidos acima)

# ---------------------------------------------------
# 6) Comentários e espaços brancos
# ---------------------------------------------------
t_ignore = ' \t\r'

def t_COMMENT(t):
    r'\{[^}]*\}|\(\*([^*]|\*+[^*)])*\*+\)'
    # Ignora comentários { ... } ou (* ... *), sem suporte a aninhamento mais profundo
    pass

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"[LEX ERROR] Caractere ilegal '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.skip(1)

# Constrói o lexer com case-insensitive
lexer = lex.lex(reflags=re.IGNORECASE)

def build_lexer():
    return lexer