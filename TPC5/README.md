# Máquina de Vending

Este trabalho consiste numa simulação de uma máquina de vending em Python. A máquina permite ao utilizador visualizar os produtos disponíveis, inserir moedas, comprar produtos, adicionar novos produtos ao stock e sair com o troco correto.

## Funcionalidades

- **Listar produtos**: Mostra os produtos disponíveis, quantidades e preços.
- **Inserir moedas**: Permite inserir moedas válidas e acumular saldo.
- **Selecionar produto**: O utilizador pode comprar um produto se tiver saldo suficiente.
- **Adicionar produtos**: Permite adicionar novos produtos ao stock ou atualizar a quantidade de produtos existentes.
- **Devolver troco**: Se o utilizador sair com saldo restante, o troco é calculado e exibido.
- **Persistência de dados**: O stock é guardado num ficheiro `stock.json` e atualizado automaticamente.

## Resolução

1. **Leitura e Escrita do Stock**: O stock de produtos é armazenado num ficheiro `stock.json`, permitindo que a informação persista entre execuções do programa. No arranque, os dados são carregados para uma lista em memória, e no final são guardados de volta.

2. **Interação com o Utilizador**: O programa aceita comandos do utilizador, que são interpretados e processados para simular o funcionamento da máquina de vending.

3. **Gestão do Saldo**: O saldo é armazenado como um valor em cêntimos para evitar erros de arredondamento. Sempre que um utilizador insere moedas, o valor total do saldo é atualizado corretamente.

4. **Compra de Produtos**: Quando um produto é selecionado, o programa verifica se o código existe, se há stock disponível e se o utilizador tem saldo suficiente. Se a compra for válida, o saldo é atualizado e a quantidade do produto diminui.

5. **Devolução do Troco**: Se o utilizador sair com saldo restante, o programa calcula a melhor combinação de moedas para devolver o troco de forma eficiente.

6. **Adição de Produtos**: O programa permite adicionar novos produtos ou atualizar a quantidade de produtos existentes, garantindo flexibilidade para a gestão do stock.

## Requisitos

- Python 3.x
- Ficheiro `stock.json` na mesma pasta que o script

## Como Utilizar

1. Executar o programa `vending.py`.
2. Inserir comandos conforme necessário:
   - `LISTAR` → Lista os produtos disponíveis.
   - `MOEDA 1E, 50C, 10C` → Insere moedas no saldo.
   - `SELECIONAR A23` → Compra o produto com código A23.
   - `ADICIONAR` → Permite adicionar ou atualizar produtos.
   - `SAIR` → Termina a sessão e devolve o troco.

## Exemplo de Uso

```
maq: Stock carregado, Estado atualizado.
maq: Bom dia. Estou disponível para atender o seu pedido.
>> LISTAR
cod    |  nome           |  quantidade  |  preço
---------------------------------
B12    | Coca-Cola 0.33L |  5           |  1.2€
C45    | Batatas Fritas  | 10           |  1.5€
...
>> MOEDA 2E
maq: Saldo = 2e00c
>> SELECIONAR B12
maq: Pode retirar o produto dispensado "Coca-Cola 0.33L"
maq: Saldo = 80c
>> SELECIONAR C45
maq: Saldo insuficiente para satisfazer o seu pedido
maq: Saldo = 80c; Pedido = 1e50c
>> SAIR
maq: Pode retirar o troco: 1x 50c, 1x 20c, 1x 10c.
maq: Até à próxima
```