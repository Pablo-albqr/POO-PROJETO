from models import Autor
from repository.autor_repository import AutorRepository
from repository.livro_repository import LivroRepository
from services.base import novo_id, obrigatorio, buscar_obrigatorio


class AutorService:
    def __init__(self, autor_repository=None, livro_repository=None):
        self.repository = autor_repository or AutorRepository()
        self.livros = livro_repository or LivroRepository()

    def consultar_autores(self):
        return self.repository.listar_todos()

    def buscar_autor_por_id(self, autor_id):
        return self.repository.buscar_por_id(autor_id)

    def cadastrar_autor(self, nome, nacionalidade="", biografia=""):
        return self.repository.salvar(Autor(novo_id(), obrigatorio(nome, "Nome"), nacionalidade, biografia))

    def atualizar_autor(self, autor_id, nome, nacionalidade="", biografia=""):
        buscar_obrigatorio(self.repository, autor_id)
        return self.repository.salvar(Autor(autor_id, obrigatorio(nome, "Nome"), nacionalidade, biografia))

    def excluir_autor(self, autor_id):
        if any(l.autor_id == autor_id for l in self.livros.listar_todos()):
            raise ValueError("Este autor possui livros cadastrados.")
        return self.repository.excluir(autor_id)
