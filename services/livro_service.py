"""
Regras de negócio relacionadas à Gestão do Acervo (livros) e à
Consulta e Pesquisa (RF16-RF19).
"""

from typing import List, Optional

from models.livro import Exemplar, Livro
from repository.autor_repository import AutorRepository
from repository.categoria_repository import CategoriaRepository
from repository.emprestimo_repository import EmprestimoRepository
from repository.livro_repository import LivroRepository
from utils.ids import gerar_id
from utils.validacoes import validar_ano, validar_nao_vazio


class LivroService:
    def __init__(
        self,
        livro_repository: Optional[LivroRepository] = None,
        autor_repository: Optional[AutorRepository] = None,
        categoria_repository: Optional[CategoriaRepository] = None,
        emprestimo_repository: Optional[EmprestimoRepository] = None,
    ):
        self.livro_repository = livro_repository or LivroRepository()
        self.autor_repository = autor_repository or AutorRepository()
        self.categoria_repository = categoria_repository or CategoriaRepository()
        self.emprestimo_repository = emprestimo_repository or EmprestimoRepository()

    # RF06 - cadastro de livros -----------------------------------------
    def cadastrar_livro(
        self,
        titulo: str,
        autor_id: str,
        categoria_id: str,
        ano_publicacao: str = "",
        isbn: str = "",
        quantidade_exemplares: int = 1,
    ) -> Livro:
        if not validar_nao_vazio(titulo):
            raise ValueError("O título do livro é obrigatório.")
        if not self.autor_repository.existe(autor_id):
            raise ValueError("Autor não encontrado.")
        if not self.categoria_repository.existe(categoria_id):
            raise ValueError("Categoria não encontrada.")
        if ano_publicacao and not validar_ano(ano_publicacao):
            raise ValueError("Ano de publicação inválido.")
        if quantidade_exemplares < 1:
            raise ValueError("É necessário cadastrar ao menos um exemplar.")

        exemplares = [Exemplar(id=gerar_id("EXP")) for _ in range(quantidade_exemplares)]  # RN03
        livro = Livro(
            id=gerar_id("LIV"),
            titulo=titulo.strip(),
            autor_id=autor_id,
            categoria_id=categoria_id,
            ano_publicacao=ano_publicacao.strip(),
            isbn=isbn.strip(),
            exemplares=exemplares,
        )
        return self.livro_repository.salvar(livro)

    # RF13 - adicionar/remover exemplares de um livro já cadastrado ------
    def adicionar_exemplares(self, livro_id: str, quantidade: int) -> Livro:
        livro = self._obter_livro_ou_falhar(livro_id)
        if quantidade < 1:
            raise ValueError("A quantidade deve ser maior que zero.")
        livro.exemplares.extend(Exemplar(id=gerar_id("EXP")) for _ in range(quantidade))
        self.livro_repository.atualizar(livro)
        return livro

    def remover_exemplar(self, livro_id: str, exemplar_id: str) -> Livro:
        livro = self._obter_livro_ou_falhar(livro_id)
        exemplar = livro.obter_exemplar(exemplar_id)
        if exemplar is None:
            raise ValueError("Exemplar não encontrado.")
        if not exemplar.esta_disponivel():
            raise ValueError("Não é possível remover um exemplar emprestado.")
        livro.exemplares = [e for e in livro.exemplares if e.id != exemplar_id]
        self.livro_repository.atualizar(livro)
        return livro

    # RF12 - atualização --------------------------------------------------
    def atualizar_livro(
        self,
        livro_id: str,
        titulo: Optional[str] = None,
        autor_id: Optional[str] = None,
        categoria_id: Optional[str] = None,
        ano_publicacao: Optional[str] = None,
        isbn: Optional[str] = None,
    ) -> Livro:
        livro = self._obter_livro_ou_falhar(livro_id)

        if titulo is not None:
            if not validar_nao_vazio(titulo):
                raise ValueError("O título do livro é obrigatório.")
            livro.titulo = titulo.strip()
        if autor_id is not None:
            if not self.autor_repository.existe(autor_id):
                raise ValueError("Autor não encontrado.")
            livro.autor_id = autor_id
        if categoria_id is not None:
            if not self.categoria_repository.existe(categoria_id):
                raise ValueError("Categoria não encontrada.")
            livro.categoria_id = categoria_id
        if ano_publicacao is not None:
            if ano_publicacao and not validar_ano(ano_publicacao):
                raise ValueError("Ano de publicação inválido.")
            livro.ano_publicacao = ano_publicacao.strip()
        if isbn is not None:
            livro.isbn = isbn.strip()

        self.livro_repository.atualizar(livro)
        return livro

    # RF08 - remoção de livros --------------------------------------------
    def excluir_livro(self, livro_id: str) -> bool:
        if self.emprestimo_repository.buscar_por_livro(livro_id):
            ativos = [e for e in self.emprestimo_repository.buscar_por_livro(livro_id) if e.esta_ativo()]
            if ativos:
                raise ValueError("Não é possível remover um livro com empréstimos ativos.")
        return self.livro_repository.excluir(livro_id)

    # RF16-RF19 - pesquisa ---------------------------------------------------
    def pesquisar_por_titulo(self, titulo: str) -> List[Livro]:
        return self.livro_repository.buscar_por_titulo(titulo)

    def pesquisar_por_autor(self, autor_id: str) -> List[Livro]:
        return self.livro_repository.buscar_por_autor(autor_id)

    def pesquisar_por_categoria(self, categoria_id: str) -> List[Livro]:
        return self.livro_repository.buscar_por_categoria(categoria_id)

    def consultar_disponibilidade(self, livro_id: str) -> str:
        livro = self._obter_livro_ou_falhar(livro_id)
        return f"{livro.quantidade_disponivel()} de {livro.quantidade_total()} exemplar(es) disponível(is)"

    def consultar_livros(self) -> List[Livro]:
        return self.livro_repository.listar_todos()

    def buscar_livro_por_id(self, livro_id: str) -> Optional[Livro]:
        return self.livro_repository.buscar_por_id(livro_id)

    # RF31 - estatísticas de utilização do acervo ---------------------------
    def estatisticas_acervo(self) -> dict:
        livros = self.livro_repository.listar_todos()
        total_exemplares = sum(l.quantidade_total() for l in livros)
        total_disponiveis = sum(l.quantidade_disponivel() for l in livros)
        return {
            "total_titulos": len(livros),
            "total_exemplares": total_exemplares,
            "exemplares_disponiveis": total_disponiveis,
            "exemplares_emprestados": total_exemplares - total_disponiveis,
        }

    # ------------------------------------------------------------------
    def _obter_livro_ou_falhar(self, livro_id: str) -> Livro:
        livro = self.livro_repository.buscar_por_id(livro_id)
        if livro is None:
            raise ValueError("Livro não encontrado.")
        return livro
