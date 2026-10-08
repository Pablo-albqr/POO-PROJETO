from uuid import uuid4


def novo_id():
    return uuid4().hex


def obrigatorio(valor, campo):
    valor = str(valor).strip()
    if not valor:
        raise ValueError(f"Preencha o campo: {campo}.")
    return valor


def buscar_obrigatorio(repository, registro_id):
    registro = repository.buscar_por_id(registro_id)
    if registro is None:
        raise ValueError("Registro não encontrado.")
    return registro
