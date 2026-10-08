# Sistema para Bibliotecas

Execute com Python 3 em um terminal:

```console
python main.py
```

Escolha **2 - Criar usuário** e informe nome, login e senha.
Depois escolha **1 - Entrar** com os dados cadastrados. A conta fica salva
em `dados/funcionarios.csv` para os próximos acessos, com a senha protegida
por hash. Não existe mais uma conta padrão criada automaticamente.
A primeira conta criada é administradora; as seguintes têm acesso comum.
Cadastre autores e categorias antes dos livros. O menu permite cadastrar,
consultar, editar e excluir usuários, autores, categorias e livros.

Escolha as opções digitando os números dos menus. Na edição, Enter mantém
o valor atual e `/limpar` apaga um campo opcional. Use `/cancelar` para
cancelar um formulário. A senha não aparece enquanto é digitada.
O comando antigo `python gui.py` também inicia a interface de terminal.
Tkinter não é necessário.

Os dados são salvos automaticamente na pasta `dados`, ao lado de `gui.py`.
As senhas são armazenadas como hashes PBKDF2 com salt. Não são necessárias
bibliotecas externas. A persistência foi projetada para uma instância local
do programa por vez.

Para executar os testes sem alterar os cadastros reais:

```console
python -m unittest discover -s tests -v
```
