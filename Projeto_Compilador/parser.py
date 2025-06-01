from lexer import tokens, build_lexer
import ply.yacc as yacc
import sys, re

# ---------------------------------------------------
# Precedência de operadores
# ---------------------------------------------------
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQUAL', 'NE', 'LT', 'LE', 'GT', 'GE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'DIV', 'MOD'),
)

# ---------------------------------------------------
# Estruturas AST e tabelas auxiliares
# ---------------------------------------------------

codigo_meio = []          # lista de linhas (strings) do .ewvm que vamos gerar
tabela_variaveis = {}     # dicionário: nome_variável → (tipo, índice_global)
contador_etiquetas = 0    # para gerar L0, L1, L2, …
next_global_index = 0     # para atribuir índices a variáveis globais

# ---------------------------------------------------
# Funções auxiliares de geração de código (EWVM)
# ---------------------------------------------------

def nova_etiqueta():
    """
    Retorna um novo rótulo Lx (sem espaços antes), 
    e incrementa o contador interno.
    """
    global contador_etiquetas
    etiqueta = f"L{contador_etiquetas}"
    contador_etiquetas += 1
    return etiqueta

def generate_expr_code(expr):
    """
    Gera instruções EWVM para avaliar 'expr' e deixar o valor no topo da pilha.
    Em cada caso, usamos exatamente os opcodes da documentação:
      - Para inteiro literal: PUSHI <n>
      - Para real literal:    PUSHF <x>
      - Para string literal:  PUSHS "texto"
      - Para variável (id):   PUSHG <índice>
      - Para boolean literal: PUSHI 1 (True) ou PUSHI 0 (False)
      - Para binop: empilha esquerda, empilha direita, emite opcode aritmético/booleano
    """
    tp = expr[0]

    if tp == 'num':
        # Literais inteiros
        val = expr[1]
        codigo_meio.append(f"PUSHI {val}")

    elif tp == 'real':
        # Literais reais (caso seu lexer retorne floats)
        val = expr[1]
        codigo_meio.append(f"PUSHF {val}")

    elif tp == 'str':
        # Literais de string → PUSHS "texto"
        texto = expr[1].replace('"', '\\"')
        codigo_meio.append(f'PUSHS "{texto}"')

    elif tp == 'bool':
        # Booleano → mapeamos True → 1, False → 0
        if expr[1]:
            codigo_meio.append("PUSHI 1")
        else:
            codigo_meio.append("PUSHI 0")

    elif tp == 'id':
        # Variável global: empilha o valor via PUSHG <índice>
        nome_var = expr[1]
        tipo_var, idx = tabela_variaveis[nome_var]
        codigo_meio.append(f"PUSHG {idx}")

    elif tp == 'binop':
        # Operação binária: ('binop', operador, esquerdo, direito)
        op    = expr[1].lower()
        e_esq = expr[2]
        e_dir = expr[3]

        # 1) Empilha recursivamente o valor de e_esq
        generate_expr_code(e_esq)
        # 2) Empilha recursivamente o valor de e_dir
        generate_expr_code(e_dir)

        # 3) Emite o opcode correto
        if op == '+':
            codigo_meio.append("ADD")
        elif op == '-':
            codigo_meio.append("SUB")
        elif op == '*':
            codigo_meio.append("MUL")
        elif op == '/':
            codigo_meio.append("DIV")
        elif op == 'div':
            codigo_meio.append("DIV")
        elif op == 'mod':
            codigo_meio.append("MOD")
        elif op == '=':
            codigo_meio.append("EQUAL")
        elif op == '<>':
            # “<>” → EQUAL + NOT
            codigo_meio.append("EQUAL")
            codigo_meio.append("NOT")
        elif op == '<':
            codigo_meio.append("INF")
        elif op == '<=':
            codigo_meio.append("INFEQ")
        elif op == '>':
            codigo_meio.append("SUP")
        elif op == '>=':
            codigo_meio.append("SUPEQ")
        elif op == 'and':
            codigo_meio.append("AND")
        elif op == 'or':
            codigo_meio.append("OR")
        else:
            raise ValueError(f"Operador desconhecido no codegen: {op}")

    else:
        raise ValueError(f"Tipo de expressão inesperado em generate_expr_code: {tp}")

def generate_stmt_code(stmt):
    """
    Gera instruções EWVM para o nó de statement 'stmt', sem espaços à esquerda.
    Cada tipo de stmt mapeia para as instruções exatas da sua VM.
    """
    tp = stmt[0]

    if tp == 'assign':
        # ('assign', var, expr)
        var  = stmt[1]
        expr = stmt[2]

        # 1) Empilha o valor de 'expr'
        generate_expr_code(expr)

        # 2) Grava em 'var' usando STOREG <índice>
        tipo_var, idx = tabela_variaveis[var]
        codigo_meio.append(f"STOREG {idx}")

    elif tp == 'read':
        # ('read', var)
        var = stmt[1]
        tipo_var, idx = tabela_variaveis[var]

        # 1) Lê string do teclado
        codigo_meio.append("READ")

        # 2) Converte conforme tipo
        if tipo_var == 'integer':
            codigo_meio.append("ATOI")
        elif tipo_var == 'real':
            codigo_meio.append("ATOF")
        elif tipo_var == 'boolean':
            codigo_meio.append("ATOI")
        # se for 'string', não converte

        # 3) Grava em var → STOREG <índice>
        codigo_meio.append(f"STOREG {idx}")

    elif tp == 'write':
        # ('write', [expressions], newline_flag)
        lista_expr = stmt[1]
        newline    = stmt[2]

        for e in lista_expr:
            # 1) empilha o valor de 'e'
            generate_expr_code(e)

            # 2) escolhe o opcode de impressão:
            if e[0] == 'num' or e[0] == 'bool':
                codigo_meio.append("WRITEI")
            elif e[0] == 'real':
                codigo_meio.append("WRITEF")
            elif e[0] == 'str':
                codigo_meio.append("WRITES")
            elif e[0] == 'id':
                nome_var = e[1]
                tipo_v, _ = tabela_variaveis[nome_var]
                if tipo_v in ('integer', 'boolean'):
                    codigo_meio.append("WRITEI")
                elif tipo_v == 'real':
                    codigo_meio.append("WRITEF")
                elif tipo_v == 'string':
                    codigo_meio.append("WRITES")
                else:
                    codigo_meio.append("WRITEI")
            else:
                # Se for binop, infere tipo do resultado
                def infer_tipo(no):
                    if no[0] == 'binop':
                        opb = no[1].lower()
                        if opb in ['=', '<>', '<', '<=', '>', '>=', 'and', 'or']:
                            return 'boolean'
                        t1 = infer_tipo(no[2]) if no[2][0] == 'binop' else no[2][0]
                        t2 = infer_tipo(no[3]) if no[3][0] == 'binop' else no[3][0]
                        if t1 == 'real' or t2 == 'real':
                            return 'real'
                        return 'integer'
                    return no[0]

                tipo_res = infer_tipo(e)
                if tipo_res == 'real':
                    codigo_meio.append("WRITEF")
                else:
                    codigo_meio.append("WRITEI")

        if newline:
            codigo_meio.append("WRITELN")

    elif tp == 'if':
        # ('if', cond, then_stmt, else_stmt)
        cond   = stmt[1]
        then_s = stmt[2]
        else_s = stmt[3]

        etiqueta_else = nova_etiqueta()
        etiqueta_fim  = nova_etiqueta()

        # 1) Empilha condição
        generate_expr_code(cond)
        # 2) Se zero, JZ → vai para etiqueta_else
        codigo_meio.append(f"JZ {etiqueta_else}")
        # 3) Gera THEN
        generate_stmt_code(then_s)
        # 4) Pula para fim
        codigo_meio.append(f"JUMP {etiqueta_fim}")
        # 5) Rótulo ELSE
        codigo_meio.append(f"{etiqueta_else}:")
        if else_s is not None:
            generate_stmt_code(else_s)
        # 6) Rótulo FIM
        codigo_meio.append(f"{etiqueta_fim}:")

    elif tp == 'while':
        # ('while', cond, corpo_stmt)
        cond  = stmt[1]
        corpo = stmt[2]

        etiqueta_inicio = nova_etiqueta()
        etiqueta_saida  = nova_etiqueta()

        # 1) Rótulo início
        codigo_meio.append(f"{etiqueta_inicio}:")
        # 2) Empilha condição
        generate_expr_code(cond)
        # 3) Se falso, pula para etiqueta_saida
        codigo_meio.append(f"JZ {etiqueta_saida}")
        # 4) Gera corpo
        generate_stmt_code(corpo)
        # 5) Pula de volta para início
        codigo_meio.append(f"JUMP {etiqueta_inicio}")
        # 6) Rótulo saída
        codigo_meio.append(f"{etiqueta_saida}:")

    elif tp == 'for':
        # stmt = ('for', var, expr_inicio, expr_limite, corpo_stmt, direction)
        var_nome     = stmt[1]
        expr_inicio  = stmt[2]
        expr_limite  = stmt[3]
        corpo        = stmt[4]
        direction    = stmt[5]  # 'to' ou 'downto'

        # 1) Atribui à variável de controle o valor inicial
        generate_expr_code(expr_inicio)
        tipo_var, idx = tabela_variaveis[var_nome]
        codigo_meio.append(f"STOREG {idx}")  # var := expr_inicio

        # 2) Cria etiquetas para início e saída do loop
        etiqueta_inicio = nova_etiqueta()
        etiqueta_saida  = nova_etiqueta()

        # 3) Rótulo de início
        codigo_meio.append(f"{etiqueta_inicio}:")

        # 4) Carrega a variável de controle e compara com o limite
        #    Para 'to': empilha var e limite, usa INFEQ para i <= limite
        #    Para 'downto': usa SUPEQ para i >= limite
        codigo_meio.append(f"PUSHG {idx}")
        generate_expr_code(expr_limite)
        if direction == 'to':
            codigo_meio.append("INFEQ")
        else:  # 'downto'
            codigo_meio.append("SUPEQ")
        # Se comparação for zero, significa condição falhou → sai do loop
        codigo_meio.append(f"JZ {etiqueta_saida}")

        # 5) Gera o corpo do loop
        generate_stmt_code(corpo)

        # 6) Incrementa ou decrementa a variável de controle
        codigo_meio.append(f"PUSHG {idx}")    # empilha var atual
        codigo_meio.append("PUSHI 1")         # empilha constante 1
        if direction == 'to':
            codigo_meio.append("ADD")         # var + 1
        else:
            codigo_meio.append("SUB")         # var - 1
        codigo_meio.append(f"STOREG {idx}")   # armazena de volta em var

        # 7) Pula de volta para o início
        codigo_meio.append(f"JUMP {etiqueta_inicio}")

        # 8) Rótulo de saída
        codigo_meio.append(f"{etiqueta_saida}:")

    elif tp == 'block':
        # ('block', [lista_de_statements])
        for s in stmt[1]:
            generate_stmt_code(s)

    else:
        raise ValueError(f"Tipo de statement inesperado em generate_stmt_code: {tp}")

def generate_code(ast_program):
    """
    Recebe ast_program = ('program', nome, bloco_stmt)
    1) Declara todas as variáveis em tabela_variaveis (já povoada por p_declaracao)
       gerando "nome: 0" na ordem dos índices.
    2) Em seguida, insere uma linha em branco e o rótulo START:.
    3) Por fim, gera o bloco de statements e acrescenta STOP.
    """
    nome_prog = ast_program[1]
    bloco     = ast_program[2]

    # 1) Declaração de variáveis (cada var com “nome: 0”):
    for var, (tipo, idx) in tabela_variaveis.items():
        codigo_meio.append(f"{var}: 0:")

    # 2) Linha em branco para separar dados do código:
    codigo_meio.append("")

    # 3) Começo do código:
    codigo_meio.append("START:")
    generate_stmt_code(bloco)

    # 4) Fim com STOP:
    codigo_meio.append("STOP")


# ---------------------------------------------------
# Gramática (PLY) — constrói o AST
# ---------------------------------------------------

def p_programa(p):
    'programa : PROGRAM ID SEMICOLON bloco DOT'
    p[0] = ('program', p[2], p[4])

def p_bloco_com_var(p):
    'bloco : VAR declaracoes BEGIN instrucoes END'
    p[0] = ('block', p[4])

def p_bloco_sem_var(p):
    'bloco : BEGIN instrucoes END'
    p[0] = ('block', p[2])

def p_declaracoes(p):
    '''declaracoes : declaracoes declaracao
                   | declaracao
                   | empty'''
    if len(p) == 2:
        if p[1] is None:
            p[0] = []
        else:
            p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_declaracao(p):
    'declaracao : lista_ids COLON tipo SEMICOLON'
    """
    Aqui, cada nome em p[1] recebe:
       tabela_variaveis[nome] = (tipo, índice_global_atual)
    e incrementamos next_global_index para a próxima.
    """
    global next_global_index
    tipo = p[3]
    for nome in p[1]:
        tabela_variaveis[nome] = (tipo, next_global_index)
        next_global_index += 1
    p[0] = ('decl', p[1], tipo)

def p_lista_ids(p):
    '''lista_ids : ID
                 | lista_ids COMMA ID'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_tipo_primitivo(p):
    '''tipo : INTEGER
            | BOOLEAN
            | STRING
            | REAL'''
    p[0] = p[1].lower()

def p_tipo_array(p):
    'tipo : ARRAY LBRACKET NUMBER DOTDOT NUMBER RBRACKET OF tipo'
    p[0] = 'array'

def p_instrucoes(p):
    'instrucoes : statement_list'
    p[0] = p[1]

def p_statement_list_multi(p):
    'statement_list : statement_list SEMICOLON statement'
    p[0] = p[1] + [p[3]]

def p_statement_list_trail(p):
    'statement_list : statement_list SEMICOLON'
    p[0] = p[1]

def p_statement_list_single(p):
    'statement_list : statement'
    p[0] = [p[1]]

def p_statement(p):
    '''statement : atribuicao_instr_only
                 | leitura_stmt
                 | escrita_stmt
                 | if_then_else
                 | if_then
                 | while_stmt
                 | for_stmt
                 | bloco_instr'''
    p[0] = p[1]

def p_atribuicao_instr_only(p):
    'atribuicao_instr_only : ID ASSIGN expressao'
    p[0] = ('assign', p[1], p[3])

def p_leitura_stmt(p):
    'leitura_stmt : READLN LPAREN ID RPAREN'
    p[0] = ('read', p[3])

def p_escrita_stmt_writeln(p):
    'escrita_stmt : WRITELN LPAREN exp_list RPAREN'
    p[0] = ('write', p[3], True)

def p_escrita_stmt_write(p):
    'escrita_stmt : WRITE LPAREN exp_list RPAREN'
    p[0] = ('write', p[3], False)

def p_exp_list(p):
    '''exp_list : expressao
                | exp_list COMMA expressao'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_if_then_else(p):
    'if_then_else : IF expressao THEN statement ELSE statement'
    cond      = p[2]
    then_stmt = p[4]
    else_stmt = p[6]
    p[0] = ('if', cond, then_stmt, else_stmt)

def p_if_then(p):
    'if_then : IF expressao THEN statement'
    cond      = p[2]
    then_stmt = p[4]
    p[0] = ('if', cond, then_stmt, None)

def p_while_stmt(p):
    'while_stmt : WHILE expressao DO statement'
    cond  = p[2]
    corpo = p[4]
    p[0] = ('while', cond, corpo)

def p_for_stmt(p):
    '''for_stmt : FOR ID ASSIGN expressao TO expressao DO statement
                | FOR ID ASSIGN expressao DOWNTO expressao DO statement'''
    """
    Construímos um nó AST do tipo ('for', var, expr_inicial, expr_limite, corpo, direction)
      direction = 'to' ou 'downto'
    """
    var_nome      = p[2]
    expr_inicio   = p[4]
    expr_limite   = p[6]
    corpo_stmt    = p[8]
    direction_key = p[5].lower()  # 'to' ou 'downto'
    p[0] = ('for', var_nome, expr_inicio, expr_limite, corpo_stmt, direction_key)

def p_bloco_instr(p):
    'bloco_instr : BEGIN instrucoes END'
    p[0] = ('block', p[2])

# ---------------- EXPRESSÕES ----------------

def p_expressao_binaria(p):
    '''expressao : expressao PLUS expressao
                 | expressao MINUS expressao
                 | expressao TIMES expressao
                 | expressao DIVIDE expressao
                 | expressao DIV expressao
                 | expressao MOD expressao
                 | expressao EQUAL expressao
                 | expressao NE expressao
                 | expressao LT expressao
                 | expressao LE expressao
                 | expressao GT expressao
                 | expressao GE expressao
                 | expressao AND expressao
                 | expressao OR expressao'''
    left  = p[1]
    op    = p[2]
    right = p[3]
    p[0] = ('binop', op, left, right)

def p_expressao_grupo(p):
    'expressao : LPAREN expressao RPAREN'
    p[0] = p[2]

def p_expressao_id(p):
    'expressao : ID'
    p[0] = ('id', p[1])

def p_expressao_num(p):
    'expressao : NUMBER'
    p[0] = ('num', p[1])

def p_expressao_str(p):
    'expressao : STRING_LITERAL'
    p[0] = ('str', p[1])

def p_expressao_true(p):
    'expressao : TRUE'
    p[0] = ('bool', True)

def p_expressao_false(p):
    'expressao : FALSE'
    p[0] = ('bool', False)

def p_empty(p):
    'empty :'
    p[0] = None

def p_error(p):
    if p:
        raise SyntaxError(f"Token inesperado {p.value!r} (linha {p.lineno})")
    else:
        raise SyntaxError("Fim de arquivo inesperado")

parser = yacc.yacc(debug=True)

# ---------------------------------------------------
# Driver principal: separa cada “program … end.” em input.txt e gera .ewvm
# ---------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python parser.py <input.txt>")
        sys.exit(1)

    arquivo_entrada = sys.argv[1]
    with open(arquivo_entrada, 'r', encoding='utf-8') as f:
        data = f.read()

    # Regex para isolar cada trecho “program Nome; … end.” (case-insensitive)
    padrao = re.compile(
        r'(?i)program\s+([A-Za-z_][A-Za-z0-9_]*)\s*;.*?end\.',
        re.IGNORECASE | re.DOTALL
    )
    matches = list(padrao.finditer(data))
    if not matches:
        print("Nenhum programa Pascal encontrado em input.txt")
        sys.exit(1)

    for m in matches:
        trecho    = m.group(0)
        nome_prog = m.group(1)

        # Limpa tudo antes de compilar cada programa
        codigo_meio.clear()
        tabela_variaveis.clear()
        contador_etiquetas = 0
        next_global_index = 0

        lexer = build_lexer()
        try:
            ast_prog = parser.parse(trecho, lexer=lexer)
        except SyntaxError as e:
            print(f"[ERRO DE SINTAXE em '{nome_prog}'] {e}")
            continue

        # Gera as instruções EWVM (Data + Code)
        generate_code(ast_prog)

        # Escreve no arquivo <nome_prog>.ewvm
        nome_saida = f"{nome_prog}.ewvm"
        with open(nome_saida, 'w', encoding='utf-8') as fout:
            for linha in codigo_meio:
                fout.write(linha + "\n")

        print(f"Gerado → {nome_saida}")