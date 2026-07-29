"""Repositório de acesso a dados de Autor (RF06/RF07/RF09/RF14/RF15)."""

from typing import List

from models.autor import Autor
from repository.base_repository import BaseRepository
from utils.constantes import CAMINHO_AUTORES

FIELDNAMES = ["id", "nome", "nacionalidade", "biografia"]


class AutorRepository(BaseRepository[Autor]):
    def __init__(self):
        super().__init__(CAMINHO_AUTORES, Autor, FIELDNAMES)

    def buscar_por_nome(self, termo: str) -> List[Autor]:
        termo = termo.lower()
        return [a for a in self.listar_todos() if termo in a.nome.lower()]
