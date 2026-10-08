"""TELA PRINCIPAL (Semana 2): login e menu com acesso a cada CRUD."""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from interface.contexto import Contexto
from interface.listagem import JanelaListagem

MAX_TENTATIVAS_LOGIN = 3


class TelaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema para Bibliotecas")
        self.geometry("420x360")
        self.resizable(False, False)
        self.ctx = Contexto()
        self._quadro: Optional[ttk.Frame] = None
        self._tentativas = 0
        self._mostrar_login()

    def _trocar_quadro(self) -> ttk.Frame:
        if self._quadro is not None:
            self._quadro.destroy()
        self._quadro = ttk.Frame(self, padding=25)
        self._quadro.pack(fill="both", expand=True)
        return self._quadro

    # -- login (usa o AutenticacaoService existente) ------------------------
    def _mostrar_login(self) -> None:
        self.unbind("<Return>")
        q = self._trocar_quadro()
        ttk.Label(q, text="SISTEMA PARA BIBLIOTECAS", font=("Segoe UI", 14, "bold")).pack(pady=(10, 4))
        ttk.Label(q, text="Use sua conta cadastrada pelo terminal", foreground="#666").pack(pady=(0, 20))

        form = ttk.Frame(q)
        form.pack()
        ttk.Label(form, text="Login:").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_login = ttk.Entry(form, width=26)
        self.ent_login.grid(row=0, column=1, pady=5, padx=(8, 0))
        ttk.Label(form, text="Senha:").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_senha = ttk.Entry(form, width=26, show="*")
        self.ent_senha.grid(row=1, column=1, pady=5, padx=(8, 0))

        ttk.Button(q, text="Entrar", command=self._entrar).pack(pady=20)
        self.bind("<Return>", lambda _e: self._entrar())
        self.ent_login.focus_set()

    def _entrar(self) -> None:
        funcionario = self.ctx.autenticacao.autenticar(
            self.ent_login.get().strip(), self.ent_senha.get().strip()
        )
        if funcionario is None:
            self._tentativas += 1
            if self._tentativas >= MAX_TENTATIVAS_LOGIN:
                messagebox.showerror("Login", "Número de tentativas excedido. Encerrando o sistema.")
                self.destroy()
                return
            messagebox.showerror("Login", "Login ou senha inválidos.")
            self.ent_senha.delete(0, "end")
            return
        self.ctx.funcionario_logado = funcionario
        self._mostrar_menu()

    # -- menu principal -----------------------------------------------------
    def _mostrar_menu(self) -> None:
        self.unbind("<Return>")
        q = self._trocar_quadro()
        func = self.ctx.funcionario_logado
        ttk.Label(q, text="MENU PRINCIPAL", font=("Segoe UI", 14, "bold")).pack(pady=(0, 2))
        ttk.Label(q, text=f"{func.nome} ({func.nivel_acesso})", foreground="#666").pack(pady=(0, 16))

        for chave in ("usuarios", "autores", "categorias", "livros"):
            entidade = self.ctx.entidades[chave]
            ttk.Button(
                q, text=entidade.titulo, width=28,
                command=lambda e=entidade: JanelaListagem(self, e),
            ).pack(pady=5, ipady=4)

        ttk.Button(q, text="Sair", width=28, command=self.destroy).pack(pady=(14, 0))
