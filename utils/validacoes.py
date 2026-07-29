"""
Funções de validação reutilizadas pelas camadas de serviço.
Mantê-las centralizadas evita duplicação de regras simples
de validação de dados de entrada.
"""

import re
from datetime import datetime

from utils.constantes import FORMATO_DATA

_REGEX_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validar_nao_vazio(texto: str) -> bool:
    """Retorna True se o texto não for nulo/vazio após remover espaços."""
    return bool(texto and texto.strip())


def validar_email(email: str) -> bool:
    """Valida um formato de e-mail simples (usuario@dominio.tld)."""
    return bool(email) and bool(_REGEX_EMAIL.match(email.strip()))


def validar_data(data_str: str, formato: str = FORMATO_DATA) -> bool:
    """Valida se a string representa uma data válida no formato informado."""
    try:
        datetime.strptime(data_str, formato)
        return True
    except (ValueError, TypeError):
        return False


def validar_ano(ano: str) -> bool:
    """Valida se o ano informado é um número plausível (1000-2100)."""
    try:
        ano_int = int(ano)
        return 1000 <= ano_int <= 2100
    except (ValueError, TypeError):
        return False


def validar_inteiro_positivo(valor) -> bool:
    """Valida se o valor é um inteiro maior que zero."""
    try:
        return int(valor) > 0
    except (ValueError, TypeError):
        return False
