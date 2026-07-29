"""
Regras de negócio de Segurança e Controle de Acesso.

RF32: autenticação por login e senha.
RF33: diferentes níveis de acesso (administrador e bibliotecário).
RNF02: senhas armazenadas de forma segura (hash, nunca em texto puro).
RNF03: apenas usuários autorizados podem alterar/excluir registros.
"""

import hashlib
from typing import Optional

from models.funcionario import Funcionario
from repository.funcionario_repository import FuncionarioRepository
from utils.constantes import NIVEIS_ACESSO, NIVEL_BIBLIOTECARIO
from utils.ids import gerar_id
from utils.validacoes import validar_nao_vazio


class AutenticacaoService:
    def __init__(self, funcionario_repository: Optional[FuncionarioRepository] = None):
        self.funcionario_repository = funcionario_repository or FuncionarioRepository()

    @staticmethod
    def _gerar_hash(senha: str) -> str:
        # RNF02 - a senha nunca é armazenada em texto puro.
        return hashlib.sha256(senha.encode("utf-8")).hexdigest()

    def cadastrar_funcionario(
        self, nome: str, login: str, senha: str, nivel_acesso: str = NIVEL_BIBLIOTECARIO
    ) -> Funcionario:
        if not validar_nao_vazio(nome) or not validar_nao_vazio(login):
            raise ValueError("Nome e login são obrigatórios.")
        if not validar_nao_vazio(senha) or len(senha) < 4:
            raise ValueError("A senha deve possuir ao menos 4 caracteres.")
        if nivel_acesso not in NIVEIS_ACESSO:
            raise ValueError(f"Nível de acesso inválido. Use um de: {NIVEIS_ACESSO}.")
        if self.funcionario_repository.buscar_por_login(login):
            raise ValueError("Já existe um funcionário com este login.")

        funcionario = Funcionario(
            id=gerar_id("FUNC"),
            nome=nome.strip(),
            login=login.strip(),
            senha_hash=self._gerar_hash(senha),
            nivel_acesso=nivel_acesso,
        )
        return self.funcionario_repository.salvar(funcionario)

    def autenticar(self, login: str, senha: str) -> Optional[Funcionario]:
        # RF32
        funcionario = self.funcionario_repository.buscar_por_login(login)
        if funcionario is None:
            return None
        if funcionario.senha_hash != self._gerar_hash(senha):
            return None
        return funcionario

    def verificar_autorizacao(self, funcionario: Optional[Funcionario]) -> bool:
        # RNF03 - apenas usuários autenticados podem alterar/excluir registros.
        return funcionario is not None
