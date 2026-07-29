"""Regras de negócio relacionadas à Gestão de Autores."""

from typing import List, Optional

from models.autor import Autor
from repository.autor_repository import AutorRepository
from repository.livro_repository import LivroRepository
from utils.ids import gerar_id
from utils.validacoes import validar_nao_vazio


class AutorService:
    def __init__(
        self,
        autor_repository: Optional[AutorRepository] = None,
        livro_repository: Optional[LivroRepository] = None,
    ):
        self.autor_repository = autor_repository or AutorRepository()
        self.livro_repository = livro_repository or LivroRepository()

    # RF07 ----------------------------------------------------------------
    def cadastrar_autor(self, nome: str, nacionalidade: str = "", biografia: str = "") -> Autor:
        if not validar_nao_vazio(nome):
            raise ValueError("O nome do autor é obrigatório.")
        autor = Autor(id=gerar_id("AUT"), nome=nome.strip(), nacionalidade=nacionalidade.strip(), biografia=biografia.strip())
        return self.autor_repository.salvar(autor)

    # RF14 ----------------------------------------------------------------
    def consultar_autores(self) -> List[Autor]:
        return self.autor_repository.listar_todos()

    def buscar_autor_por_id(self, autor_id: str) -> Optional[Autor]:
        return self.autor_repository.buscar_por_id(autor_id)

    def buscar_autores_por_nome(self, termo: str) -> List[Autor]:
        return self.autor_repository.buscar_por_nome(termo)

    # RF15 ----------------------------------------------------------------
    def atualizar_autor(
        self,
        autor_id: str,
        nome: Optional[str] = None,
        nacionalidade: Optional[str] = None,
        biografia: Optional[str] = None,
    ) -> Autor:
        autor = self.autor_repository.buscar_por_id(autor_id)
        if autor is None:
            raise ValueError("Autor não encontrado.")

        if nome is not None:
            if not validar_nao_vazio(nome):
                raise ValueError("O nome do autor é obrigatório.")
            autor.nome = nome.strip()
        if nacionalidade is not None:
            autor.nacionalidade = nacionalidade.strip()
        if biografia is not None:
            autor.biografia = biografia.strip()

        self.autor_repository.atualizar(autor)
        return autor

    # RF09 ----------------------------------------------------------------
    def excluir_autor(self, autor_id: str) -> bool:
        if self.livro_repository.buscar_por_autor(autor_id):
            raise ValueError("Não é possível remover um autor que possui livros cadastrados.")
        return self.autor_repository.excluir(autor_id)
