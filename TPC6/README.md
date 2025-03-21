# Parser LL(1) Recursivo Descendente para Expressões Aritméticas

## Descrição do Problema

O objetivo deste trabalho é desenvolver um parser recursivo descendente LL(1) que possa:
1. Reconhecer expressões aritméticas válidas
2. Calcular o valor dessas expressões

As expressões aritméticas suportadas incluem:
- Números inteiros
- Operadores aritméticos básicos: `+`, `-`, `*`, `/`
- Parênteses para modificar a ordem de precedência

## Solução Implementada

### Gramática LL(1)

Para criar um parser recursivo descendente, foi necessário transformar uma gramática tradicional de expressões aritméticas em uma gramática LL(1) sem recursão à esquerda. A gramática utilizada é:

```
expr → term expr'
expr' → + term expr' | - term expr' | ε
term → factor term'
term' → * factor term' | / factor term' | ε
factor → number | ( expr )
```

Esta gramática respeita a precedência dos operadores (multiplicação/divisão têm precedência sobre adição/subtração) e elimina ambiguidades.

### Implementação

A solução foi implementada em Python através de um parser recursivo descendente preditivo que segue os princípios de um analisador LL(1). O código:

1. Realiza análise léxica, identificando tokens (números e símbolos)
2. Implementa uma função para cada não-terminal da gramática
3. Calcula os valores das expressões durante a análise sintática
4. Fornece mensagens de erro claras para expressões inválidas

## Exemplos de Utilização

Execute o script Python e digite expressões aritméticas quando solicitado:

```
$ python parser.py
Parser LL(1) Recursivo Descendente para Expressões Aritméticas
Digite 'sair' para encerrar o programa
--------------------------------------------------
Expressão: 2+3
Resultado: 5
--------------------------------------------------
Expressão: 67-(2+3*4)
Resultado: 53
--------------------------------------------------
Expressão: (9-2)*(13-4)
Resultado: 63
--------------------------------------------------
Expressão: sair
Programa encerrado.
```

## Exemplos de Expressões Suportadas

### Expressões Simples
- `2+3` = 5

### Expressões com Precedência de Operadores
- `2+3*4` = 14 (a multiplicação é calculada antes da adição)

### Expressões com Parênteses
- `(2+3)*4` = 20 (os parênteses alteram a precedência)

### Expressões Complexas
- `(10+5)*(9-7)/(3+1)` = 7.5

## Tratamento de Erros

O parser detecta e reporta vários tipos de erros:

```
Expressão: 2+
Resultado: Erro de sintaxe: Expressão incompleta

Expressão: 2+*3
Resultado: Erro de sintaxe: Esperava NUMBER, encontrou SYMBOL

Expressão: 2+3)
Resultado: Erro de sintaxe: Tokens não processados após o final da expressão: ('SYMBOL', ')')

Expressão: (2+3
Resultado: Erro de sintaxe: Esperava SYMBOL, encontrou fim da entrada

Expressão: 5/0
Resultado: Erro de sintaxe: Divisão por zero
```