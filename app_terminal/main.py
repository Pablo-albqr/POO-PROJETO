"""Inicie o sistema no terminal com: python main.py."""
from interface.terminal import Terminal


def main():
    try:
        Terminal().executar()
    except (EOFError, KeyboardInterrupt):
        print("\nSistema encerrado.")


if __name__ == "__main__":
    main()
