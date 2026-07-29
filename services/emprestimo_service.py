"""
Regras de negócio de Empréstimos, Devoluções e Renovações, além dos
relatórios que dependem dessas informações (RF20-RF31).
"""

from datetime import datetime, timedelta
from typing import List, Optional

from models.emprestimo import Emprestimo
from repository.emprestimo_repository import EmprestimoRepository
from repository.livro_repository import LivroRepository
from repository.usuario_repository import UsuarioRepository
from utils.constantes import (
    FORMATO_DATA,
    MAX_RENOVACOES,
    MULTA_POR_DIA_ATRASO,
    PRAZO_EMPRESTIMO_DIAS,
    STATUS_EMPRESTIMO_ATIVO,
    STATUS_EMPRESTIMO_ATRASADO,
    STATUS_EMPRESTIMO_DEVOLVIDO,
)
from utils.ids import gerar_id


class EmprestimoService:
    def __init__(
        self,
        emprestimo_repository: Optional[EmprestimoRepository] = None,
        livro_repository: Optional[LivroRepository] = None,
        usuario_repository: Optional[UsuarioRepository] = None,
        usuario_service=None,
        reservas_por_livro: Optional[dict] = None,
    ):
        self.emprestimo_repository = emprestimo_repository or EmprestimoRepository()
        self.livro_repository = livro_repository or LivroRepository()
        self.usuario_repository = usuario_repository or UsuarioRepository()

        # Importação tardia para evitar dependência circular entre services.
        if usuario_service is None:
            from services.usuario_service import UsuarioService

            usuario_service = UsuarioService(self.usuario_repository, self.emprestimo_repository)
        self.usuario_service = usuario_service

        # Estrutura simples de reservas: {livro_id: [usuario_id, ...]} usada
        # apenas para respeitar a RN07 (livro reservado por terceiros não
        # pode ser renovado).
        self.reservas_por_livro = reservas_por_livro if reservas_por_livro is not None else {}

    # RF20-RF23 - registrar empréstimo ------------------------------------
    def registrar_emprestimo(self, usuario_id: str, livro_id: str) -> Emprestimo:
        usuario = self.usuario_repository.buscar_por_id(usuario_id)
        if usuario is None:
            raise ValueError("Usuário não encontrado.")

        livro = self.livro_repository.buscar_por_id(livro_id)
        if livro is None:
            raise ValueError("Livro não encontrado.")

        if not self.usuario_service.pode_emprestar(usuario_id):  # RN01/RN02
            raise ValueError(
                "Usuário não pode realizar novos empréstimos "
                "(limite atingido ou pendências em aberto)."
            )

        exemplar = livro.obter_exemplar_disponivel()
        if exemplar is None:  # RF23
            raise ValueError("Não há exemplares disponíveis para este livro.")

        exemplar.marcar_emprestado()  # RN04
        self.livro_repository.atualizar(livro)

        hoje = datetime.now()
        data_prevista = hoje + timedelta(days=PRAZO_EMPRESTIMO_DIAS)  # RN05

        emprestimo = Emprestimo(
            id=gerar_id("EMP"),
            usuario_id=usuario_id,
            livro_id=livro_id,
            exemplar_id=exemplar.id,
            data_emprestimo=hoje.strftime(FORMATO_DATA),
            data_prevista_devolucao=data_prevista.strftime(FORMATO_DATA),
            status=STATUS_EMPRESTIMO_ATIVO,
        )
        return self.emprestimo_repository.salvar(emprestimo)

    # RF24/RF26/RF27/RN08 - devolução --------------------------------------
    def registrar_devolucao(self, emprestimo_id: str) -> Emprestimo:
        emprestimo = self._obter_emprestimo_ou_falhar(emprestimo_id)
        if emprestimo.status == STATUS_EMPRESTIMO_DEVOLVIDO:
            raise ValueError("Este empréstimo já foi devolvido.")

        hoje = datetime.now()
        emprestimo.data_devolucao = hoje.strftime(FORMATO_DATA)
        emprestimo.multa = self._calcular_multa(emprestimo, hoje)  # RF26/RN08
        emprestimo.status = STATUS_EMPRESTIMO_DEVOLVIDO

        livro = self.livro_repository.buscar_por_id(emprestimo.livro_id)
        if livro is not None:
            exemplar = livro.obter_exemplar(emprestimo.exemplar_id)
            if exemplar is not None:
                exemplar.marcar_disponivel()  # RF27/RN04
                self.livro_repository.atualizar(livro)

        if emprestimo.multa > 0:
            self.usuario_service.marcar_pendencia(emprestimo.usuario_id, True)

        self.emprestimo_repository.atualizar(emprestimo)
        return emprestimo

    # RF25/RN07 - renovação ---------------------------------------------
    def renovar_emprestimo(self, emprestimo_id: str) -> Emprestimo:
        emprestimo = self._obter_emprestimo_ou_falhar(emprestimo_id)
        if emprestimo.status == STATUS_EMPRESTIMO_DEVOLVIDO:
            raise ValueError("Não é possível renovar um empréstimo já devolvido.")
        if emprestimo.renovacoes >= MAX_RENOVACOES:
            raise ValueError("Limite de renovações atingido para este empréstimo.")

        reservas = self.reservas_por_livro.get(emprestimo.livro_id, [])
        outras_reservas = [uid for uid in reservas if uid != emprestimo.usuario_id]
        if outras_reservas:  # RN07
            raise ValueError("Este livro está reservado por outro usuário e não pode ser renovado.")

        data_atual = datetime.strptime(emprestimo.data_prevista_devolucao, FORMATO_DATA)
        nova_data = data_atual + timedelta(days=PRAZO_EMPRESTIMO_DIAS)
        emprestimo.data_prevista_devolucao = nova_data.strftime(FORMATO_DATA)
        emprestimo.renovacoes += 1
        emprestimo.status = STATUS_EMPRESTIMO_ATIVO

        self.emprestimo_repository.atualizar(emprestimo)
        return emprestimo

    # ------------------------------------------------------------------
    def _calcular_multa(self, emprestimo: Emprestimo, data_devolucao: datetime) -> float:
        data_prevista = datetime.strptime(emprestimo.data_prevista_devolucao, FORMATO_DATA)
        dias_atraso = (data_devolucao - data_prevista).days
        if dias_atraso <= 0:
            return 0.0
        return round(dias_atraso * MULTA_POR_DIA_ATRASO, 2)

    def _obter_emprestimo_ou_falhar(self, emprestimo_id: str) -> Emprestimo:
        emprestimo = self.emprestimo_repository.buscar_por_id(emprestimo_id)
        if emprestimo is None:
            raise ValueError("Empréstimo não encontrado.")
        return emprestimo

    def _atualizar_status_atrasados(self) -> None:
        """Marca como 'atrasado' os empréstimos ativos cuja data já venceu."""
        hoje = datetime.now()
        for emprestimo in self.emprestimo_repository.buscar_ativos():
            data_prevista = datetime.strptime(emprestimo.data_prevista_devolucao, FORMATO_DATA)
            if hoje > data_prevista and emprestimo.status != STATUS_EMPRESTIMO_ATRASADO:
                emprestimo.status = STATUS_EMPRESTIMO_ATRASADO
                self.emprestimo_repository.atualizar(emprestimo)

    # RF28 - relatório de livros emprestados -------------------------------
    def relatorio_emprestados(self) -> List[Emprestimo]:
        return self.emprestimo_repository.buscar_ativos()

    # RF29 - relatório de livros atrasados ----------------------------------
    def relatorio_atrasados(self) -> List[Emprestimo]:
        self._atualizar_status_atrasados()
        return [e for e in self.emprestimo_repository.listar_todos() if e.status == STATUS_EMPRESTIMO_ATRASADO]
