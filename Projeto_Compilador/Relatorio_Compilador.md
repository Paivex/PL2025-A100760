# Relatório Técnico — Compilador Pascal para EWVM

## Índice

1. [Introdução](#introdução)  
2. [Análise e Especificação da Linguagem Pascal](#análise-e-especificação-da-linguagem-pascal)  
   2.1. Expressões Aritméticas e Booleanas  
   2.2. Expressões Condicionais  
   2.3. Strings e Literais  
   2.4. Operações de Input/Output  
   2.5. Manobras na Stack da EWVM  
3. [Desempenho do Compilador](#desempenho-do-compilador)  
   3.1. Arquitetura do Compilador  
   3.2. Gramática Independente de Contexto (GIC)  
   3.3. Analisador Léxico  
   3.4. Analisador Sintático  
   3.5. Análise Semântica  
   3.6. Gestão de Erros  
4. [Implementação](#implementação)  
   4.1. Decisões de Projeto  
   4.2. Limitações Atuais  
   4.3. Melhorias Futuras  

---

## 1. Introdução

O presente relatório descreve o desenvolvimento de um compilador para a linguagem **Pascal Standard**, cuja saída é o código intermédio para a máquina virtual **EWVM**, fornecida como ferramenta de execução. O projeto visa consolidar conhecimentos em análise léxica, sintática e semântica, bem como geração de código e modelação de uma arquitetura de compilador.

---

## 2. Análise e Especificação da Linguagem Pascal

### 2.1. Expressões Aritméticas e Booleanas

O compilador suporta expressões com operadores aritméticos (`+`, `-`, `*`, `/`, `div`, `mod`) e operadores relacionais/lógicos (`=`, `<>`, `<`, `<=`, `>`, `>=`, `and`, `or`). A precedência é cuidadosamente definida no parser para garantir a correta construção do AST (árvore sintática abstrata).

### 2.2. Expressões Condicionais

São suportadas instruções `if ... then ... else` e ciclos `while ... do`, ambos compilados com base em saltos condicionais (instruções `JZ`, `JUMP`) para etiquetas geradas dinamicamente.

### 2.3. Strings e Literais

Strings são reconhecidas entre aspas simples e convertidas para o formato da EWVM com o opcode `PUSHS`. Literais booleanos (`true` e `false`) são convertidos para inteiros (`1` ou `0`), sendo tratados como inteiros na stack.

### 2.4. Operações de Input/Output

Instruções como `readln` e `write/writeln` são processadas com os opcodes `READ`, `WRITEI`, `WRITEF`, `WRITES`, conforme o tipo da expressão. Há conversão de tipos usando `ATOI` ou `ATOF` conforme necessário.

### 2.5. Manobras na Stack da EWVM

Cada expressão é compilada com as instruções da stack machine:
- `PUSHI`, `PUSHF`, `PUSHS`, `PUSHG` — empilamento de valores ou variáveis.
- `STOREG` — gravação de valores na memória global.
- `ADD`, `SUB`, `MUL`, `DIV`, `MOD`, `AND`, `OR`, etc. — operações sobre operandos no topo da pilha.
- `JUMP`, `JZ` — controlo de fluxo.

---

## 3. Desempenho do Compilador

### 3.1. Arquitetura do Compilador

O compilador segue a arquitetura tradicional de 4 fases:
1. **Análise Léxica** com PLY (lex)
2. **Análise Sintática** com PLY (yacc)
3. **Construção da AST**
4. **Geração de Código Intermédio (EWVM)**

### 3.2. Gramática Independente de Contexto (GIC)

A Gramática Independente de Contexto (GIC) adotada para este compilador visa dar suporte a uma sub-linguagem de Pascal com funcionalidades essenciais, mantendo simplicidade na análise sintática e viabilidade de tradução direta para a EWVM.

A gramática pode ser representada na forma GIC = <T, N, S, P>, onde:

- T é o conjunto de terminais (tokens reconhecidos pelo lexer);
- N é o conjunto de não-terminais (construções sintáticas);
- S é o símbolo inicial (`programa`);
- P é o conjunto de produções.

Exemplo de produções principais:

```
programa - PROGRAM ID SEMICOLON bloco DOT
```
Esta produção define o ponto de entrada do programa Pascal. A palavra-chave `PROGRAM` seguida de um identificador e um bloco entre `BEGIN` e `END` estabelece a estrutura mínima válida.

```
bloco - VAR declaracoes BEGIN instrucoes END
      | BEGIN instrucoes END
```
O bloco principal pode ou não conter uma secção de declaração de variáveis (`VAR ...`). Ambas as formas são suportadas, permitindo flexibilidade nos testes.

```
declaracao - lista_ids COLON tipo SEMICOLON
```
As variáveis são declaradas com lista de identificadores, seguidos por dois pontos e um tipo (como `INTEGER`, `REAL`, etc.). Esta produção alimenta a `tabela_variaveis` e associa cada variável a um índice global.

```
statement - atribuicao
          | leitura
          | escrita
          | if_then_else
          | if_then
          | while_loop
          | bloco_instr
```
Esta produção define os diferentes tipos de instruções que o compilador reconhece. Cada uma tem regras próprias para construção de AST e geração de código intermediário.

```
expressao - expressao operador_binario expressao
          | LPAREN expressao RPAREN
          | ID
          | NUMBER
          | STRING_LITERAL
          | TRUE
          | FALSE
```
A expressão é o elemento mais recorrente do compilador, usada em condições, atribuições e chamadas `write`. Suporta agrupamento com parêntesis e operadores binários como `+`, `-`, `*`, `div`, `and`, `or`, entre outros.

A utilização de regras com recursão à esquerda (por exemplo, na `statement_list` e `expressao`) foi planeada para facilitar a criação da árvore sintática em profundidade, sem ambiguidade para o parser `ply.yacc`.

Além disso, a precedência e associatividade de operadores foram definidas no topo do parser com a diretiva `precedence`, garantindo que expressões como `3 + 5 * 2` são avaliadas corretamente.

Esta GIC foi desenhada para equilibrar expressividade com simplicidade, cobrindo a maioria das construções essenciais da linguagem Pascal esperadas no contexto académico.

### 3.3. Analisador Léxico

Baseado em `ply.lex`, reconhece tokens reservados, identificadores, números, strings, operadores, e ignora comentários e espaços. Utiliza `re.IGNORECASE`.

### 3.4. Analisador Sintático

Implementado com `ply.yacc`, define precedência entre operadores e gera a árvore sintática abstrata que alimenta a geração de código.

### 3.5. Análise Semântica

Durante a análise sintática, são verificados tipos, declaração de variáveis e coerência no uso de identificadores, com registo numa tabela global.

### 3.6. Gestão de Erros

O analisador léxico e sintático reporta erros com mensagens claras e linha do erro. Programas malformados são ignorados sem comprometer os restantes.

---

## 4. Implementação

### 4.1. Decisões de Projeto

- Uso de dicionário `tabela_variaveis` para registar variáveis e os seus índices.
- Geração de etiquetas `Lx` para controlo de fluxo.
- Geração de código diretamente a partir do AST.

### 4.2. Limitações Atuais

- `for`, `procedure` e `function` ainda não estão implementados.
- Falta verificação de tipos entre expressões e variáveis.
- Arrays não têm geração de código.
- Sem otimizações.

### 4.3. Melhorias Futuras

- Implementar `for`, `procedure`, `function`.
- Verificação estática de tipos.
- Geração de código para arrays.
- Otimizações de código intermediário.

### 4.4 Testes e Resultados

Mostram-se de seguida, testes realizados, em que introduzimos linguagem Pascal no nosso programa, e os respetivos resultados obtidos (instruções para EWVM).

- Expressões Aritmétricas:

```program SomaSimples;

var
    a, b, resultado: integer;

begin
    readln(a);
    readln(b);
    resultado := a + b;
    writeln('Resultado: ', resultado);
end.
```

```
a: 0:
b: 0:
resultado: 0:

START:
READ
ATOI
STOREG 0
READ
ATOI
STOREG 1
PUSHG 0
PUSHG 1
ADD
STOREG 2
PUSHS "Resultado: "
WRITES
PUSHG 2
WRITEI
WRITELN
STOP
```
- Maior3

```
program Maior3;

var
    num1, num2, num3, maior: Integer;
begin
    Write('Introduza o primeiro número: ');
    ReadLn(num1);

    Write('Introduza o segundo número: ');
    ReadLn(num2);

    Write('Introduza o terceiro número: ');
    ReadLn(num3);

    if num1 > num2 then
        if num1 > num3 then maior := num1
        else maior := num3
    else
        if num2 > num3 then maior := num2
        else maior := num3;

    WriteLn('O maior é: ', maior)
end.
```
```
num1: 0:
num2: 0:
num3: 0:
maior: 0:

START:
PUSHS "Introduza o primeiro número: "
WRITES
READ
ATOI
STOREG 0
PUSHS "Introduza o segundo número: "
WRITES
READ
ATOI
STOREG 1
PUSHS "Introduza o terceiro número: "
WRITES
READ
ATOI
STOREG 2
PUSHG 0
PUSHG 1
SUP
JZ L0
PUSHG 0
PUSHG 2
SUP
JZ L2
PUSHG 0
STOREG 3
JUMP L3
L2:
PUSHG 2
STOREG 3
L3:
JUMP L1
L0:
PUSHG 1
PUSHG 2
SUP
JZ L4
PUSHG 1
STOREG 3
JUMP L5
L4:
PUSHG 2
STOREG 3
L5:
L1:
PUSHS "O maior é: "
WRITES
PUSHG 3
WRITEI
WRITELN
STOP
```

- Número Primo

```
program NumeroPrimo;

var
  num, i: integer;
  primo: boolean;

begin
  writeln('Introduza um número inteiro positivo:');
  readln(num);

  primo := true;
  i := 2;

  while (i <= (num div 2)) and primo do
  begin
    if (num mod i) = 0 then
      primo := false;
    i := i + 1;
  end;

  if primo then
    writeln(num, ' é um número primo')
  else
    writeln(num, ' não é um número primo')
end.
```
```
num: 0:
i: 0:
primo: 0:

START:
PUSHS "Introduza um número inteiro positivo:"
WRITES
WRITELN
READ
ATOI
STOREG 0
PUSHI 1
STOREG 2
PUSHI 2
STOREG 1
L0:
PUSHG 1
PUSHG 0
PUSHI 2
DIV
INFEQ
PUSHG 2
AND
JZ L1
PUSHG 0
PUSHG 1
MOD
PUSHI 0
EQUAL
JZ L2
PUSHI 0
STOREG 2
JUMP L3
L2:
L3:
PUSHG 1
PUSHI 1
ADD
STOREG 1
JUMP L0
L1:
PUSHG 2
JZ L4
PUSHG 0
WRITEI
PUSHS " é um número primo"
WRITES
WRITELN
JUMP L5
L4:
PUSHG 0
WRITEI
PUSHS " não é um número primo"
WRITES
WRITELN
L5:
STOP
```
## Conclusão

O desenvolvimento deste compilador para a linguagem Pascal standard permitiu consolidar conhecimentos fundamentais sobre o processo de compilação, abrangendo desde a análise léxica e sintática até à geração de código para uma máquina virtual baseada em stack (EWVM).  

Através da implementação com recurso à biblioteca PLY, foi possível construir um analisador léxico robusto, capaz de identificar as principais construções da linguagem, bem como um parser orientado por uma gramática independente de contexto desenhada especificamente para suportar os principais blocos estruturais do Pascal, como variáveis, expressões aritméticas, controlo de fluxo e operações de entrada/saída.

A utilização de uma árvore sintática abstrata (AST) como estrutura intermédia revelou-se eficaz para separar a análise da geração de código, contribuindo para uma organização modular e extensível do compilador. A geração de código, por sua vez, foi feita de forma dirigida pela sintaxe, com regras específicas para cada tipo de instrução e com tradução direta para os opcodes da EWVM.

Apesar de algumas funcionalidades opcionais não terem sido ainda implementadas, como `for`, `function` e `procedure`, a arquitetura modular do compilador permite uma expansão futura com relativa facilidade. A deteção e tratamento de erros foram também incorporados de forma básica, permitindo a continuação da análise mesmo na presença de falhas locais.

Em suma, este projeto não só evidenciou a aplicabilidade dos conceitos teóricos de compiladores, como também reforçou competências práticas de análise de linguagens, definição de gramáticas e programação estruturada em Python. O resultado final cumpre os objetivos propostos, mostrando-se funcional e alinhado com os requisitos da máquina virtual alvo.

---