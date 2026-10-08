from models import Autor
from repository.base import CsvRepository


class AutorRepository(CsvRepository):
    modelo = Autor
    arquivo = "autores.csv"
