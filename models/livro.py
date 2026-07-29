"""
Model que representa um livro do acervo.

Cada livro pode possuir vários exemplares físicos (RF13). Cada
exemplar possui uma identificação única (RN03) e só pode estar
em um dos dois estados: disponível ou emprestado (RN04).
"""

from dataclasses import dataclass, field
from typing import List

from utils.constantes import STATUS_EXEMPLAR_DISPONIVEL, STATUS_EXEMPLAR_EMPRESTADO


@dataclass
class Exemplar:
    id: str
    status: str = STATUS_EXEMPLAR_DISPONIVEL

    def esta_disponivel(self) -> bool:
        return self.status == STATUS_EXEMPLAR_DISPONIVEL

    def marcar_emprestado(self) -> None:
        self.status = STATUS_EXEMPLAR_EMPRESTADO

    def marcar_disponivel(self) -> None:
        self.status = STATUS_EXEMPLAR_DISPONIVEL


@dataclass
class Livro:
    id: str
    titulo: str
    autor_id: str
    categoria_id: str
    ano_publicacao: str = ""
    isbn: str = ""
    exemplares: List[Exemplar] = field(default_factory=list)

    # -- persistência -------------------------------------------------
    def to_dict(self) -> dict:
        exemplares_str = ";".join(f"{e.id}:{e.status}" for e in self.exemplares)
        return {
            "id": self.id,
            "titulo": self.titulo,
            "autor_id": self.autor_id,
            "categoria_id": self.categoria_id,
            "ano_publicacao": self.ano_publicacao,
            "isbn": self.isbn,
            "exemplares": exemplares_str,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Livro":
        exemplares: List[Exemplar] = []
        bruto = data.get("exemplares", "")
        if bruto:
            for item in bruto.split(";"):
                if not item:
                    continue
                exemplar_id, status = item.split(":")
                exemplares.append(Exemplar(id=exemplar_id, status=status))
        return cls(
            id=data["id"],
            titulo=data["titulo"],
            autor_id=data.get("autor_id", ""),
            categoria_id=data.get("categoria_id", ""),
            ano_publicacao=data.get("ano_publicacao", ""),
            isbn=data.get("isbn", ""),
            exemplares=exemplares,
        )

    # -- regras de domínio ---------------------------------------------
    def quantidade_total(self) -> int:
        return len(self.exemplares)

    def quantidade_disponivel(self) -> int:
        return sum(1 for e in self.exemplares if e.esta_disponivel())

    def esta_disponivel(self) -> bool:
        return self.quantidade_disponivel() > 0

    def obter_exemplar_disponivel(self) -> Exemplar | None:
        for exemplar in self.exemplares:
            if exemplar.esta_disponivel():
                return exemplar
        return None

    def obter_exemplar(self, exemplar_id: str) -> Exemplar | None:
        for exemplar in self.exemplares:
            if exemplar.id == exemplar_id:
                return exemplar
        return None

    def __str__(self) -> str:
        return (
            f"[{self.id}] {self.titulo} - "
            f"{self.quantidade_disponivel()}/{self.quantidade_total()} disponíveis"
        )
