import io
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from interface.terminal import Terminal
from repository.funcionario_repository import FuncionarioRepository
from services.autenticacao_service import AutenticacaoService


class TestContas(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.arquivo = Path(self.tmp.name) / "funcionarios.csv"
        self.auth = AutenticacaoService(FuncionarioRepository(self.arquivo))
        self.ctx = SimpleNamespace(autenticacao=self.auth, funcionario_logado=None, entidades={})

    def test_cadastro_terminal_e_login_apos_reabrir(self):
        with patch("builtins.input", side_effect=["2", "Ana", "ana", "0"]), patch("interface.terminal.getpass", return_value="senha de teste"), patch("sys.stdout", new_callable=io.StringIO):
            Terminal(self.ctx).executar()
        self.assertNotIn("senha de teste", self.arquivo.read_text(encoding="utf-8"))
        self.ctx.autenticacao = AutenticacaoService(FuncionarioRepository(self.arquivo))
        with patch("builtins.input", side_effect=["1", "ana", "0"]), patch("interface.terminal.getpass", return_value="senha de teste"), patch("sys.stdout", new_callable=io.StringIO):
            Terminal(self.ctx).executar()
        self.assertEqual(self.ctx.funcionario_logado.nome, "Ana")
        self.assertTrue(self.auth.verificar_autorizacao(self.ctx.funcionario_logado))
        segunda = self.auth.criar_conta("Bia", "bia", "outra senha")
        self.assertFalse(self.auth.verificar_autorizacao(segunda))

    def test_senhas_diferentes_nao_salvam_conta(self):
        with patch("builtins.input", side_effect=["2", "Ana", "ana", "0"]), patch("interface.terminal.getpass", side_effect=["uma", "outra"]), patch("sys.stdout", new_callable=io.StringIO):
            Terminal(self.ctx).executar()
        self.assertEqual(self.auth.funcionario_repository.listar_todos(), [])

    def test_login_duplicado_preserva_senha_original(self):
        self.auth.criar_conta("Ana", "ana", "original")
        with self.assertRaises(ValueError):
            self.auth.criar_conta("Outra", "ana", "nova")
        self.assertIsNotNone(self.auth.autenticar("ana", "original"))
        self.assertIsNone(self.auth.autenticar("ana", "nova"))

    def test_nao_existe_login_padrao(self):
        self.assertIsNone(self.auth.autenticar("admin", "admin123"))
        self.assertEqual(self.auth.funcionario_repository.listar_todos(), [])
