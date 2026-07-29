"""Model que representa uma categoria (gênero) de livro."""

from dataclasses import dataclass


@dataclass
class Categoria:
    id: str
    nome: str
    descricao: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Categoria":
        return cls(
            id=data["id"],
            nome=data["nome"],
            descricao=data.get("descricao", ""),
        )

    def __str__(self) -> str:
        return f"[{self.id}] {self.nome}"
