from models import Categoria
from repository.base import CsvRepository


class CategoriaRepository(CsvRepository):
    modelo = Categoria
    arquivo = "categorias.csv"
