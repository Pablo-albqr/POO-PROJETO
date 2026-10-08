import re
from models import Usuario
from repository.usuario_repository import UsuarioRepository
from repository.emprestimo_repository import EmprestimoRepository
from services.base import novo_id, obrigatorio, buscar_obrigatorio


class UsuarioService:
    def __init__(self, usuario_repository=None, emprestimo_repository=None):
        self.repository = usuario_repository or UsuarioRepository()
        self.emprestimos = emprestimo_repository or EmprestimoRepository()

    def consultar_usuarios(self):
        return self.repository.listar_todos()

    def _validar_email(self, email, usuario_id=None):
        email = obrigatorio(email, "E-mail").lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            raise ValueError("Informe um e-mail válido.")
        if any(u.email.casefold() == email.casefold() and u.id != usuario_id for u in self.consultar_usuarios()):
            raise ValueError("Já existe um usuário com este e-mail.")
        return email

    def cadastrar_usuario(self, nome, email, telefone=""):
        return self.repository.salvar(Usuario(novo_id(), obrigatorio(nome, "Nome"), self._validar_email(email), telefone))

    def atualizar_usuario(self, usuario_id, nome, email, telefone=""):
        usuario = buscar_obrigatorio(self.repository, usuario_id)
        usuario.nome = obrigatorio(nome, "Nome")
        usuario.email = self._validar_email(email, usuario_id)
        usuario.telefone = telefone
        return self.repository.salvar(usuario)

    def excluir_usuario(self, usuario_id, funcionario_autorizado=False):
        if not funcionario_autorizado:
            raise PermissionError("É necessário um administrador para excluir usuários.")
        usuario = self.repository.buscar_por_id(usuario_id)
        if usuario is None:
            return False
        if usuario.pendencias or any(e.usuario_id == usuario_id and not e.devolvido for e in self.emprestimos.listar_todos()):
            raise ValueError("Usuário possui pendências ou empréstimos ativos.")
        return self.repository.excluir(usuario_id)
