"""
Regras de negócio relacionadas à Gestão de Usuários.

RF01-RF05: cadastro, consulta, atualização e exclusão de usuários.
RN01: um usuário pode ter no máximo 5 livros emprestados simultaneamente.
RN02: usuários com pendências não podem realizar novos empréstimos.
"""

from typing import List, Optional

from models.usuario import Usuario
from repository.emprestimo_repository import EmprestimoRepository
from repository.usuario_repository import UsuarioRepository
from utils.constantes import MAX_LIVROS_POR_USUARIO
from utils.ids import gerar_id
from utils.validacoes import validar_email, validar_nao_vazio


class UsuarioService:
    def __init__(
        self,
        usuario_repository: Optional[UsuarioRepository] = None,
        emprestimo_repository: Optional[EmprestimoRepository] = None,
    ):
        self.usuario_repository = usuario_repository or UsuarioRepository()
        self.emprestimo_repository = emprestimo_repository or EmprestimoRepository()

    # RF01/RF05 --------------------------------------------------------
    def cadastrar_usuario(self, nome: str, email: str, telefone: str = "") -> Usuario:
        if not validar_nao_vazio(nome):
            raise ValueError("O nome do usuário é obrigatório.")
        if not validar_email(email):
            raise ValueError("E-mail inválido.")
        if self.usuario_repository.buscar_por_email(email):
            raise ValueError("Já existe um usuário cadastrado com este e-mail.")

        usuario = Usuario(id=gerar_id("USR"), nome=nome.strip(), email=email.strip(), telefone=telefone.strip())
        return self.usuario_repository.salvar(usuario)

    # RF02 ---------------------------------------------------------------
    def consultar_usuarios(self) -> List[Usuario]:
        return self.usuario_repository.listar_todos()

    def buscar_usuario_por_id(self, usuario_id: str) -> Optional[Usuario]:
        return self.usuario_repository.buscar_por_id(usuario_id)

    def buscar_usuarios_por_nome(self, termo: str) -> List[Usuario]:
        return self.usuario_repository.buscar_por_nome(termo)

    # RF03 --------------------------------------------------------------
    def atualizar_usuario(
        self,
        usuario_id: str,
        nome: Optional[str] = None,
        email: Optional[str] = None,
        telefone: Optional[str] = None,
    ) -> Usuario:
        usuario = self.usuario_repository.buscar_por_id(usuario_id)
        if usuario is None:
            raise ValueError("Usuário não encontrado.")

        if nome is not None:
            if not validar_nao_vazio(nome):
                raise ValueError("O nome do usuário é obrigatório.")
            usuario.nome = nome.strip()
        if email is not None:
            if not validar_email(email):
                raise ValueError("E-mail inválido.")
            usuario.email = email.strip()
        if telefone is not None:
            usuario.telefone = telefone.strip()

        self.usuario_repository.atualizar(usuario)
        return usuario

    # RF04 - exclusão de usuários autorizados ---------------------------
    def excluir_usuario(self, usuario_id: str, funcionario_autorizado: bool = False) -> bool:
        if not funcionario_autorizado:
            raise PermissionError("Apenas usuários autorizados podem excluir cadastros.")
        if self.emprestimo_repository.buscar_ativos_por_usuario(usuario_id):
            raise ValueError("Não é possível excluir um usuário com empréstimos ativos.")
        return self.usuario_repository.excluir(usuario_id)

    # RN01/RN02 -----------------------------------------------------------
    def contar_emprestimos_ativos(self, usuario_id: str) -> int:
        return len(self.emprestimo_repository.buscar_ativos_por_usuario(usuario_id))

    def pode_emprestar(self, usuario_id: str) -> bool:
        usuario = self.usuario_repository.buscar_por_id(usuario_id)
        if usuario is None or not usuario.ativo:
            return False
        if usuario.pendencias:  # RN02
            return False
        if self.contar_emprestimos_ativos(usuario_id) >= MAX_LIVROS_POR_USUARIO:  # RN01
            return False
        return True

    def marcar_pendencia(self, usuario_id: str, pendencia: bool) -> None:
        usuario = self.usuario_repository.buscar_por_id(usuario_id)
        if usuario is None:
            raise ValueError("Usuário não encontrado.")
        usuario.pendencias = pendencia
        self.usuario_repository.atualizar(usuario)

    # RF30 - relatório de usuários com pendências ------------------------
    def listar_usuarios_com_pendencias(self) -> List[Usuario]:
        return [u for u in self.usuario_repository.listar_todos() if u.pendencias]
