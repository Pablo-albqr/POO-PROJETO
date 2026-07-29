"""
Constantes globais utilizadas em todo o sistema.
Centralizar esses valores facilita a manutenção e a alteração
das regras de negócio (RN01 a RN08) em um único lugar.
"""

import os

# ---------------------------------------------------------------------------
# Caminhos de arquivos (persistência em CSV)
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

CAMINHO_USUARIOS = os.path.join(DATA_DIR, "usuarios.csv")
CAMINHO_AUTORES = os.path.join(DATA_DIR, "autores.csv")
CAMINHO_CATEGORIAS = os.path.join(DATA_DIR, "categorias.csv")
CAMINHO_LIVROS = os.path.join(DATA_DIR, "livros.csv")
CAMINHO_EMPRESTIMOS = os.path.join(DATA_DIR, "emprestimos.csv")
CAMINHO_FUNCIONARIOS = os.path.join(DATA_DIR, "funcionarios.csv")

# ---------------------------------------------------------------------------
# Regras de negócio
# ---------------------------------------------------------------------------
MAX_LIVROS_POR_USUARIO = 5          # RN01
PRAZO_EMPRESTIMO_DIAS = 14          # RN05
MULTA_POR_DIA_ATRASO = 1.50         # RN08 - valor em R$ por dia de atraso
MAX_RENOVACOES = 2                  # limite de renovações por empréstimo

# ---------------------------------------------------------------------------
# Status possíveis
# ---------------------------------------------------------------------------
STATUS_EXEMPLAR_DISPONIVEL = "disponivel"
STATUS_EXEMPLAR_EMPRESTADO = "emprestado"

STATUS_EMPRESTIMO_ATIVO = "ativo"
STATUS_EMPRESTIMO_DEVOLVIDO = "devolvido"
STATUS_EMPRESTIMO_ATRASADO = "atrasado"

# ---------------------------------------------------------------------------
# Controle de acesso (RF33)
# ---------------------------------------------------------------------------
NIVEL_ADMINISTRADOR = "administrador"
NIVEL_BIBLIOTECARIO = "bibliotecario"
NIVEIS_ACESSO = (NIVEL_ADMINISTRADOR, NIVEL_BIBLIOTECARIO)

FORMATO_DATA = "%d/%m/%Y"
