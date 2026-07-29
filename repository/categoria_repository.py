"""Repositório de acesso a dados de Categoria (RF10/RF11)."""

from typing import List

from models.categoria import Categoria
from repository.base_repository import BaseRepository
from utils.constantes import CAMINHO_CATEGORIAS

FIELDNAMES = ["id", "nome", "descricao"]


class CategoriaRepository(BaseRepository[Categoria]):
    def __init__(self):
        super().__init__(CAMINHO_CATEGORIAS, Categoria, FIELDNAMES)

    def buscar_por_nome(self, termo: str) -> List[Categoria]:
        termo = termo.lower()
        return [c for c in self.listar_todos() if termo in c.nome.lower()]
