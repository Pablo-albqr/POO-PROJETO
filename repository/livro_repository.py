"""Repositório de acesso a dados de Livro (RF06/RF08/RF12/RF13, RF16-RF19)."""

from typing import List

from models.livro import Livro
from repository.base_repository import BaseRepository
from utils.constantes import CAMINHO_LIVROS

FIELDNAMES = ["id", "titulo", "autor_id", "categoria_id", "ano_publicacao", "isbn", "exemplares"]


class LivroRepository(BaseRepository[Livro]):
    def __init__(self):
        super().__init__(CAMINHO_LIVROS, Livro, FIELDNAMES)

    def buscar_por_titulo(self, termo: str) -> List[Livro]:
        termo = termo.lower()
        return [l for l in self.listar_todos() if termo in l.titulo.lower()]

    def buscar_por_autor(self, autor_id: str) -> List[Livro]:
        return [l for l in self.listar_todos() if l.autor_id == autor_id]

    def buscar_por_categoria(self, categoria_id: str) -> List[Livro]:
        return [l for l in self.listar_todos() if l.categoria_id == categoria_id]
