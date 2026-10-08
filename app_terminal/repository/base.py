import csv
import os
import tempfile
from dataclasses import asdict, fields
from pathlib import Path


class CsvRepository:
    modelo = None
    arquivo = ""

    def __init__(self, caminho_arquivo=None):
        self.caminho_arquivo = caminho_arquivo or Path(__file__).resolve().parent.parent / "dados" / self.arquivo

    def _garantir_arquivo(self):
        caminho = Path(self.caminho_arquivo)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        if not caminho.exists():
            with caminho.open("x", newline="", encoding="utf-8") as arquivo:
                csv.DictWriter(arquivo, fieldnames=[f.name for f in fields(self.modelo)]).writeheader()

    def listar_todos(self):
        self._garantir_arquivo()
        with open(self.caminho_arquivo, newline="", encoding="utf-8") as arquivo:
            registros = []
            for linha in csv.DictReader(arquivo):
                valores = {}
                for campo in fields(self.modelo):
                    valor = linha[campo.name]
                    if campo.type is bool:
                        valor = valor.lower() == "true"
                    elif campo.type is int:
                        valor = int(valor)
                    valores[campo.name] = valor
                registros.append(self.modelo(**valores))
            return registros

    def buscar_por_id(self, registro_id):
        return next((r for r in self.listar_todos() if r.id == registro_id), None)

    def _gravar(self, registros):
        self._garantir_arquivo()
        caminho = Path(self.caminho_arquivo)
        temporario = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", newline="", encoding="utf-8", dir=caminho.parent, delete=False) as arquivo:
                temporario = arquivo.name
                escritor = csv.DictWriter(arquivo, fieldnames=[f.name for f in fields(self.modelo)])
                escritor.writeheader()
                escritor.writerows(asdict(r) for r in registros)
            os.replace(temporario, caminho)
        finally:
            if temporario and os.path.exists(temporario):
                os.unlink(temporario)

    def salvar(self, registro):
        registros = self.listar_todos()
        for indice, atual in enumerate(registros):
            if atual.id == registro.id:
                registros[indice] = registro
                break
        else:
            registros.append(registro)
        self._gravar(registros)
        return registro

    def excluir(self, registro_id):
        registros = self.listar_todos()
        restantes = [r for r in registros if r.id != registro_id]
        if len(restantes) == len(registros):
            return False
        self._gravar(restantes)
        return True
