"""
Ponto de entrada do Sistema para Bibliotecas.

Execute com:
    python main.py
"""

from menu import Menu


def main() -> None:
    menu = Menu()
    menu.executar()


if __name__ == "__main__":
    main()
