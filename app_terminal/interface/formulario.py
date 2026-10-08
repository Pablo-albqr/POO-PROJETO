"""Telas de CADASTRO (Semana 3) e EDIÇÃO (Semana 5): mesmo formulário, dois modos."""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Dict, Optional

from interface.entidades import Entidade


class FormularioDialog(tk.Toplevel):
    def __init__(
        self,
        master,
        entidade: Entidade,
        modo: str,
        item_id: Optional[str] = None,
        valores: Optional[Dict[str, str]] = None,
        ao_salvar: Optional[Callable[[], None]] = None,
    ):
        super().__init__(master)
        self.entidade = entidade
        self.modo = modo  # "cadastro" ou "edicao"
        self.item_id = item_id
        self.ao_salvar = ao_salvar
        self.widgets: Dict[str, tk.Widget] = {}

        acao = "Cadastrar" if modo == "cadastro" else "Editar"
        self.title(f"{acao} {entidade.singular}")
        self.resizable(False, False)
        self.transient(master)

        quadro = ttk.Frame(self, padding=15)
        quadro.pack(fill="both", expand=True)

        if modo == "edicao":
            ttk.Label(quadro, text="ID:").grid(row=0, column=0, sticky="w", pady=4)
            ttk.Label(quadro, text=item_id, foreground="#555").grid(row=0, column=1, sticky="w", pady=4)

        linha = 1
        for campo in entidade.campos:
            if (campo.so_cadastro and modo != "cadastro") or (campo.so_edicao and modo != "edicao"):
                continue
            ttk.Label(quadro, text=campo.rotulo + ":").grid(row=linha, column=0, sticky="w", pady=4, padx=(0, 10))
            inicial = (valores or {}).get(campo.chave, campo.padrao)
            if campo.tipo == "combo":
                widget = ttk.Combobox(
                    quadro, width=38, state="readonly", values=campo.opcoes() if campo.opcoes else []
                )
                if inicial:
                    widget.set(inicial)
            else:
                widget = ttk.Entry(quadro, width=40)
                widget.insert(0, inicial)
            widget.grid(row=linha, column=1, pady=4)
            self.widgets[campo.chave] = widget
            linha += 1

        botoes = ttk.Frame(quadro)
        botoes.grid(row=linha, column=0, columnspan=2, pady=(12, 0), sticky="e")
        ttk.Button(botoes, text="Salvar", command=self._salvar).pack(side="left", padx=5)
        ttk.Button(botoes, text="Cancelar", command=self.destroy).pack(side="left")

        self.bind("<Return>", lambda _e: self._salvar())
        self.bind("<Escape>", lambda _e: self.destroy())

        # grab_set só funciona com a janela já visível (evita TclError no Linux)
        self.wait_visibility()
        self.grab_set()
        primeiro = next(iter(self.widgets.values()), None)
        if primeiro is not None:
            primeiro.focus_set()

    def _coletar(self) -> Dict[str, str]:
        return {chave: widget.get().strip() for chave, widget in self.widgets.items()}

    def _validar(self, valores: Dict[str, str]) -> Optional[str]:
        """Retorna uma mensagem de erro, ou None se estiver tudo certo."""
        for campo in self.entidade.campos:
            if campo.chave not in valores:
                continue
            texto = valores[campo.chave]
            nome = campo.rotulo.replace(" *", "")
            if campo.obrigatorio and not texto:
                return f"Preencha o campo: {nome}"
            if campo.tipo == "inteiro" and texto and not texto.isdigit():
                return f"{nome} deve ser um número inteiro (0 ou maior)."
        return None

    def _salvar(self) -> None:
        valores = self._coletar()
        erro_validacao = self._validar(valores)
        if erro_validacao:
            messagebox.showwarning("Dados inválidos", erro_validacao, parent=self)
            return
        try:
            if self.modo == "cadastro":
                self.entidade.criar(valores)
                mensagem = f"{self.entidade.singular.capitalize()} cadastrado(a) com sucesso!"
            else:
                self.entidade.atualizar(self.item_id, valores)
                mensagem = f"{self.entidade.singular.capitalize()} atualizado(a) com sucesso!"
        except (ValueError, PermissionError) as erro:
            messagebox.showerror("Erro", str(erro), parent=self)
            return
        messagebox.showinfo("Sucesso", mensagem, parent=self)
        if self.ao_salvar:
            self.ao_salvar()
        self.destroy()
