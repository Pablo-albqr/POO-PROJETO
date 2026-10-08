"""Menus de terminal que compartilham os serviços e os dados em CSV."""
from getpass import getpass
from interface.contexto import Contexto


class Terminal:
    def __init__(self, contexto=None):
        self.ctx = contexto if contexto is not None else Contexto()

    def executar(self):
        print("\nSISTEMA PARA BIBLIOTECAS")
        self.ctx.funcionario_logado = None
        tentativas = 0
        while self.ctx.funcionario_logado is None:
            print("\n1 - Entrar\n2 - Criar usuário\n0 - Sair")
            opcao = input("Opção: ").strip()
            if opcao == "0":
                return
            if opcao == "2":
                self.criar_conta()
                continue
            if opcao != "1":
                print("Opção inválida.")
                continue
            login = input("Login: ").strip()
            try:
                funcionario = self.ctx.autenticacao.autenticar(login, getpass("Senha: "))
            except OSError as erro:
                print(f"Não foi possível ler as contas: {erro}")
                continue
            if funcionario is None:
                tentativas += 1
                print("Login ou senha inválidos.")
                if tentativas >= 3:
                    print("Número de tentativas excedido. Sistema encerrado.")
                    return
            else:
                self.ctx.funcionario_logado = funcionario
        funcionario = self.ctx.funcionario_logado
        print(f"\nBem-vindo(a), {funcionario.nome}!")
        entidades = list(self.ctx.entidades.values())
        while True:
            print("\nMENU PRINCIPAL")
            for numero, entidade in enumerate(entidades, 1):
                print(f"{numero} - {entidade.titulo}")
            print("0 - Sair")
            opcao = input("Opção: ").strip()
            if opcao == "0":
                print("Sistema encerrado.")
                return
            if opcao not in [str(i) for i in range(1, len(entidades) + 1)]:
                print("Opção inválida.")
                continue
            self.menu_entidade(entidades[int(opcao) - 1])

    def criar_conta(self):
        print("\nCRIAR USUÁRIO (digite /cancelar para voltar)")
        nome = input("Nome: ").strip()
        if nome == "/cancelar":
            return
        login = input("Escolha seu login: ").strip()
        if login == "/cancelar":
            return
        senha = getpass("Crie sua senha: ")
        if senha == "/cancelar":
            return
        confirmacao = getpass("Confirme a senha: ")
        if confirmacao == "/cancelar":
            return
        if senha != confirmacao:
            print("As senhas não coincidem. Cadastro não realizado.")
            return
        try:
            self.ctx.autenticacao.criar_conta(nome, login, senha)
        except (ValueError, OSError) as erro:
            print(f"Não foi possível criar o usuário: {erro}")
            return
        print("Usuário criado! Login salvo. Escolha Entrar para acessar sua conta.")

    def listar(self, entidade, termo=""):
        itens = []
        for item in entidade.listar():
            valores = entidade.linha(item)
            if termo and not any(termo.casefold() in str(v).casefold() for v in valores):
                continue
            itens.append(item)
            print(f"\n[{len(itens)}]")
            for (rotulo, _), valor in zip(entidade.colunas, valores):
                print(f"  {rotulo}: {valor}")
        print(f"\n{len(itens)} registro(s).")
        return itens

    def selecionar(self, entidade):
        itens = self.listar(entidade)
        if not itens:
            return None
        while True:
            opcao = input("Número do registro (0 para cancelar): ").strip()
            if opcao == "0":
                return None
            if opcao.isdecimal() and 1 <= int(opcao) <= len(itens):
                return itens[int(opcao) - 1]
            print("Número inválido.")

    def formulario(self, entidade, item=None):
        edicao = item is not None
        atuais = entidade.valores_edicao(item) if edicao else {}
        valores = {}
        print("\nDigite /cancelar para cancelar.")
        if edicao:
            print("Enter mantém o valor atual; /limpar apaga um campo opcional.")
        for campo in entidade.campos:
            if (campo.so_cadastro and edicao) or (campo.so_edicao and not edicao):
                continue
            padrao = str(atuais.get(campo.chave, campo.padrao))
            opcoes = campo.opcoes() if campo.tipo == "combo" and campo.opcoes else []
            if campo.tipo == "combo":
                if not opcoes:
                    print(f"Cadastre primeiro uma opção para {campo.rotulo}.")
                    return None
                print(f"\n{campo.rotulo}:")
                for numero, opcao in enumerate(opcoes, 1):
                    print(f"{numero} - {opcao}")
            while True:
                dica = f" [{padrao}]" if padrao else ""
                texto = input(f"{campo.rotulo}{dica}: ").strip()
                if texto == "/cancelar":
                    return None
                if texto == "/limpar":
                    texto = ""
                elif not texto:
                    texto = padrao
                elif campo.tipo == "combo":
                    if texto.isdecimal() and 1 <= int(texto) <= len(opcoes):
                        texto = opcoes[int(texto) - 1]
                    else:
                        print("Escolha o número de uma das opções.")
                        continue
                if campo.obrigatorio and not texto:
                    print("Este campo é obrigatório.")
                    continue
                if campo.tipo == "inteiro" and texto and not texto.isdecimal():
                    print("Informe um número inteiro igual ou maior que zero.")
                    continue
                if campo.chave == "exemplares" and texto and int(texto) < 1:
                    print("Informe pelo menos um exemplar.")
                    continue
                valores[campo.chave] = texto
                break
        return valores

    def menu_entidade(self, entidade):
        while True:
            print(f"\n{entidade.titulo.upper()}")
            print("1 - Listar\n2 - Buscar\n3 - Cadastrar\n4 - Editar\n5 - Excluir\n0 - Voltar")
            opcao = input("Opção: ").strip()
            try:
                if opcao == "0":
                    return
                if opcao == "1":
                    self.listar(entidade)
                elif opcao == "2":
                    self.listar(entidade, input("Buscar: ").strip())
                elif opcao == "3":
                    valores = self.formulario(entidade)
                    if valores is not None:
                        entidade.criar(valores)
                        print("Cadastro realizado com sucesso.")
                elif opcao == "4":
                    item = self.selecionar(entidade)
                    if item is not None:
                        valores = self.formulario(entidade, item)
                        if valores is not None:
                            entidade.atualizar(item.id, valores)
                            print("Registro atualizado com sucesso.")
                elif opcao == "5":
                    item = self.selecionar(entidade)
                    if item is not None and input("Confirmar exclusão? (s/N): ").strip().lower() == "s":
                        excluido = entidade.excluir(item.id)
                        print("Registro excluído." if excluido else "Registro não encontrado.")
                else:
                    print("Opção inválida.")
            except (ValueError, PermissionError, OSError) as erro:
                print(f"Erro: {erro}")
