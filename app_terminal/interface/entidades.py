"""
Descrição das entidades exibidas na interface (Semana 1 - planejamento).

Aqui ficam apenas dados e pequenas funções que ligam a interface aos
services já existentes. Este módulo NÃO usa Tkinter, por isso também é
usado nos testes de integração (Semana 7).
"""

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple


@dataclass
class Campo:
    chave: str
    rotulo: str
    obrigatorio: bool = False
    tipo: str = "texto"  # "texto" | "combo" | "inteiro"
    opcoes: Optional[Callable[[], List[str]]] = None  # usado quando tipo == "combo"
    so_cadastro: bool = False  # aparece apenas na tela de cadastro
    so_edicao: bool = False  # aparece apenas na tela de edição
    padrao: str = ""


@dataclass
class Entidade:
    titulo: str
    singular: str
    colunas: List[Tuple[str, int]]  # (cabeçalho, largura)
    campos: List[Campo]
    listar: Callable[[], list]
    linha: Callable[[object], tuple]
    valores_edicao: Callable[[object], Dict[str, str]]
    criar: Callable[[Dict[str, str]], object]
    atualizar: Callable[[str, Dict[str, str]], object]
    excluir: Callable[[str], bool]


def id_da_opcao(texto: str) -> str:
    """Extrai o ID de uma opção de combo no formato 'ID - Nome'."""
    return texto.split(" - ")[0].strip() if texto else ""


def montar_entidades(ctx) -> Dict[str, Entidade]:
    """Cria a descrição dos 4 CRUDs usando os services guardados em `ctx`."""

    # -- apoio para livros ---------------------------------------------------
    def opcoes_autores() -> List[str]:
        return [f"{a.id} - {a.nome}" for a in ctx.autores.consultar_autores()]

    def opcoes_categorias() -> List[str]:
        return [f"{c.id} - {c.nome}" for c in ctx.categorias.consultar_categorias()]

    def nome_autor(autor_id: str) -> str:
        autor = ctx.autores.buscar_autor_por_id(autor_id)
        return autor.nome if autor else "(removido)"

    def nome_categoria(categoria_id: str) -> str:
        categoria = ctx.categorias.buscar_categoria_por_id(categoria_id)
        return categoria.nome if categoria else "(removida)"

    def criar_livro(v: Dict[str, str]):
        quantidade = int(v["exemplares"]) if v.get("exemplares") else 1
        return ctx.livros.cadastrar_livro(
            v["titulo"], id_da_opcao(v["autor"]), id_da_opcao(v["categoria"]),
            v["ano"], v["isbn"], quantidade,
        )

    def atualizar_livro(livro_id: str, v: Dict[str, str]):
        livro = ctx.livros.atualizar_livro(
            livro_id, v["titulo"], id_da_opcao(v["autor"]), id_da_opcao(v["categoria"]),
            v["ano"], v["isbn"],
        )
        extra = int(v.get("novos_exemplares") or 0)
        if extra > 0:
            livro = ctx.livros.adicionar_exemplares(livro_id, extra)
        return livro

    def excluir_usuario(usuario_id: str) -> bool:
        autorizado = ctx.autenticacao.verificar_autorizacao(ctx.funcionario_logado)
        return ctx.usuarios.excluir_usuario(usuario_id, funcionario_autorizado=autorizado)

    # -- Usuários -------------------------------------------------------------
    usuarios = Entidade(
        titulo="Usuários",
        singular="usuário",
        colunas=[("ID", 110), ("Nome", 180), ("E-mail", 200), ("Telefone", 110), ("Situação", 110)],
        campos=[
            Campo("nome", "Nome *", obrigatorio=True),
            Campo("email", "E-mail *", obrigatorio=True),
            Campo("telefone", "Telefone"),
        ],
        listar=ctx.usuarios.consultar_usuarios,
        linha=lambda u: (u.id, u.nome, u.email, u.telefone, "com pendências" if u.pendencias else "regular"),
        valores_edicao=lambda u: {"nome": u.nome, "email": u.email, "telefone": u.telefone},
        criar=lambda v: ctx.usuarios.cadastrar_usuario(v["nome"], v["email"], v["telefone"]),
        atualizar=lambda i, v: ctx.usuarios.atualizar_usuario(i, v["nome"], v["email"], v["telefone"]),
        excluir=excluir_usuario,
    )

    # -- Autores --------------------------------------------------------------
    autores = Entidade(
        titulo="Autores",
        singular="autor",
        colunas=[("ID", 110), ("Nome", 200), ("Nacionalidade", 140), ("Biografia", 260)],
        campos=[
            Campo("nome", "Nome *", obrigatorio=True),
            Campo("nacionalidade", "Nacionalidade"),
            Campo("biografia", "Biografia"),
        ],
        listar=ctx.autores.consultar_autores,
        linha=lambda a: (a.id, a.nome, a.nacionalidade, a.biografia),
        valores_edicao=lambda a: {"nome": a.nome, "nacionalidade": a.nacionalidade, "biografia": a.biografia},
        criar=lambda v: ctx.autores.cadastrar_autor(v["nome"], v["nacionalidade"], v["biografia"]),
        atualizar=lambda i, v: ctx.autores.atualizar_autor(i, v["nome"], v["nacionalidade"], v["biografia"]),
        excluir=lambda i: ctx.autores.excluir_autor(i),
    )

    # -- Categorias -----------------------------------------------------------
    categorias = Entidade(
        titulo="Categorias",
        singular="categoria",
        colunas=[("ID", 110), ("Nome", 200), ("Descrição", 320)],
        campos=[
            Campo("nome", "Nome *", obrigatorio=True),
            Campo("descricao", "Descrição"),
        ],
        listar=ctx.categorias.consultar_categorias,
        linha=lambda c: (c.id, c.nome, c.descricao),
        valores_edicao=lambda c: {"nome": c.nome, "descricao": c.descricao},
        criar=lambda v: ctx.categorias.cadastrar_categoria(v["nome"], v["descricao"]),
        atualizar=lambda i, v: ctx.categorias.atualizar_categoria(i, v["nome"], v["descricao"]),
        excluir=lambda i: ctx.categorias.excluir_categoria(i),
    )

    # -- Livros ---------------------------------------------------------------
    livros = Entidade(
        titulo="Livros",
        singular="livro",
        colunas=[
            ("ID", 100), ("Título", 190), ("Autor", 130), ("Categoria", 110),
            ("Ano", 50), ("ISBN", 100), ("Disponíveis", 80),
        ],
        campos=[
            Campo("titulo", "Título *", obrigatorio=True),
            Campo("autor", "Autor *", obrigatorio=True, tipo="combo", opcoes=opcoes_autores),
            Campo("categoria", "Categoria *", obrigatorio=True, tipo="combo", opcoes=opcoes_categorias),
            Campo("ano", "Ano de publicação"),
            Campo("isbn", "ISBN"),
            Campo("exemplares", "Qtd. de exemplares", tipo="inteiro", so_cadastro=True, padrao="1"),
            Campo("novos_exemplares", "Adicionar exemplares", tipo="inteiro", so_edicao=True, padrao="0"),
        ],
        listar=ctx.livros.consultar_livros,
        linha=lambda l: (
            l.id, l.titulo, nome_autor(l.autor_id), nome_categoria(l.categoria_id),
            l.ano_publicacao, l.isbn, f"{l.quantidade_disponivel()}/{l.quantidade_total()}",
        ),
        valores_edicao=lambda l: {
            "titulo": l.titulo,
            "autor": f"{l.autor_id} - {nome_autor(l.autor_id)}",
            "categoria": f"{l.categoria_id} - {nome_categoria(l.categoria_id)}",
            "ano": l.ano_publicacao,
            "isbn": l.isbn,
            "novos_exemplares": "0",
        },
        criar=criar_livro,
        atualizar=atualizar_livro,
        excluir=lambda i: ctx.livros.excluir_livro(i),
    )

    return {"usuarios": usuarios, "autores": autores, "categorias": categorias, "livros": livros}
