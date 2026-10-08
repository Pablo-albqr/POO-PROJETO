import hashlib
import hmac
import secrets
from models import Funcionario
from repository.funcionario_repository import FuncionarioRepository
from services.base import novo_id, obrigatorio


class AutenticacaoService:
    def __init__(self, funcionario_repository=None):
        self.funcionario_repository = funcionario_repository or FuncionarioRepository()

    def cadastrar_funcionario(self, nome, login, senha, nivel_acesso="funcionario"):
        nome = obrigatorio(nome, "Nome")
        login = obrigatorio(login, "Login")
        obrigatorio(senha, "Senha")
        if nivel_acesso not in ("administrador", "funcionario"):
            raise ValueError("Nível de acesso inválido.")
        if any(f.login == login for f in self.funcionario_repository.listar_todos()):
            raise ValueError("Login já cadastrado.")
        salt = secrets.token_hex(16)
        digest = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt.encode(), 600000).hex()
        return self.funcionario_repository.salvar(Funcionario(novo_id(), nome, login, f"{salt}${digest}", nivel_acesso))

    def criar_conta(self, nome, login, senha):
        # A primeira conta administra esta instalação; as demais têm acesso comum.
        nivel = "funcionario" if self.funcionario_repository.listar_todos() else "administrador"
        return self.cadastrar_funcionario(nome, login, senha, nivel)

    def autenticar(self, login, senha):
        for funcionario in self.funcionario_repository.listar_todos():
            if funcionario.login == login:
                salt, digest = funcionario.senha.split("$", 1)
                tentativa = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt.encode(), 600000).hex()
                if hmac.compare_digest(tentativa, digest):
                    return funcionario
        return None

    def verificar_autorizacao(self, funcionario):
        if funcionario is None:
            return False
        salvo = self.funcionario_repository.buscar_por_id(funcionario.id)
        return salvo is not None and salvo.nivel_acesso == "administrador"
