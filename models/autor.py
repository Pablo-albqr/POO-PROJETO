"""Model que representa um autor cadastrado no acervo."""

from dataclasses import dataclass


@dataclass
class Autor:
    id: str
    nome: str
    nacionalidade: str = ""
    biografia: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "nacionalidade": self.nacionalidade,
            "biografia": self.biografia,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Autor":
        return cls(
            id=data["id"],
            nome=data["nome"],
            nacionalidade=data.get("nacionalidade", ""),
            biografia=data.get("biografia", ""),
        )

    def __str__(self) -> str:
        return f"[{self.id}] {self.nome} ({self.nacionalidade})"
