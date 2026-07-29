"""
Repositório genérico com persistência em arquivos CSV.

Implementa o padrão Repository: encapsula toda a lógica de leitura
e escrita em disco, para que as camadas superiores (services) não
precisem conhecer detalhes de armazenamento. Cada repositório
específico (AutorRepository, LivroRepository, etc.) herda desta
classe e apenas define o caminho do arquivo, o model e as colunas.
"""

import csv
import os
from typing import Generic, List, Optional, Type, TypeVar

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, caminho_arquivo: str, model_class: Type[T], fieldnames: List[str]):
        self.caminho_arquivo = caminho_arquivo
        self.model_class = model_class
        self.fieldnames = fieldnames
        self._garantir_arquivo()

    # ------------------------------------------------------------------
    # Infra
    # ------------------------------------------------------------------
    def _garantir_arquivo(self) -> None:
        os.makedirs(os.path.dirname(self.caminho_arquivo), exist_ok=True)
        if not os.path.exists(self.caminho_arquivo):
            with open(self.caminho_arquivo, "w", newline="", encoding="utf-8") as arquivo:
                writer = csv.DictWriter(arquivo, fieldnames=self.fieldnames)
                writer.writeheader()

    def _salvar_todos(self, itens: List[T]) -> None:
        with open(self.caminho_arquivo, "w", newline="", encoding="utf-8") as arquivo:
            writer = csv.DictWriter(arquivo, fieldnames=self.fieldnames)
            writer.writeheader()
            for item in itens:
                writer.writerow(item.to_dict())

    # ------------------------------------------------------------------
    # Operações CRUD (RF de cadastro / consulta / atualização / exclusão)
    # ------------------------------------------------------------------
    def listar_todos(self) -> List[T]:
        with open(self.caminho_arquivo, newline="", encoding="utf-8") as arquivo:
            reader = csv.DictReader(arquivo)
            return [self.model_class.from_dict(linha) for linha in reader if linha.get("id")]

    def buscar_por_id(self, id_: str) -> Optional[T]:
        for item in self.listar_todos():
            if item.id == id_:
                return item
        return None

    def salvar(self, item: T) -> T:
        itens = self.listar_todos()
        itens.append(item)
        self._salvar_todos(itens)
        return item

    def atualizar(self, item: T) -> bool:
        itens = self.listar_todos()
        for indice, existente in enumerate(itens):
            if existente.id == item.id:
                itens[indice] = item
                self._salvar_todos(itens)
                return True
        return False

    def excluir(self, id_: str) -> bool:
        itens = self.listar_todos()
        novos = [item for item in itens if item.id != id_]
        if len(novos) == len(itens):
            return False
        self._salvar_todos(novos)
        return True

    def existe(self, id_: str) -> bool:
        return self.buscar_por_id(id_) is not None
