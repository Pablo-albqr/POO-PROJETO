"""
Testes unitários para EmprestimoService, cobrindo RF20-RF27 e RN03-RN08.
"""

import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.emprestimo import Emprestimo
from repository.emprestimo_repository import EmprestimoRepository
from repository.livro_repository import LivroRepository
from repository.usuario_repository import UsuarioRepository
from services.emprestimo_service import EmprestimoService
from services.livro_service import LivroService
from services.usuario_service import UsuarioService
from utils.constantes import FORMATO_DATA


class TestEmprestimoService(unittest.TestCase):
    def setUp(self):
        self.diretorio_temp = tempfile.mkdtemp()

        self.usuario_repository = UsuarioRepository()
        self.usuario_repository.caminho_arquivo = os.path.join(self.diretorio_temp, "usuarios.csv")
        self.usuario_repository._garantir_arquivo()

        self.emprestimo_repository = EmprestimoRepository()
        self.emprestimo_repository.caminho_arquivo = os.path.join(self.diretorio_temp, "emprestimos.csv")
        self.emprestimo_repository._garantir_arquivo()

        self.livro_repository = LivroRepository()
        self.livro_repository.caminho_arquivo = os.path.join(self.diretorio_temp, "livros.csv")
        self.livro_repository._garantir_arquivo()

        self.usuario_service = UsuarioService(self.usuario_repository, self.emprestimo_repository)
        self.livro_service = LivroService(livro_repository=self.livro_repository)
        # Contorna as validações de autor/categoria criando o livro direto no repositório.
        from models.livro import Exemplar, Livro

        self.livro = Livro(
            id="LIV-1",
            titulo="Dom Casmurro",
            autor_id="AUT-1",
            categoria_id="CAT-1",
            exemplares=[Exemplar(id="EXP-1")],
        )
        self.livro_repository.salvar(self.livro)

        self.usuario = self.usuario_service.cadastrar_usuario("Pedro", "pedro@teste.com")

        self.emprestimo_service = EmprestimoService(
            emprestimo_repository=self.emprestimo_repository,
            livro_repository=self.livro_repository,
            usuario_repository=self.usuario_repository,
            usuario_service=self.usuario_service,
        )

    def test_registrar_emprestimo_marca_exemplar_como_emprestado(self):
        emprestimo = self.emprestimo_service.registrar_emprestimo(self.usuario.id, self.livro.id)
        livro_atualizado = self.livro_repository.buscar_por_id(self.livro.id)
        self.assertEqual(livro_atualizado.quantidade_disponivel(), 0)
        self.assertEqual(emprestimo.status, "ativo")

    def test_nao_permite_emprestimo_sem_exemplar_disponivel(self):
        self.emprestimo_service.registrar_emprestimo(self.usuario.id, self.livro.id)
        outro_usuario = self.usuario_service.cadastrar_usuario("Lucas", "lucas@teste.com")
        with self.assertRaises(ValueError):
            self.emprestimo_service.registrar_emprestimo(outro_usuario.id, self.livro.id)

    def test_devolucao_sem_atraso_nao_gera_multa(self):
        emprestimo = self.emprestimo_service.registrar_emprestimo(self.usuario.id, self.livro.id)
        devolvido = self.emprestimo_service.registrar_devolucao(emprestimo.id)
        self.assertEqual(devolvido.multa, 0.0)
        livro_atualizado = self.livro_repository.buscar_por_id(self.livro.id)
        self.assertEqual(livro_atualizado.quantidade_disponivel(), 1)

    def test_devolucao_com_atraso_gera_multa(self):
        emprestimo = self.emprestimo_service.registrar_emprestimo(self.usuario.id, self.livro.id)
        # Simula um empréstimo cuja data prevista já passou.
        data_passada = datetime.now() - timedelta(days=5)
        emprestimo.data_prevista_devolucao = data_passada.strftime(FORMATO_DATA)
        self.emprestimo_repository.atualizar(emprestimo)

        devolvido = self.emprestimo_service.registrar_devolucao(emprestimo.id)
        self.assertGreater(devolvido.multa, 0.0)

        usuario_atualizado = self.usuario_repository.buscar_por_id(self.usuario.id)
        self.assertTrue(usuario_atualizado.pendencias)

    def test_renovar_emprestimo_estende_a_data(self):
        emprestimo = self.emprestimo_service.registrar_emprestimo(self.usuario.id, self.livro.id)
        data_original = emprestimo.data_prevista_devolucao
        renovado = self.emprestimo_service.renovar_emprestimo(emprestimo.id)
        self.assertNotEqual(renovado.data_prevista_devolucao, data_original)
        self.assertEqual(renovado.renovacoes, 1)


if __name__ == "__main__":
    unittest.main()
