"""
Testes unitários para UsuarioService, cobrindo RF01-RF05, RN01 e RN02.

Executar com:
    python -m unittest discover -s tests
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.emprestimo import Emprestimo
from repository.emprestimo_repository import EmprestimoRepository
from repository.usuario_repository import UsuarioRepository
from services.usuario_service import UsuarioService
from utils.constantes import MAX_LIVROS_POR_USUARIO


class TestUsuarioService(unittest.TestCase):
    def setUp(self):
        self.diretorio_temp = tempfile.mkdtemp()
        caminho_usuarios = os.path.join(self.diretorio_temp, "usuarios.csv")
        caminho_emprestimos = os.path.join(self.diretorio_temp, "emprestimos.csv")

        self.usuario_repository = UsuarioRepository()
        self.usuario_repository.caminho_arquivo = caminho_usuarios
        self.usuario_repository._garantir_arquivo()

        self.emprestimo_repository = EmprestimoRepository()
        self.emprestimo_repository.caminho_arquivo = caminho_emprestimos
        self.emprestimo_repository._garantir_arquivo()

        self.service = UsuarioService(self.usuario_repository, self.emprestimo_repository)

    def test_cadastrar_usuario_com_sucesso(self):
        usuario = self.service.cadastrar_usuario("Maria Silva", "maria@teste.com")
        self.assertEqual(usuario.nome, "Maria Silva")
        self.assertFalse(usuario.pendencias)

    def test_nao_permite_email_duplicado(self):
        self.service.cadastrar_usuario("Maria Silva", "maria@teste.com")
        with self.assertRaises(ValueError):
            self.service.cadastrar_usuario("Outra Maria", "maria@teste.com")

    def test_nao_permite_email_invalido(self):
        with self.assertRaises(ValueError):
            self.service.cadastrar_usuario("João", "email-invalido")

    def test_rn02_usuario_com_pendencia_nao_pode_emprestar(self):
        usuario = self.service.cadastrar_usuario("Carlos", "carlos@teste.com")
        self.service.marcar_pendencia(usuario.id, True)
        self.assertFalse(self.service.pode_emprestar(usuario.id))

    def test_rn01_limite_de_emprestimos_simultaneos(self):
        usuario = self.service.cadastrar_usuario("Ana", "ana@teste.com")
        for indice in range(MAX_LIVROS_POR_USUARIO):
            emprestimo = Emprestimo(
                id=f"EMP-{indice}",
                usuario_id=usuario.id,
                livro_id=f"LIV-{indice}",
                exemplar_id=f"EXP-{indice}",
                data_emprestimo="01/01/2026",
                data_prevista_devolucao="15/01/2026",
            )
            self.emprestimo_repository.salvar(emprestimo)

        self.assertFalse(self.service.pode_emprestar(usuario.id))


if __name__ == "__main__":
    unittest.main()
