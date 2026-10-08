from models import Livro
from repository.livro_repository import LivroRepository
from repository.autor_repository import AutorRepository
from repository.categoria_repository import CategoriaRepository
from repository.emprestimo_repository import EmprestimoRepository
from services.base import novo_id, obrigatorio, buscar_obrigatorio


class LivroService:
    def __init__(self, livro_repository=None, autor_repository=None, categoria_repository=None, emprestimo_repository=None):
        self.repository = livro_repository or LivroRepository()
        self.autores = autor_repository or AutorRepository()
        self.categorias = categoria_repository or CategoriaRepository()
        self.emprestimos = emprestimo_repository or EmprestimoRepository()

    def consultar_livros(self):
        return self.repository.listar_todos()

    def _validar(self, titulo, autor_id, categoria_id, ano, isbn, livro_id=None):
        titulo = obrigatorio(titulo, "Título")
        if self.autores.buscar_por_id(autor_id) is None:
            raise ValueError("Selecione um autor cadastrado.")
        if self.categorias.buscar_por_id(categoria_id) is None:
            raise ValueError("Selecione uma categoria cadastrada.")
        ano = str(ano).strip()
        if ano and (not ano.isdigit() or int(ano) < 1):
            raise ValueError("Ano de publicação deve ser um inteiro positivo.")
        isbn = isbn.strip()
        if isbn and any(l.isbn == isbn and l.id != livro_id for l in self.consultar_livros()):
            raise ValueError("Já existe um livro com este ISBN.")
        return titulo, ano, isbn

    @staticmethod
    def _quantidade(quantidade):
        if isinstance(quantidade, bool) or not isinstance(quantidade, int) or quantidade < 1:
            raise ValueError("Informe uma quantidade inteira de exemplares maior que zero.")
        return quantidade

    def cadastrar_livro(self, titulo, autor_id, categoria_id, ano_publicacao="", isbn="", quantidade=1):
        titulo, ano, isbn = self._validar(titulo, autor_id, categoria_id, ano_publicacao, isbn)
        return self.repository.salvar(Livro(novo_id(), titulo, autor_id, categoria_id, ano, isbn, self._quantidade(quantidade)))

    def atualizar_livro(self, livro_id, titulo, autor_id, categoria_id, ano_publicacao="", isbn=""):
        livro = buscar_obrigatorio(self.repository, livro_id)
        titulo, ano, isbn = self._validar(titulo, autor_id, categoria_id, ano_publicacao, isbn, livro_id)
        livro.titulo, livro.autor_id, livro.categoria_id = titulo, autor_id, categoria_id
        livro.ano_publicacao, livro.isbn = ano, isbn
        return self.repository.salvar(livro)

    def adicionar_exemplares(self, livro_id, quantidade):
        livro = buscar_obrigatorio(self.repository, livro_id)
        livro.exemplares += self._quantidade(quantidade)
        return self.repository.salvar(livro)

    def excluir_livro(self, livro_id):
        livro = self.repository.buscar_por_id(livro_id)
        if livro is None:
            return False
        if livro.emprestados or any(e.livro_id == livro_id and not e.devolvido for e in self.emprestimos.listar_todos()):
            raise ValueError("Este livro possui empréstimos ativos.")
        return self.repository.excluir(livro_id)
