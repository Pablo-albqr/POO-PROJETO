"""
Contexto da interface: reúne os services (já existentes) e o funcionário
logado, para serem compartilhados entre as telas. Sem Tkinter.
"""

from services.autenticacao_service import AutenticacaoService
from services.autor_service import AutorService
from services.categoria_service import CategoriaService
from services.livro_service import LivroService
from services.usuario_service import UsuarioService

from interface.entidades import montar_entidades


class Contexto:
    def __init__(self, autenticacao=None, usuarios=None, autores=None, categorias=None, livros=None):
        # Os parâmetros permitem injetar services nos testes; na aplicação
        # normal tudo é criado com os repositórios (arquivos CSV) padrão.
        self.autenticacao = autenticacao or AutenticacaoService()
        self.usuarios = usuarios or UsuarioService()
        self.autores = autores or AutorService()
        self.categorias = categorias or CategoriaService()
        self.livros = livros or LivroService()
        self.funcionario_logado = None
        self.entidades = montar_entidades(self)
