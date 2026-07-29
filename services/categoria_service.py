"""Regras de negócio relacionadas à Gestão de Categorias."""

from typing import List, Optional

from models.categoria import Categoria
from repository.categoria_repository import CategoriaRepository
from repository.livro_repository import LivroRepository
from utils.ids import gerar_id
from utils.validacoes import validar_nao_vazio


class CategoriaService:
    def __init__(
        self,
        categoria_repository: Optional[CategoriaRepository] = None,
        livro_repository: Optional[LivroRepository] = None,
    ):
        self.categoria_repository = categoria_repository or CategoriaRepository()
        self.livro_repository = livro_repository or LivroRepository()

    # RF10 - cadastro -------------------------------------------------
    def cadastrar_categoria(self, nome: str, descricao: str = "") -> Categoria:
        if not validar_nao_vazio(nome):
            raise ValueError("O nome da categoria é obrigatório.")
        categoria = Categoria(id=gerar_id("CAT"), nome=nome.strip(), descricao=descricao.strip())
        return self.categoria_repository.salvar(categoria)

    # RF11 - consulta -----------------------------------------------
    def consultar_categorias(self) -> List[Categoria]:
        return self.categoria_repository.listar_todos()

    def buscar_categoria_por_id(self, categoria_id: str) -> Optional[Categoria]:
        return self.categoria_repository.buscar_por_id(categoria_id)

    def atualizar_categoria(
        self, categoria_id: str, nome: Optional[str] = None, descricao: Optional[str] = None
    ) -> Categoria:
        categoria = self.categoria_repository.buscar_por_id(categoria_id)
        if categoria is None:
            raise ValueError("Categoria não encontrada.")
        if nome is not None:
            if not validar_nao_vazio(nome):
                raise ValueError("O nome da categoria é obrigatório.")
            categoria.nome = nome.strip()
        if descricao is not None:
            categoria.descricao = descricao.strip()
        self.categoria_repository.atualizar(categoria)
        return categoria

    # RF10 - remoção ---------------------------------------------------
    def excluir_categoria(self, categoria_id: str) -> bool:
        if self.livro_repository.buscar_por_categoria(categoria_id):
            raise ValueError("Não é possível remover uma categoria que possui livros cadastrados.")
        return self.categoria_repository.excluir(categoria_id)
