"""
Model que representa um funcionário do sistema (quem opera a
biblioteca). Suporta autenticação (RF32) e níveis de acesso (RF33).
"""

from dataclasses import dataclass

from utils.constantes import NIVEL_BIBLIOTECARIO


@dataclass
class Funcionario:
    id: str
    nome: str
    login: str
    senha_hash: str
    nivel_acesso: str = NIVEL_BIBLIOTECARIO

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "login": self.login,
            "senha_hash": self.senha_hash,
            "nivel_acesso": self.nivel_acesso,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Funcionario":
        return cls(
            id=data["id"],
            nome=data["nome"],
            login=data["login"],
            senha_hash=data["senha_hash"],
            nivel_acesso=data.get("nivel_acesso", NIVEL_BIBLIOTECARIO),
        )

    def eh_administrador(self) -> bool:
        return self.nivel_acesso == "administrador"

    def __str__(self) -> str:
        return f"[{self.id}] {self.nome} ({self.nivel_acesso})"
