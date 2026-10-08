import io
import unittest
from unittest.mock import patch
from interface.terminal import Terminal
from tests import test_interface


class TestTerminal(unittest.TestCase):
    setUp = test_interface.TestInterfaceIntegracao.setUp
    tearDown = test_interface.TestInterfaceIntegracao.tearDown

    def executar_menu(self, respostas):
        saida = io.StringIO()
        with patch("builtins.input", side_effect=respostas), patch("sys.stdout", saida):
            Terminal(self.ctx).menu_entidade(self.ent["autores"])
        return saida.getvalue()

    def test_crud_completo_pelos_menus(self):
        saida = self.executar_menu([
            "3", "Machado", "BR", "Biografia",
            "2", "Machado",
            "4", "1", "Machado de Assis", "", "/limpar",
            "1", "5", "1", "s", "0",
        ])
        self.assertIn("Machado de Assis", saida)
        self.assertIn("Registro excluído.", saida)
        self.assertEqual(self.ctx.autores.consultar_autores(), [])

    def test_cancelamento_e_exclusao_nao_confirmada(self):
        self.executar_menu(["3", "/cancelar", "3", "Autor", "", "", "5", "1", "n", "0"])
        self.assertEqual(len(self.ctx.autores.consultar_autores()), 1)

    def test_login_e_saida(self):
        with patch("builtins.input", side_effect=["1", "admin", "9", "0"]), patch("interface.terminal.getpass", return_value="admin123"), patch("sys.stdout", new_callable=io.StringIO) as saida:
            Terminal(self.ctx).executar()
        self.assertIn("Bem-vindo(a)", saida.getvalue())
        self.assertIn("Opção inválida.", saida.getvalue())

    def test_bloqueio_apos_tres_senhas_erradas(self):
        with patch("builtins.input", side_effect=["1", "admin"] * 3), patch("interface.terminal.getpass", return_value="errada"), patch("sys.stdout", new_callable=io.StringIO) as saida:
            Terminal(self.ctx).executar()
        self.assertIn("Número de tentativas excedido", saida.getvalue())

    def test_livro_com_selecao_numerica_e_quantidade_invalida(self):
        self.ctx.autores.cadastrar_autor("Machado")
        self.ctx.categorias.cadastrar_categoria("Romance")
        with patch("builtins.input", side_effect=["3", "Dom Casmurro", "9", "1", "1", "1899", "", "-1", "0", "2", "0"]), patch("sys.stdout", new_callable=io.StringIO):
            Terminal(self.ctx).menu_entidade(self.ent["livros"])
        livro = self.ctx.livros.consultar_livros()[0]
        self.assertEqual(livro.quantidade_total(), 2)
        self.assertEqual(livro.titulo, "Dom Casmurro")
