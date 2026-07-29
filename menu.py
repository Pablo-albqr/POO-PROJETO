"""
Interface de linha de comando (CLI) do Sistema para Bibliotecas.

Este módulo é responsável apenas pela interação com o usuário
(entrada/saída via terminal). Toda a lógica de negócio fica nas
camadas de service, mantendo a separação de responsabilidades.
"""

from models.funcionario import Funcionario
from services.autenticacao_service import AutenticacaoService
from services.autor_service import AutorService
from services.categoria_service import CategoriaService
from services.emprestimo_service import EmprestimoService
from services.livro_service import LivroService
from services.usuario_service import UsuarioService


class Menu:
    def __init__(self):
        self.autenticacao_service = AutenticacaoService()
        self.usuario_service = UsuarioService()
        self.autor_service = AutorService()
        self.categoria_service = CategoriaService()
        self.livro_service = LivroService()
        self.emprestimo_service = EmprestimoService(usuario_service=self.usuario_service)

        self.funcionario_logado: Funcionario | None = None
        self._garantir_funcionario_padrao()

    # ------------------------------------------------------------------
    # Bootstrap / login
    # ------------------------------------------------------------------
    def _garantir_funcionario_padrao(self) -> None:
        """Cria um administrador padrão na primeira execução (admin/admin123)."""
        if not self.autenticacao_service.funcionario_repository.listar_todos():
            self.autenticacao_service.cadastrar_funcionario(
                nome="Administrador",
                login="admin",
                senha="admin123",
                nivel_acesso="administrador",
            )

    def _tela_login(self) -> bool:
        print("\n=== LOGIN ===")
        login = input("Login: ").strip()
        senha = input("Senha: ").strip()
        funcionario = self.autenticacao_service.autenticar(login, senha)
        if funcionario is None:
            print(">> Login ou senha inválidos.")
            return False
        self.funcionario_logado = funcionario
        print(f">> Bem-vindo(a), {funcionario.nome} ({funcionario.nivel_acesso})!")
        return True

    # ------------------------------------------------------------------
    # Loop principal
    # ------------------------------------------------------------------
    def executar(self) -> None:
        print("=== SISTEMA PARA BIBLIOTECAS ===")
        print("(usuário padrão: admin / senha: admin123)")

        tentativas = 0
        while self.funcionario_logado is None:
            if self._tela_login():
                break
            tentativas += 1
            if tentativas >= 3:
                print(">> Número de tentativas excedido. Encerrando o sistema.")
                return

        while True:
            self._exibir_menu_principal()
            opcao = input("Escolha uma opção: ").strip()

            if opcao == "1":
                self._menu_usuarios()
            elif opcao == "2":
                self._menu_acervo()
            elif opcao == "3":
                self._menu_emprestimos()
            elif opcao == "4":
                self._menu_relatorios()
            elif opcao == "0":
                print("Até logo!")
                break
            else:
                print(">> Opção inválida.")

    def _exibir_menu_principal(self) -> None:
        print("\n===== MENU PRINCIPAL =====")
        print("1 - Gestão de Usuários")
        print("2 - Gestão do Acervo (livros, autores, categorias)")
        print("3 - Empréstimos, Devoluções e Renovações")
        print("4 - Relatórios")
        print("0 - Sair")

    # ------------------------------------------------------------------
    # 1. Usuários (RF01-RF05)
    # ------------------------------------------------------------------
    def _menu_usuarios(self) -> None:
        while True:
            print("\n--- GESTÃO DE USUÁRIOS ---")
            print("1 - Cadastrar usuário")
            print("2 - Consultar usuários")
            print("3 - Atualizar usuário")
            print("4 - Excluir usuário")
            print("0 - Voltar")
            opcao = input("Escolha uma opção: ").strip()

            if opcao == "1":
                self._cadastrar_usuario()
            elif opcao == "2":
                self._consultar_usuarios()
            elif opcao == "3":
                self._atualizar_usuario()
            elif opcao == "4":
                self._excluir_usuario()
            elif opcao == "0":
                break
            else:
                print(">> Opção inválida.")

    def _cadastrar_usuario(self) -> None:
        try:
            nome = input("Nome: ").strip()
            email = input("E-mail: ").strip()
            telefone = input("Telefone (opcional): ").strip()
            usuario = self.usuario_service.cadastrar_usuario(nome, email, telefone)
            print(f">> Usuário cadastrado com sucesso: {usuario}")
        except ValueError as erro:
            print(f">> Erro: {erro}")

    def _consultar_usuarios(self) -> None:
        usuarios = self.usuario_service.consultar_usuarios()
        if not usuarios:
            print(">> Nenhum usuário cadastrado.")
        for usuario in usuarios:
            print(f"  {usuario}")

    def _atualizar_usuario(self) -> None:
        usuario_id = input("ID do usuário: ").strip()
        print("(deixe em branco para não alterar um campo)")
        nome = input("Novo nome: ").strip() or None
        email = input("Novo e-mail: ").strip() or None
        telefone = input("Novo telefone: ").strip() or None
        try:
            usuario = self.usuario_service.atualizar_usuario(usuario_id, nome, email, telefone)
            print(f">> Usuário atualizado: {usuario}")
        except ValueError as erro:
            print(f">> Erro: {erro}")

    def _excluir_usuario(self) -> None:
        usuario_id = input("ID do usuário: ").strip()
        try:
            autorizado = self.autenticacao_service.verificar_autorizacao(self.funcionario_logado)
            if self.usuario_service.excluir_usuario(usuario_id, funcionario_autorizado=autorizado):
                print(">> Usuário excluído com sucesso.")
            else:
                print(">> Usuário não encontrado.")
        except (ValueError, PermissionError) as erro:
            print(f">> Erro: {erro}")

    # ------------------------------------------------------------------
    # 2. Acervo: autores, categorias e livros
    # ------------------------------------------------------------------
    def _menu_acervo(self) -> None:
        while True:
            print("\n--- GESTÃO DO ACERVO ---")
            print("1 - Autores")
            print("2 - Categorias")
            print("3 - Livros")
            print("4 - Pesquisar livros")
            print("0 - Voltar")
            opcao = input("Escolha uma opção: ").strip()

            if opcao == "1":
                self._menu_autores()
            elif opcao == "2":
                self._menu_categorias()
            elif opcao == "3":
                self._menu_livros()
            elif opcao == "4":
                self._menu_pesquisa_livros()
            elif opcao == "0":
                break
            else:
                print(">> Opção inválida.")

    # -- Autores (RF06/RF07/RF09/RF14/RF15) -----------------------------
    def _menu_autores(self) -> None:
        while True:
            print("\n-- AUTORES --")
            print("1 - Cadastrar autor")
            print("2 - Consultar autores")
            print("3 - Atualizar autor")
            print("4 - Remover autor")
            print("0 - Voltar")
            opcao = input("Escolha uma opção: ").strip()

            if opcao == "1":
                try:
                    nome = input("Nome do autor: ").strip()
                    nacionalidade = input("Nacionalidade (opcional): ").strip()
                    biografia = input("Biografia (opcional): ").strip()
                    autor = self.autor_service.cadastrar_autor(nome, nacionalidade, biografia)
                    print(f">> Autor cadastrado: {autor}")
                except ValueError as erro:
                    print(f">> Erro: {erro}")
            elif opcao == "2":
                autores = self.autor_service.consultar_autores()
                if not autores:
                    print(">> Nenhum autor cadastrado.")
                for autor in autores:
                    print(f"  {autor}")
            elif opcao == "3":
                autor_id = input("ID do autor: ").strip()
                nome = input("Novo nome (branco p/ manter): ").strip() or None
                nacionalidade = input("Nova nacionalidade (branco p/ manter): ").strip() or None
                try:
                    autor = self.autor_service.atualizar_autor(autor_id, nome, nacionalidade)
                    print(f">> Autor atualizado: {autor}")
                except ValueError as erro:
                    print(f">> Erro: {erro}")
            elif opcao == "4":
                autor_id = input("ID do autor: ").strip()
                try:
                    if self.autor_service.excluir_autor(autor_id):
                        print(">> Autor removido com sucesso.")
                    else:
                        print(">> Autor não encontrado.")
                except ValueError as erro:
                    print(f">> Erro: {erro}")
            elif opcao == "0":
                break
            else:
                print(">> Opção inválida.")

    # -- Categorias (RF10/RF11) ------------------------------------------
    def _menu_categorias(self) -> None:
        while True:
            print("\n-- CATEGORIAS --")
            print("1 - Cadastrar categoria")
            print("2 - Consultar categorias")
            print("3 - Remover categoria")
            print("0 - Voltar")
            opcao = input("Escolha uma opção: ").strip()

            if opcao == "1":
                try:
                    nome = input("Nome da categoria: ").strip()
                    descricao = input("Descrição (opcional): ").strip()
                    categoria = self.categoria_service.cadastrar_categoria(nome, descricao)
                    print(f">> Categoria cadastrada: {categoria}")
                except ValueError as erro:
                    print(f">> Erro: {erro}")
            elif opcao == "2":
                categorias = self.categoria_service.consultar_categorias()
                if not categorias:
                    print(">> Nenhuma categoria cadastrada.")
                for categoria in categorias:
                    print(f"  {categoria}")
            elif opcao == "3":
                categoria_id = input("ID da categoria: ").strip()
                try:
                    if self.categoria_service.excluir_categoria(categoria_id):
                        print(">> Categoria removida com sucesso.")
                    else:
                        print(">> Categoria não encontrada.")
                except ValueError as erro:
                    print(f">> Erro: {erro}")
            elif opcao == "0":
                break
            else:
                print(">> Opção inválida.")

    # -- Livros (RF06/RF08/RF12/RF13) -------------------------------------
    def _menu_livros(self) -> None:
        while True:
            print("\n-- LIVROS --")
            print("1 - Cadastrar livro")
            print("2 - Consultar livros")
            print("3 - Atualizar livro")
            print("4 - Remover livro")
            print("5 - Adicionar exemplares")
            print("0 - Voltar")
            opcao = input("Escolha uma opção: ").strip()

            if opcao == "1":
                self._cadastrar_livro()
            elif opcao == "2":
                self._listar_livros(self.livro_service.consultar_livros())
            elif opcao == "3":
                self._atualizar_livro()
            elif opcao == "4":
                livro_id = input("ID do livro: ").strip()
                try:
                    if self.livro_service.excluir_livro(livro_id):
                        print(">> Livro removido com sucesso.")
                    else:
                        print(">> Livro não encontrado.")
                except ValueError as erro:
                    print(f">> Erro: {erro}")
            elif opcao == "5":
                livro_id = input("ID do livro: ").strip()
                try:
                    quantidade = int(input("Quantidade de exemplares a adicionar: ").strip())
                    livro = self.livro_service.adicionar_exemplares(livro_id, quantidade)
                    print(f">> Exemplares adicionados. {livro}")
                except (ValueError, TypeError) as erro:
                    print(f">> Erro: {erro}")
            elif opcao == "0":
                break
            else:
                print(">> Opção inválida.")

    def _cadastrar_livro(self) -> None:
        try:
            titulo = input("Título: ").strip()
            autor_id = input("ID do autor: ").strip()
            categoria_id = input("ID da categoria: ").strip()
            ano_publicacao = input("Ano de publicação (opcional): ").strip()
            isbn = input("ISBN (opcional): ").strip()
            quantidade = input("Quantidade de exemplares [1]: ").strip()
            quantidade = int(quantidade) if quantidade else 1

            livro = self.livro_service.cadastrar_livro(
                titulo, autor_id, categoria_id, ano_publicacao, isbn, quantidade
            )
            print(f">> Livro cadastrado: {livro}")
        except ValueError as erro:
            print(f">> Erro: {erro}")

    def _atualizar_livro(self) -> None:
        livro_id = input("ID do livro: ").strip()
        print("(deixe em branco para não alterar um campo)")
        titulo = input("Novo título: ").strip() or None
        autor_id = input("Novo ID de autor: ").strip() or None
        categoria_id = input("Novo ID de categoria: ").strip() or None
        try:
            livro = self.livro_service.atualizar_livro(livro_id, titulo, autor_id, categoria_id)
            print(f">> Livro atualizado: {livro}")
        except ValueError as erro:
            print(f">> Erro: {erro}")

    def _listar_livros(self, livros) -> None:
        if not livros:
            print(">> Nenhum livro encontrado.")
        for livro in livros:
            print(f"  {livro}")

    # -- Pesquisa (RF16-RF19) ---------------------------------------------
    def _menu_pesquisa_livros(self) -> None:
        print("\n-- PESQUISAR LIVROS --")
        print("1 - Por título")
        print("2 - Por autor (ID)")
        print("3 - Por categoria (ID)")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            termo = input("Título (ou parte dele): ").strip()
            self._listar_livros(self.livro_service.pesquisar_por_titulo(termo))
        elif opcao == "2":
            autor_id = input("ID do autor: ").strip()
            self._listar_livros(self.livro_service.pesquisar_por_autor(autor_id))
        elif opcao == "3":
            categoria_id = input("ID da categoria: ").strip()
            self._listar_livros(self.livro_service.pesquisar_por_categoria(categoria_id))
        else:
            print(">> Opção inválida.")

    # ------------------------------------------------------------------
    # 3. Empréstimos / Devoluções / Renovações
    # ------------------------------------------------------------------
    def _menu_emprestimos(self) -> None:
        while True:
            print("\n--- EMPRÉSTIMOS / DEVOLUÇÕES / RENOVAÇÕES ---")
            print("1 - Registrar empréstimo")
            print("2 - Registrar devolução")
            print("3 - Renovar empréstimo")
            print("0 - Voltar")
            opcao = input("Escolha uma opção: ").strip()

            if opcao == "1":
                try:
                    usuario_id = input("ID do usuário: ").strip()
                    livro_id = input("ID do livro: ").strip()
                    emprestimo = self.emprestimo_service.registrar_emprestimo(usuario_id, livro_id)
                    print(f">> Empréstimo registrado: {emprestimo}")
                except ValueError as erro:
                    print(f">> Erro: {erro}")
            elif opcao == "2":
                try:
                    emprestimo_id = input("ID do empréstimo: ").strip()
                    emprestimo = self.emprestimo_service.registrar_devolucao(emprestimo_id)
                    if emprestimo.multa > 0:
                        print(f">> Devolução registrada com atraso. Multa: R$ {emprestimo.multa:.2f}")
                    else:
                        print(">> Devolução registrada com sucesso.")
                except ValueError as erro:
                    print(f">> Erro: {erro}")
            elif opcao == "3":
                try:
                    emprestimo_id = input("ID do empréstimo: ").strip()
                    emprestimo = self.emprestimo_service.renovar_emprestimo(emprestimo_id)
                    print(f">> Empréstimo renovado. Nova devolução: {emprestimo.data_prevista_devolucao}")
                except ValueError as erro:
                    print(f">> Erro: {erro}")
            elif opcao == "0":
                break
            else:
                print(">> Opção inválida.")

    # ------------------------------------------------------------------
    # 4. Relatórios (RF28-RF31)
    # ------------------------------------------------------------------
    def _menu_relatorios(self) -> None:
        while True:
            print("\n--- RELATÓRIOS ---")
            print("1 - Livros emprestados")
            print("2 - Livros atrasados")
            print("3 - Usuários com pendências")
            print("4 - Estatísticas do acervo")
            print("0 - Voltar")
            opcao = input("Escolha uma opção: ").strip()

            if opcao == "1":
                for emprestimo in self.emprestimo_service.relatorio_emprestados():
                    print(f"  {emprestimo}")
            elif opcao == "2":
                for emprestimo in self.emprestimo_service.relatorio_atrasados():
                    print(f"  {emprestimo}")
            elif opcao == "3":
                for usuario in self.usuario_service.listar_usuarios_com_pendencias():
                    print(f"  {usuario}")
            elif opcao == "4":
                estatisticas = self.livro_service.estatisticas_acervo()
                for chave, valor in estatisticas.items():
                    print(f"  {chave}: {valor}")
            elif opcao == "0":
                break
            else:
                print(">> Opção inválida.")
