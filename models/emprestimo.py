"""
Model que representa um empréstimo de um exemplar de livro a um
usuário (RF20-RF23).
"""

from dataclasses import dataclass

from utils.constantes import STATUS_EMPRESTIMO_ATIVO


@dataclass
class Emprestimo:
    id: str
    usuario_id: str
    livro_id: str
    exemplar_id: str
    data_emprestimo: str
    data_prevista_devolucao: str
    data_devolucao: str = ""
    renovacoes: int = 0
    multa: float = 0.0
    status: str = STATUS_EMPRESTIMO_ATIVO

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "livro_id": self.livro_id,
            "exemplar_id": self.exemplar_id,
            "data_emprestimo": self.data_emprestimo,
            "data_prevista_devolucao": self.data_prevista_devolucao,
            "data_devolucao": self.data_devolucao,
            "renovacoes": str(self.renovacoes),
            "multa": str(self.multa),
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Emprestimo":
        return cls(
            id=data["id"],
            usuario_id=data["usuario_id"],
            livro_id=data["livro_id"],
            exemplar_id=data["exemplar_id"],
            data_emprestimo=data["data_emprestimo"],
            data_prevista_devolucao=data["data_prevista_devolucao"],
            data_devolucao=data.get("data_devolucao", ""),
            renovacoes=int(data.get("renovacoes", 0) or 0),
            multa=float(data.get("multa", 0.0) or 0.0),
            status=data.get("status", STATUS_EMPRESTIMO_ATIVO),
        )

    def esta_ativo(self) -> bool:
        return self.status == "ativo" or self.status == "atrasado"

    def __str__(self) -> str:
        return (
            f"[{self.id}] usuário={self.usuario_id} livro={self.livro_id} "
            f"status={self.status}"
        )
