"""Registros persistidos pelo sistema de bibliotecas."""
from dataclasses import dataclass


@dataclass
class Autor:
    id: str
    nome: str
    nacionalidade: str = ""
    biografia: str = ""


@dataclass
class Categoria:
    id: str
    nome: str
    descricao: str = ""


@dataclass
class Usuario:
    id: str
    nome: str
    email: str
    telefone: str = ""
    pendencias: bool = False


@dataclass
class Funcionario:
    id: str
    nome: str
    login: str
    senha: str
    nivel_acesso: str = "funcionario"


@dataclass
class Livro:
    id: str
    titulo: str
    autor_id: str
    categoria_id: str
    ano_publicacao: str = ""
    isbn: str = ""
    exemplares: int = 1
    emprestados: int = 0

    def quantidade_total(self):
        return self.exemplares

    def quantidade_disponivel(self):
        return self.exemplares - self.emprestados


@dataclass
class Emprestimo:
    id: str
    usuario_id: str
    livro_id: str
    devolvido: bool = False
