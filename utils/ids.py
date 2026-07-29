"""
Utilitário responsável pela geração de identificadores únicos.
Usado para garantir, por exemplo, a identificação única de cada
exemplar de livro (RN03).
"""

import uuid


def gerar_id(prefixo: str = "") -> str:
    """
    Gera um identificador único curto (8 caracteres hexadecimais),
    opcionalmente prefixado (ex.: 'USR-3f8a1c2d').
    """
    sufixo = uuid.uuid4().hex[:8]
    return f"{prefixo}-{sufixo}" if prefixo else sufixo
