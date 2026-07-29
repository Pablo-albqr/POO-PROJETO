"""Repositório de acesso a dados de Usuario (RF01-RF05)."""

from typing import List, Optional

from models.usuario import Usuario
from repository.base_repository import BaseRepository
from utils.constantes import CAMINHO_USUARIOS

FIELDNAMES = ["id", "nome", "email", "telefone", "ativo", "pendencias"]


class UsuarioRepository(BaseRepository[Usuario]):
    def __init__(self):
        super().__init__(CAMINHO_USUARIOS, Usuario, FIELDNAMES)

    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        for usuario in self.listar_todos():
            if usuario.email.lower() == email.lower():
                return usuario
        return None

    def buscar_por_nome(self, termo: str) -> List[Usuario]:
        termo = termo.lower()
        return [u for u in self.listar_todos() if termo in u.nome.lower()]
