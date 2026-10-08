from models import Categoria
from repository.categoria_repository import CategoriaRepository
from repository.livro_repository import LivroRepository
from services.base import novo_id, obrigatorio, buscar_obrigatorio


class CategoriaService:
    def __init__(self, categoria_repository=None, livro_repository=None):
        self.repository = categoria_repository or CategoriaRepository()
        self.livros = livro_repository or LivroRepository()

    def consultar_categorias(self):
        return self.repository.listar_todos()

    def buscar_categoria_por_id(self, categoria_id):
        return self.repository.buscar_por_id(categoria_id)

    def cadastrar_categoria(self, nome, descricao=""):
        return self.repository.salvar(Categoria(novo_id(), obrigatorio(nome, "Nome"), descricao))

    def atualizar_categoria(self, categoria_id, nome, descricao=""):
        buscar_obrigatorio(self.repository, categoria_id)
        return self.repository.salvar(Categoria(categoria_id, obrigatorio(nome, "Nome"), descricao))

    def excluir_categoria(self, categoria_id):
        if any(l.categoria_id == categoria_id for l in self.livros.listar_todos()):
            raise ValueError("Esta categoria possui livros cadastrados.")
        return self.repository.excluir(categoria_id)
