"""Repositório de acesso a dados de Emprestimo (RF20-RF27)."""

from typing import List

from models.emprestimo import Emprestimo
from repository.base_repository import BaseRepository
from utils.constantes import CAMINHO_EMPRESTIMOS

FIELDNAMES = [
    "id",
    "usuario_id",
    "livro_id",
    "exemplar_id",
    "data_emprestimo",
    "data_prevista_devolucao",
    "data_devolucao",
    "renovacoes",
    "multa",
    "status",
]


class EmprestimoRepository(BaseRepository[Emprestimo]):
    def __init__(self):
        super().__init__(CAMINHO_EMPRESTIMOS, Emprestimo, FIELDNAMES)

    def buscar_por_usuario(self, usuario_id: str) -> List[Emprestimo]:
        return [e for e in self.listar_todos() if e.usuario_id == usuario_id]

    def buscar_ativos_por_usuario(self, usuario_id: str) -> List[Emprestimo]:
        return [e for e in self.buscar_por_usuario(usuario_id) if e.esta_ativo()]

    def buscar_por_livro(self, livro_id: str) -> List[Emprestimo]:
        return [e for e in self.listar_todos() if e.livro_id == livro_id]

    def buscar_ativos(self) -> List[Emprestimo]:
        return [e for e in self.listar_todos() if e.esta_ativo()]
