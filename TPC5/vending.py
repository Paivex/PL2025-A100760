import json

# Nome do ficheiro onde o stock é guardado
STOCK_FILE = "stock.json"

# Função para carregar o stock do ficheiro JSON
def carregar_stock():
    try:
        with open(STOCK_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Função para guardar o stock no ficheiro JSON
def guardar_stock(stock):
    with open(STOCK_FILE, "w") as f:
        json.dump(stock, f, indent=4)

# Função para listar os produtos disponíveis
def listar_produtos(stock):
    print("cod    |  nome      |  quantidade  |  preço")
    print("---------------------------------")
    for produto in stock:
        print(f"{produto['cod']} | {produto['nome']} | {produto['quant']} | {produto['preco']}€")

# Função para converter moedas inseridas em cêntimos
def processar_moedas(moedas):
    valores = {"1E": 100, "50C": 50, "20C": 20, "10C": 10, "5C": 5, "2C": 2, "1C": 1}
    saldo = 0
    for moeda in moedas:
        moeda = moeda.upper()
        if moeda in valores:
            saldo += valores[moeda]
        else:
            print(f"maq: Moeda desconhecida '{moeda}', ignorada.")
    return saldo

# Função para calcular o troco
def calcular_troco(saldo):
    valores = [100, 50, 20, 10, 5, 2, 1]
    nomes = ["1e", "50c", "20c", "10c", "5c", "2c", "1c"]
    troco = []
    for i, valor in enumerate(valores):
        if saldo >= valor:
            quantidade = saldo // valor
            saldo %= valor
            troco.append(f"{quantidade}x {nomes[i]}")
    return ", ".join(troco)

# Função para adicionar um novo produto ao stock
def adicionar_produto(stock):
    cod = input("Código do produto: ").strip().upper()
    nome = input("Nome do produto: ").strip()
    quant = int(input("Quantidade: ").strip())
    preco = float(input("Preço (€): ").strip())
    
    produto_existente = next((p for p in stock if p["cod"] == cod), None)
    if produto_existente:
        produto_existente["quant"] += quant
        print(f"maq: Produto '{produto_existente['nome']}' atualizado. Nova quantidade: {produto_existente['quant']}")
    else:
        stock.append({"cod": cod, "nome": nome, "quant": quant, "preco": preco})
        print(f"maq: Produto '{nome}' adicionado com sucesso.")
    guardar_stock(stock)

# Função principal
def maquina_vending():
    stock = carregar_stock()
    saldo = 0
    
    print("maq: Stock carregado, Estado atualizado.")
    print("maq: Bom dia. Estou disponível para atender o seu pedido.")
    
    while True:
        comando = input(">> ").strip().upper()
        
        if comando == "LISTAR":
            listar_produtos(stock)
        
        elif comando.startswith("MOEDA"):
            moedas = comando[6:].replace(" ", "").split(",")
            saldo += processar_moedas(moedas)
            print(f"maq: Saldo = {saldo // 100}e{saldo % 100}c")
        
        elif comando.startswith("SELECIONAR"):
            cod = comando.split()[1]
            produto = next((p for p in stock if p["cod"] == cod), None)
            
            if not produto:
                print("maq: Produto inexistente.")
            elif produto["quant"] == 0:
                print("maq: Produto esgotado.")
            elif saldo < int(produto["preco"] * 100):
                print(f"maq: Saldo insuficiente para satisfazer o seu pedido")
                print(f"maq: Saldo = {saldo // 100}e{saldo % 100}c; Pedido = {int(produto['preco'] * 100) // 100}e{int(produto['preco'] * 100) % 100}c")
            else:
                saldo -= int(produto["preco"] * 100)
                produto["quant"] -= 1
                print(f"maq: Pode retirar o produto dispensado \"{produto['nome']}\"")
                print(f"maq: Saldo = {saldo // 100}e{saldo % 100}c")
        
        elif comando == "ADICIONAR":
            adicionar_produto(stock)
        
        elif comando == "SAIR":
            if saldo > 0:
                print(f"maq: Pode retirar o troco: {calcular_troco(saldo)}.")
            print("maq: Até à próxima")
            guardar_stock(stock)
            break

if __name__ == "__main__":
    maquina_vending()
