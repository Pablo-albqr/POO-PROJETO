from models import Usuario
from repository.base import CsvRepository


class UsuarioRepository(CsvRepository):
    modelo = Usuario
    arquivo = "usuarios.csv"
