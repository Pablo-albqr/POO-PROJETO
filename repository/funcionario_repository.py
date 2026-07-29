"""Repositório de acesso a dados de Funcionario (RF32/RF33)."""

from typing import Optional

from models.funcionario import Funcionario
from repository.base_repository import BaseRepository
from utils.constantes import CAMINHO_FUNCIONARIOS

FIELDNAMES = ["id", "nome", "login", "senha_hash", "nivel_acesso"]


class FuncionarioRepository(BaseRepository[Funcionario]):
    def __init__(self):
        super().__init__(CAMINHO_FUNCIONARIOS, Funcionario, FIELDNAMES)

    def buscar_por_login(self, login: str) -> Optional[Funcionario]:
        for funcionario in self.listar_todos():
            if funcionario.login.lower() == login.lower():
                return funcionario
        return None
