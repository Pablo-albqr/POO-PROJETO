"""
Model que representa um usuário da biblioteca (leitor que realiza
empréstimos). Não confundir com Funcionario, que representa quem
opera o sistema (RF32/RF33).
"""

from dataclasses import dataclass


@dataclass
class Usuario:
    id: str
    nome: str
    email: str
    telefone: str = ""
    ativo: bool = True
    pendencias: bool = False  # RN02 - usuário com pendências não pode emprestar

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "telefone": self.telefone,
            "ativo": str(self.ativo),
            "pendencias": str(self.pendencias),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Usuario":
        return cls(
            id=data["id"],
            nome=data["nome"],
            email=data["email"],
            telefone=data.get("telefone", ""),
            ativo=data.get("ativo", "True") == "True",
            pendencias=data.get("pendencias", "False") == "True",
        )

    def __str__(self) -> str:
        situacao = "com pendências" if self.pendencias else "regular"
        return f"[{self.id}] {self.nome} <{self.email}> ({situacao})"
