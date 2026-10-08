"""Tela de LISTAGEM (Semana 4) com acesso a cadastro, edição e EXCLUSÃO (Semana 6)."""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from interface.entidades import Entidade
from interface.formulario import FormularioDialog


class JanelaListagem(tk.Toplevel):
    def __init__(self, master, entidade: Entidade):
        super().__init__(master)
        self.entidade = entidade
        self.title(f"Gestão de {entidade.titulo}")
        self.geometry("900x460")
        self.minsize(640, 320)

        # barra superior: busca + atualizar
        topo = ttk.Frame(self, padding=(10, 10, 10, 0))
        topo.pack(fill="x")
        ttk.Label(topo, text="Buscar:").pack(side="left")
        self.var_busca = tk.StringVar()
        self.var_busca.trace_add("write", lambda *_: self.carregar())
        ttk.Entry(topo, textvariable=self.var_busca, width=30).pack(side="left", padx=6)
        ttk.Button(topo, text="Atualizar lista", command=self.carregar).pack(side="left")

        # tabela
        meio = ttk.Frame(self, padding=10)
        meio.pack(fill="both", expand=True)
        colunas = [c[0] for c in entidade.colunas]
        self.tabela = ttk.Treeview(meio, columns=colunas, show="headings", selectmode="browse")
        for cabecalho, largura in entidade.colunas:
            self.tabela.heading(cabecalho, text=cabecalho)
            self.tabela.column(cabecalho, width=largura, anchor="w")
        rolagem_v = ttk.Scrollbar(meio, orient="vertical", command=self.tabela.yview)
        rolagem_h = ttk.Scrollbar(meio, orient="horizontal", command=self.tabela.xview)
        self.tabela.configure(yscrollcommand=rolagem_v.set, xscrollcommand=rolagem_h.set)
        self.tabela.grid(row=0, column=0, sticky="nsew")
        rolagem_v.grid(row=0, column=1, sticky="ns")
        rolagem_h.grid(row=1, column=0, sticky="ew")
        meio.rowconfigure(0, weight=1)
        meio.columnconfigure(0, weight=1)
        self.tabela.bind("<Double-1>", lambda _e: self._editar())

        # botões de ação
        base = ttk.Frame(self, padding=(10, 0, 10, 10))
        base.pack(fill="x")
        ttk.Button(base, text="Cadastrar", command=self._cadastrar).pack(side="left", padx=(0, 6))
        ttk.Button(base, text="Editar", command=self._editar).pack(side="left", padx=6)
        ttk.Button(base, text="Excluir", command=self._excluir).pack(side="left", padx=6)
        self.lbl_total = ttk.Label(base, text="")
        self.lbl_total.pack(side="right")

        self.carregar()

    # -- Semana 4: listagem lendo do arquivo CSV ----------------------------
    def carregar(self) -> None:
        termo = self.var_busca.get().strip().lower()
        for linha in self.tabela.get_children():
            self.tabela.delete(linha)
        total = 0
        for item in self.entidade.listar():
            valores = self.entidade.linha(item)
            if termo and not any(termo in str(v).lower() for v in valores):
                continue
            self.tabela.insert("", "end", iid=item.id, values=valores)
            total += 1
        self.lbl_total.config(text=f"{total} registro(s)")

    def _selecionado(self) -> Optional[str]:
        selecao = self.tabela.selection()
        if not selecao:
            messagebox.showinfo("Seleção", f"Selecione um(a) {self.entidade.singular} na lista.", parent=self)
            return None
        return selecao[0]

    # -- Semana 3: cadastro -------------------------------------------------
    def _cadastrar(self) -> None:
        FormularioDialog(self, self.entidade, "cadastro", ao_salvar=self.carregar)

    # -- Semana 5: edição ---------------------------------------------------
    def _editar(self) -> None:
        item_id = self._selecionado()
        if item_id is None:
            return
        item = next((i for i in self.entidade.listar() if i.id == item_id), None)
        if item is None:
            messagebox.showerror("Erro", "Registro não encontrado.", parent=self)
            self.carregar()
            return
        FormularioDialog(
            self, self.entidade, "edicao", item_id=item_id,
            valores=self.entidade.valores_edicao(item), ao_salvar=self.carregar,
        )

    # -- Semana 6: exclusão -------------------------------------------------
    def _excluir(self) -> None:
        item_id = self._selecionado()
        if item_id is None:
            return
        if not messagebox.askyesno("Confirmar exclusão", f"Deseja realmente excluir {item_id}?", parent=self):
            return
        try:
            if self.entidade.excluir(item_id):
                messagebox.showinfo("Sucesso", f"{self.entidade.singular.capitalize()} excluído(a) com sucesso.", parent=self)
            else:
                messagebox.showwarning("Aviso", "Registro não encontrado.", parent=self)
        except (ValueError, PermissionError) as erro:
            messagebox.showerror("Erro", str(erro), parent=self)
        self.carregar()
