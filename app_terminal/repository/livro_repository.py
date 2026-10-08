from models import Livro
from repository.base import CsvRepository


class LivroRepository(CsvRepository):
    modelo = Livro
    arquivo = "livros.csv"
