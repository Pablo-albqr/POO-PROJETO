from models import Funcionario
from repository.base import CsvRepository


class FuncionarioRepository(CsvRepository):
    modelo = Funcionario
    arquivo = "funcionarios.csv"
