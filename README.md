# Sistema para Bibliotecas

Trabalho de Programação Orientada a Objetos (POO) — sistema de gerenciamento
de biblioteca com CRUD de usuários, autores, categorias e livros, controle
de empréstimos/devoluções/renovações, relatórios e autenticação com níveis
de acesso.

## Arquitetura

O projeto segue uma arquitetura em camadas, separando responsabilidades:

```
biblioteca/
├── main.py            # Ponto de entrada da aplicação
├── menu.py             # Camada de apresentação (CLI)
├── data/                # Persistência em arquivos CSV
├── models/              # Entidades de domínio (dataclasses)
├── repository/           # Acesso a dados (padrão Repository)
├── services/              # Regras de negócio
├── utils/                  # Constantes, validações e geração de IDs
└── tests/                    # Testes unitários (unittest)
```

- **models/**: representam as entidades do domínio (`Usuario`, `Autor`,
  `Categoria`, `Livro`/`Exemplar`, `Emprestimo`, `Funcionario`), com métodos
  `to_dict`/`from_dict` para serialização em CSV.
- **repository/**: cada repositório herda de `BaseRepository`, uma classe
  genérica que implementa as operações de CRUD sobre arquivos CSV.
- **services/**: implementam as regras de negócio (RNs) e orquestram os
  repositórios. É aqui que ficam as validações (ex.: limite de 5 livros por
  usuário, cálculo de multa, bloqueio de renovação por reserva, etc.).
- **menu.py**: interface de linha de comando que apenas coleta entradas do
  usuário e delega para os services — sem lógica de negócio.

## Como executar

Requer apenas Python 3.10+ (usa apenas a biblioteca padrão, sem
dependências externas).

### Com VS Code

1. Abra a pasta do projeto no VS Code.
2. Instale a extensão Python da Microsoft.
3. Quando o VS Code pedir para selecionar um interpretador, escolha a opção para instalar ou selecionar o Python.
4. Se aparecer a opção "Install Python", clique nela.
5. Aguarde a instalação do interpretador pelo próprio VS Code.
6. Depois use o botão "Run and Debug" ou a opção "Run Biblioteca".

Se o VS Code não mostrar a opção automaticamente, abra a paleta de comandos com Ctrl+Shift+P e procure por:
- "Python: Select Interpreter"
- ou "Python: Create Environment"

### Terminal

```bash
cd biblioteca

# Linux/macOS
python3 main.py

# Windows (PowerShell)
py main.py
# ou
python main.py
```

Se o terminal retornar mensagens como "Python not found" ou "py is not recognized",
o Python não está corretamente instalado ou não está no PATH do sistema. Nesse caso,
instale o Python 3.10+ em https://www.python.org/ e marque a opção "Add Python to PATH"
durante a instalação.

Na primeira execução, um funcionário administrador padrão é criado
automaticamente:

- **login:** `admin`
- **senha:** `admin123`

## Como rodar os testes

```bash
cd biblioteca
python3 -m unittest discover -s tests -v
```

## Cobertura de requisitos

| Módulo | Requisitos cobertos |
|---|---|
| Gestão de Usuários | RF01–RF05, RN01, RN02 |
| Gestão do Acervo | RF06–RF15, RN03, RN04 |
| Consulta e Pesquisa | RF16–RF19 |
| Empréstimos | RF20–RF23, RN05, RN06 |
| Devoluções e Renovações | RF24–RF27, RN07, RN08 |
| Relatórios | RF28–RF31 |
| Segurança e Controle de Acesso | RF32, RF33, RNF02, RNF03 |

### Observações de implementação

- **RN05** (prazo de 14 dias) e **RN08** (multa por atraso) estão
  centralizados em `utils/constantes.py`, facilitando ajustes de política.
- **RN07** (bloqueio de renovação por reserva de terceiros) é suportado por
  uma estrutura simples de reservas em memória em `EmprestimoService`; o
  projeto não implementa uma tela de reservas dedicada, já que ela não
  consta nos requisitos funcionais, mas a regra de negócio já está pronta
  para ser conectada a um futuro módulo de reservas.
- **RNF01** (consultas em até 2 segundos) é atendida naturalmente pelo
  volume de dados esperado em um trabalho acadêmico com armazenamento em
  CSV; para grandes volumes de dados, recomenda-se migrar a persistência
  para um banco de dados relacional.
- **RNF02** (senhas seguras): as senhas de funcionários nunca são
  armazenadas em texto puro — apenas o hash SHA-256 é persistido.
