from models import Emprestimo
from repository.base import CsvRepository


class EmprestimoRepository(CsvRepository):
    modelo = Emprestimo
    arquivo = "emprestimos.csv"
