class Parser:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_token = None
        self.next_token()

    def error(self, message):
        raise Exception(f'Erro de sintaxe: {message}')

    def next_token(self):
        text = self.text
        pos = self.pos

        # Ignorar espaços em branco
        while pos < len(text) and text[pos].isspace():
            pos += 1

        if pos >= len(text):
            self.current_token = None
            self.pos = pos
            return

        # Reconhecer números
        if text[pos].isdigit():
            start = pos
            while pos < len(text) and text[pos].isdigit():
                pos += 1
            self.current_token = ('NUMBER', int(text[start:pos]))
        # Reconhecer operadores e parênteses
        elif text[pos] in '+-*/()':
            self.current_token = ('SYMBOL', text[pos])
            pos += 1
        else:
            self.error(f'Caractere inesperado: {text[pos]}')
        
        self.pos = pos

    def match(self, expected_type, expected_value=None):
        if self.current_token is None:
            self.error(f'Esperava {expected_type}, encontrou fim da entrada')
        
        token_type, token_value = self.current_token
        
        if token_type != expected_type:
            self.error(f'Esperava {expected_type}, encontrou {token_type}')
        
        if expected_value is not None and token_value != expected_value:
            self.error(f'Esperava {expected_value}, encontrou {token_value}')
        
        result = token_value
        self.next_token()
        return result

    # expr → term expr'
    def expr(self):
        value = self.term()
        return self.expr_prime(value)

    # expr' → + term expr' | - term expr' | ε
    def expr_prime(self, left):
        if self.current_token is not None and self.current_token[0] == 'SYMBOL':
            if self.current_token[1] == '+':
                self.match('SYMBOL', '+')
                right = self.term()
                return self.expr_prime(left + right)
            elif self.current_token[1] == '-':
                self.match('SYMBOL', '-')
                right = self.term()
                return self.expr_prime(left - right)
        
        return left

    # term → factor term'
    def term(self):
        value = self.factor()
        return self.term_prime(value)

    # term' → * factor term' | / factor term' | ε
    def term_prime(self, left):
        if self.current_token is not None and self.current_token[0] == 'SYMBOL':
            if self.current_token[1] == '*':
                self.match('SYMBOL', '*')
                right = self.factor()
                return self.term_prime(left * right)
            elif self.current_token[1] == '/':
                self.match('SYMBOL', '/')
                right = self.factor()
                if right == 0:
                    self.error('Divisão por zero')
                return self.term_prime(left / right)
        
        return left

    # factor → number | ( expr )
    def factor(self):
        if self.current_token is None:
            self.error('Expressão incompleta')
        
        if self.current_token[0] == 'NUMBER':
            return self.match('NUMBER')
        elif self.current_token[0] == 'SYMBOL' and self.current_token[1] == '(':
            self.match('SYMBOL', '(')
            value = self.expr()
            self.match('SYMBOL', ')')
            return value
        else:
            self.error(f'Token inesperado: {self.current_token}')

    def parse(self):
        result = self.expr()
        if self.current_token is not None:
            self.error(f'Tokens não processados após o final da expressão: {self.current_token}')
        return result


def calculate_expression(expression):
    try:
        parser = Parser(expression)
        return parser.parse()
    except Exception as e:
        return str(e)


def main():
    print("Parser LL(1) Recursivo Descendente para Expressões Aritméticas")
    print("Digite 'sair' para encerrar o programa")
    print("-" * 50)
    
    while True:
        expression = input("Expressão: ")
        
        if expression.lower() == 'sair':
            print("Programa encerrado.")
            break
            
        result = calculate_expression(expression)
        print(f"Resultado: {result}")
        print("-" * 50)


if __name__ == "__main__":
    main()