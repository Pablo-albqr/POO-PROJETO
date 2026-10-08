"""
Semana 7 - Teste da integração interface <-> arquivos.

Executa o CRUD de cada tela usando as mesmas funções que os botões chamam,
sobre uma cópia temporária dos CSV (os dados reais não são alterados).
Não precisa de Tkinter nem abre janelas.

Rode com:  python -m unittest tests.test_interface -v
"""

import os
import tempfile
import unittest

from interface.contexto import Contexto
from repository.autor_repository import AutorRepository
from repository.categoria_repository import CategoriaRepository
from repository.emprestimo_repository import EmprestimoRepository
from repository.funcionario_repository import FuncionarioRepository
from repository.livro_repository import LivroRepository
from repository.usuario_repository import UsuarioRepository
from services.autenticacao_service import AutenticacaoService
from services.autor_service import AutorService
from services.categoria_service import CategoriaService
from services.livro_service import LivroService
from services.usuario_service import UsuarioService


def _repo(classe, pasta, nome):
    repo = classe()
    repo.caminho_arquivo = os.path.join(pasta, nome)  # aponta para o arquivo temporário
    repo._garantir_arquivo()
    return repo


class TestInterfaceIntegracao(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        p = self._tmp.name
        autor_r = _repo(AutorRepository, p, "autores.csv")
        cat_r = _repo(CategoriaRepository, p, "categorias.csv")
        liv_r = _repo(LivroRepository, p, "livros.csv")
        emp_r = _repo(EmprestimoRepository, p, "emprestimos.csv")
        usu_r = _repo(UsuarioRepository, p, "usuarios.csv")
        fun_r = _repo(FuncionarioRepository, p, "funcionarios.csv")
        self.ctx = Contexto(
            autenticacao=AutenticacaoService(fun_r),
            usuarios=UsuarioService(usu_r, emp_r),
            autores=AutorService(autor_r, liv_r),
            categorias=CategoriaService(cat_r, liv_r),
            livros=LivroService(liv_r, autor_r, cat_r, emp_r),
        )
        self.ctx.autenticacao.criar_conta("Administrador de teste", "admin", "admin123")
        self.ctx.funcionario_logado = self.ctx.autenticacao.autenticar("admin", "admin123")
        self.ent = self.ctx.entidades

    def tearDown(self):
        self._tmp.cleanup()

    def test_login_cadastrado(self):
        self.assertIsNotNone(self.ctx.funcionario_logado)
        self.assertIsNone(self.ctx.autenticacao.autenticar("admin", "errada"))

    def test_crud_autor(self):
        e = self.ent["autores"]
        a = e.criar({"nome": "Machado", "nacionalidade": "BR", "biografia": ""})
        self.assertEqual([x.id for x in e.listar()], [a.id])
        e.atualizar(a.id, {"nome": "Machado de Assis", "nacionalidade": "BR", "biografia": "x"})
        self.assertEqual(e.listar()[0].nome, "Machado de Assis")
        self.assertTrue(e.excluir(a.id))
        self.assertEqual(e.listar(), [])

    def test_crud_categoria(self):
        e = self.ent["categorias"]
        c = e.criar({"nome": "Romance", "descricao": ""})
        e.atualizar(c.id, {"nome": "Clássico", "descricao": "d"})
        self.assertEqual(e.listar()[0].nome, "Clássico")
        self.assertTrue(e.excluir(c.id))
        self.assertEqual(e.listar(), [])

    def test_crud_usuario(self):
        e = self.ent["usuarios"]
        u = e.criar({"nome": "Ana", "email": "ana@exemplo.com", "telefone": "1"})
        e.atualizar(u.id, {"nome": "Ana B", "email": "ana@exemplo.com", "telefone": "2"})
        self.assertEqual(e.listar()[0].nome, "Ana B")
        with self.assertRaises(ValueError):
            e.criar({"nome": "Outra", "email": "ana@exemplo.com", "telefone": ""})  # e-mail repetido
        self.assertTrue(e.excluir(u.id))
        self.assertEqual(e.listar(), [])

    def test_exclusao_usuario_exige_login(self):
        e = self.ent["usuarios"]
        u = e.criar({"nome": "Ana", "email": "ana@exemplo.com", "telefone": ""})
        self.ctx.funcionario_logado = None
        with self.assertRaises(PermissionError):
            e.excluir(u.id)

    def test_crud_livro_e_regras(self):
        a = self.ent["autores"].criar({"nome": "Machado", "nacionalidade": "", "biografia": ""})
        c = self.ent["categorias"].criar({"nome": "Romance", "descricao": ""})
        e = self.ent["livros"]
        base = {"autor": f"{a.id} - Machado", "categoria": f"{c.id} - Romance"}

        l = e.criar({**base, "titulo": "Dom Casmurro", "ano": "1899", "isbn": "1", "exemplares": "2"})
        self.assertEqual(e.listar()[0].quantidade_total(), 2)

        e.atualizar(l.id, {**base, "titulo": "Dom Casmurro 2", "ano": "1900", "isbn": "1", "novos_exemplares": "1"})
        salvo = e.listar()[0]
        self.assertEqual((salvo.titulo, salvo.quantidade_total()), ("Dom Casmurro 2", 3))

        with self.assertRaises(ValueError):  # autor tem livro
            self.ent["autores"].excluir(a.id)
        with self.assertRaises(ValueError):  # categoria tem livro
            self.ent["categorias"].excluir(c.id)

        self.assertTrue(e.excluir(l.id))
        self.assertTrue(self.ent["autores"].excluir(a.id))
        self.assertTrue(self.ent["categorias"].excluir(c.id))


if __name__ == "__main__":
    unittest.main()
