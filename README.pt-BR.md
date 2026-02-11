# Python Git AI

[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](README.md) | **Portugues**

Automacao de workflow Git com IA para Python. Gere mensagens de commit inteligentes, changelogs automaticos e valide commits usando Conventional Commits.

## Por que usar esta ferramenta em vez do Claude Code diretamente?

Se voce ja usa o Claude Code CLI, pode se perguntar: "Por que nao pedir pro Claude fazer o commit direto?" Veja o que esta ferramenta agrega:

| Recurso | Claude Code sozinho | Python Git AI |
|---------|---------------------|---------------|
| Formato Conventional Commits | Precisa pedir toda vez | Forcado automaticamente via saida estruturada |
| Schema JSON consistente | Texto livre, pode variar | Validado contra um schema rigoroso sempre |
| Escopos do projeto | Precisa lembrar de mencionar | Configurado uma vez, forcado em todo commit |
| Tipos de commit permitidos | Disciplina manual | Restrito por config, IA nao pode usar outros |
| Suporte multi-idioma | Precisa especificar em todo prompt | Configurado uma vez, sempre aplicado |
| Geracao de changelog | Trabalho manual | Automatizado do historico de commits entre tags |
| Validacao via git hook | Nao disponivel | Hook opcional rejeita commits nao-convencionais |
| Consistencia no time | Cada dev faz prompt diferente | Mesmas regras para todos via config compartilhada |
| Controle de tamanho do diff | Sem controle, pode exceder contexto | Truncado automaticamente ate o limite configurado |
| Funciona sem CLI instalado | N/A | Usa providers de API (Anthropic/OpenAI) como fallback |

Resumindo: esta ferramenta transforma commits gerados por IA em um **padrao repetivel para o time todo** em vez de um prompt avulso.

## Funcionalidades

- **`git-ai commit`** -- Gera mensagens de commit a partir de mudancas em stage usando IA, seguindo Conventional Commits
- **`git-ai changelog`** -- Gera changelogs estruturados do historico de commits entre tags
- **`git-ai setup`** -- Wizard de configuracao interativo
- **3 providers** -- Anthropic API, OpenAI API ou Claude Code CLI (sem chave de API)
- **9 idiomas** -- Ingles, Portugues, Espanhol, Frances, Alemao, Italiano, Japones, Coreano, Chines
- **Restricao de escopos** -- Restrinja commits aos escopos do seu projeto
- **Restricao de tipos** -- Limite quais tipos de Conventional Commits sao permitidos
- **Templates de commit** -- Built-in (`minimal`, `detailed`) e presets customizados para configuracoes de body + footer
- **Controle de body** -- Configure se a IA sempre inclui body, nunca inclui, ou decide automaticamente
- **Controle de footer** -- Toggle do footer BREAKING CHANGE, adicione footer lines customizados, controle o trailer Co-Authored-By
- **Git hook** -- Hook `commit-msg` opcional que rejeita commits nao-convencionais
- **Saida estruturada** -- Respostas da IA validadas contra um JSON schema, nunca texto livre
- **Truncamento de diff** -- Diffs grandes sao automaticamente truncados para caber na janela de contexto da IA

## Requisitos

- Python 3.13+
- Um dos seguintes:
  - Chave de API da Anthropic ou OpenAI
  - **OU** [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) instalado na sua maquina (usa sua assinatura existente do Claude, ex: plano Max -- sem chave de API)

## Instalacao

```bash
# Usando UV (recomendado)
uv tool install git-ai

# Usando pip
pip install git-ai

# Usando pipx
pipx install git-ai
```

## Configuracao do Provider

### Opcao 1: Anthropic API (padrao)

```bash
export GIT_AI_PROVIDER=anthropic
export ANTHROPIC_API_KEY=sua-chave-api
```

### Opcao 2: OpenAI API

```bash
export GIT_AI_PROVIDER=openai
export OPENAI_API_KEY=sua-chave-api
```

### Opcao 3: Claude Code CLI (sem chave de API)

Se voce tem uma assinatura do Claude (ex: plano Max) e o Claude Code CLI instalado, pode usa-lo diretamente sem nenhuma chave de API:

```bash
export GIT_AI_PROVIDER=claude-code
```

Certifique-se de que o binario `claude` esta disponivel no seu PATH. Instale em: https://docs.anthropic.com/en/docs/claude-code

Esta opcao invoca o Claude Code CLI como subprocesso, passando um prompt estruturado e fazendo parse da resposta JSON. Consome do uso da sua assinatura existente -- sem tokens de API separados.

## Uso

### `git-ai commit` -- Gerar mensagem de commit

Adicione suas mudancas ao stage e execute:

```bash
git-ai commit
```

Ou adicione tudo automaticamente com a flag `--all` (`-a`):

```bash
git-ai commit --all
```

**Opcoes disponiveis:**

| Opcao | Curto | Descricao |
|-------|-------|-----------|
| `--all` | `-a` | Adiciona todas as mudancas ao stage antes de commitar |
| `--template` | | Usar um template de commit nomeado (ex: `minimal`, `detailed`) |
| `--no-body` | | Remover body da mensagem de commit |
| `--footer` | | Adicionar linha(s) de footer customizada(s) (pode ser usado multiplas vezes) |

**O que acontece:**

1. Le o diff das mudancas em stage (truncado se exceder `max_diff_size`)
2. Envia para o provider de IA configurado
3. Recebe uma resposta estruturada com `type`, `scope`, `description`, `body` e `is_breaking_change`
4. Valida o tipo e escopo contra sua configuracao
5. Formata a mensagem seguindo Conventional Commits
6. Permite que voce escolha o que fazer

**Menu interativo:**

```
Staged changes:
 src/models/user.py    | 12 ++++++---
 src/api/auth.py       | 8 ++++--
 2 files changed, 14 insertions(+), 6 deletions(-)

Generated commit message:
  feat(auth): adicionar verificacao de email no registro

What would you like to do?
  > accept
    edit
    regenerate
    cancel
```

- **accept** -- Cria o commit com a mensagem gerada
- **edit** -- Abre prompts para modificar titulo e corpo separadamente
- **regenerate** -- Chama a IA novamente para uma mensagem diferente
- **cancel** -- Aborta sem commitar

**Exemplo com corpo e breaking change:**

```
Generated commit message:
  feat(api)!: substituir endpoints REST por GraphQL

  Migrar todos os endpoints da API de REST para GraphQL.
  Isso remove todas as rotas /api/v1/*.

  BREAKING CHANGE: substituir endpoints REST por GraphQL
```

### `git-ai changelog` -- Gerar changelog

```bash
git-ai changelog
```

**Opcoes disponiveis:**

| Opcao | Descricao | Padrao |
|-------|-----------|--------|
| `--from` | Tag ou hash de commit inicial | Ultima tag (ou primeiro commit se nao houver tags) |
| `--to` | Tag ou hash de commit final | `HEAD` |
| `--tag` | Tag de versao para o cabecalho do changelog | Prompt interativo |
| `--dry-run` | Preview sem escrever no arquivo | `false` |

**Exemplos:**

```bash
# Detectar range automaticamente (ultima tag ate HEAD)
git-ai changelog

# A partir de uma tag especifica ate HEAD
git-ai changelog --from v1.0.0

# Entre duas referencias
git-ai changelog --from v1.0.0 --to v1.1.0

# Especificar a tag de versao antecipadamente
git-ai changelog --tag v2.0.0

# Preview sem escrever no arquivo
git-ai changelog --dry-run

# Combinar opcoes
git-ai changelog --from v1.0.0 --to v2.0.0 --tag v2.0.0 --dry-run
```

**O que acontece:**

1. Resolve a referencia inicial (prioridade: `--from` > ultima tag > primeiro commit)
2. Busca todos os commits entre `from` e `to`
3. Faz parse de cada mensagem de commit usando o formato Conventional Commits
4. Agrupa commits por tipo (`feat`, `fix`, `docs`, etc.)
5. Envia os commits agrupados para a IA gerar descricoes legiveis
6. Formata a saida como Markdown com emojis (configuravel)
7. Mostra preview e pede confirmacao antes de escrever

**Exemplo de saida (`CHANGELOG.md`):**

```markdown
## [v1.2.0] - 2026-02-11

### Funcionalidades

- Adicionar verificacao de email durante registro de usuario
- Implementar redefinicao de senha via SMS

### Correcoes

- Resolver null pointer ao carregar preferencias do usuario
- Corrigir tratamento de fuso horario em notificacoes agendadas

### Documentacao

- Atualizar guia de autenticacao da API com exemplos OAuth2
```

Se `changelog.with_emojis` estiver habilitado (padrao), os titulos das secoes incluem emojis:

```markdown
### ✨ Features
### 🐛 Bug Fixes
### 📚 Documentation
### ♻️ Code Refactoring
### ⚡ Performance Improvements
### 🧪 Tests
### 📦 Build System
### 🔧 Continuous Integration
### 🔨 Chores
### ⏪ Reverts
```

O changelog e inserido no topo do arquivo existente. Se o `CHANGELOG.md` ja existir, o novo conteudo e adicionado acima (abaixo do cabecalho), preservando entradas anteriores.

### `git-ai setup` -- Configuracao interativa

```bash
git-ai setup
```

O wizard guia voce por todas as opcoes configuraveis:

1. **Provider de IA** -- Anthropic API, OpenAI API ou Claude Code CLI
2. **Idioma** -- Ingles, Portugues (Brasil), Espanhol, Frances, Alemao, Italiano, Japones, Coreano ou Chines
3. **Escopos** -- Definir escopos permitidos para seu projeto (ex: `auth`, `api`, `ui`, `database`)
4. **Tipos** -- Restringir quais tipos de commit sao permitidos (ex: apenas `feat`, `fix`, `docs`)
5. **Preferencia de body** -- Como a IA trata o corpo da mensagem de commit (auto, sempre, nunca)
6. **Git hook** -- Instalar hook `commit-msg` que rejeita commits nao-convencionais

Apos o setup, ele grava `.git-ai.toml` e mostra as variaveis de ambiente que voce precisa configurar.

## Configuracao

Todas as opcoes em `.git-ai.toml`:

```toml
[git-ai]
# Provider de IA: 'anthropic', 'openai' ou 'claude-code'
provider = "anthropic"

# Override do modelo de IA (vazio = padrao do provider)
# Exemplos: 'claude-sonnet-4-5-20250929', 'gpt-4o', etc.
# model = "claude-sonnet-4-5-20250929"

# Idioma para mensagens de commit e entradas do changelog
# Suportados: 'en', 'pt-BR', 'es', 'fr', 'de', 'it', 'ja', 'ko', 'zh'
language = "en"

# Escopos de commit permitidos (vazio = qualquer escopo permitido)
# A IA so usara escopos desta lista
# Exemplo: ["auth", "api", "ui", "database", "config"]
scopes = []

# Tipos de commit permitidos (vazio = todos os tipos Conventional Commits)
# A IA so usara tipos desta lista
# Exemplo: ["feat", "fix", "docs", "refactor", "test"]
types = []

# Tamanho maximo do diff enviado a IA (em caracteres)
# Diffs maiores que isso sao truncados com um aviso
max_diff_size = 15000

[git-ai.commit]
# Comportamento do body: 'auto' (IA decide), 'always' (IA deve incluir), 'never' (removido da saida)
body = "auto"

[git-ai.commit.footer]
# Se deve incluir o footer BREAKING CHANGE quando aplicavel
breaking_change = true

# Se deve incluir um trailer "Co-Authored-By" nas mensagens de commit
# Defina como false para evitar linhas de atribuicao da IA nos commits
co_authored_by = false

# Linhas de footer customizadas para adicionar a cada mensagem de commit
# Exemplo: ["Signed-off-by: Nome <email@example.com>"]
lines = []

[git-ai.templates]
# Template padrao (vazio = sem template, usa configuracoes do 'commit' diretamente)
# default = "minimal"

# Definicoes de templates customizados
# [git-ai.templates.presets.meu-time]
# body = "always"
# breaking_change = true
# co_authored_by = false
# lines = ["Signed-off-by: Time <time@example.com>"]

[git-ai.changelog]
# Caminho do arquivo relativo a raiz do projeto
path = "CHANGELOG.md"

# Incluir emojis nos titulos das secoes (ex: "### ✨ Features")
with_emojis = true

[git-ai.hook]
# Se o hook de validacao commit-msg esta habilitado
enabled = false

# Quando true, rejeita commits nao-convencionais
# Quando false, apenas exibe um aviso
strict = true
```

### Variaveis de ambiente

| Variavel | Descricao | Padrao |
|----------|-----------|--------|
| `GIT_AI_PROVIDER` | Provider de IA (`anthropic`, `openai`, `claude-code`) | `anthropic` |
| `GIT_AI_MODEL` | Override do modelo de IA | Padrao do provider |
| `GIT_AI_LANGUAGE` | Idioma das mensagens de commit | `en` |
| `GIT_AI_MAX_DIFF_SIZE` | Tamanho maximo do diff em caracteres | `15000` |
| `GIT_AI_COMMIT_BODY` | Comportamento do body (`auto`, `always`, `never`) | `auto` |
| `GIT_AI_CO_AUTHORED_BY` | Incluir trailer Co-Authored-By | `false` |
| `GIT_AI_TEMPLATE` | Nome do template de commit padrao | -- |
| `ANTHROPIC_API_KEY` | Chave da API Anthropic (quando provider e `anthropic`) | -- |
| `OPENAI_API_KEY` | Chave da API OpenAI (quando provider e `openai`) | -- |

## Templates de Commit

Templates agrupam preferencias de body e footer em presets nomeados. Sao totalmente opcionais -- sem um template, a secao `commit` do config e usada diretamente.

### Templates built-in

| Template | Body | Footer BREAKING CHANGE | Caso de uso |
|----------|------|----------------------|-------------|
| `minimal` | Nunca | Nao | Commits rapidos de uma linha |
| `detailed` | Sempre | Sim | Commits completos com contexto total |

### Usando templates

```bash
# Usar um template built-in
git-ai commit --template minimal

# Sobrescrever body na hora
git-ai commit --no-body

# Adicionar footers customizados
git-ai commit --footer "Signed-off-by: Nome <email>"
git-ai commit --footer "Reviewed-by: Alice" --footer "Tested-by: Bob"

# Combinar opcoes
git-ai commit --template detailed --footer "Signed-off-by: Time <time@example.com>"
```

### Definir um template padrao

Via variavel de ambiente:

```bash
export GIT_AI_TEMPLATE=minimal
```

Ou em `.git-ai.toml`:

```toml
[git-ai.templates]
default = "minimal"
```

### Desativando Co-Authored-By

Por padrao, o trailer `Co-Authored-By` **nao** e incluido nas mensagens de commit. Se voce quiser habilitar:

```toml
# .git-ai.toml
[git-ai.commit.footer]
co_authored_by = true
```

Ou via variavel de ambiente:

```bash
export GIT_AI_CO_AUTHORED_BY=true
```

Quando habilitado, commits incluirao um trailer como:

```
Co-Authored-By: Claude <noreply@anthropic.com>
```

Defina como `false` (padrao) para manter commits limpos sem atribuicao da IA.

## Git Hook

A ferramenta inclui um hook `commit-msg` opcional que valida mensagens de commit contra a especificacao Conventional Commits.

**O que ele valida:**

- A mensagem deve seguir o formato: `<type>(<scope>): <description>`
- O tipo deve ser um de: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`
- A primeira linha nao pode exceder 72 caracteres
- Merge commits, reverts, fixups e squashes sao permitidos automaticamente

**Instalar o hook:**

```bash
# Via wizard de setup
git-ai setup

# Ou copie manualmente o arquivo do hook
cp hooks/commit-msg .git/hooks/commit-msg
chmod +x .git/hooks/commit-msg
```

**Exemplo de commit rejeitado:**

```
$ git commit -m "atualizei coisas"

Invalid commit message format!

Your message:
  atualizei coisas

Expected format:
  <type>(<scope>): <description>

Valid types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert

Examples:
  feat(auth): add OAuth2 login support
  fix: resolve null pointer in user service
  docs(readme): update installation instructions

Tip: Use 'git-ai commit' to generate valid messages automatically.
```

## Conventional Commits

Esta ferramenta segue a especificacao [Conventional Commits v1.0.0](https://www.conventionalcommits.org/pt-br/v1.0.0/):

```
<tipo>(<escopo>): <descricao>

[corpo opcional]

[rodape(s) opcional(is)]
```

### Tipos suportados

| Tipo | Emoji | Descricao |
|------|-------|-----------|
| `feat` | ✨ | Uma nova funcionalidade |
| `fix` | 🐛 | Correcao de bug |
| `docs` | 📚 | Mudancas apenas na documentacao |
| `style` | 💎 | Mudancas de estilo de codigo (formatacao, ponto e virgula, etc.) |
| `refactor` | ♻️ | Refatoracao de codigo (sem funcionalidade ou correcao) |
| `perf` | ⚡ | Melhorias de performance |
| `test` | 🧪 | Adicao ou correcao de testes |
| `build` | 📦 | Mudancas no sistema de build ou dependencias |
| `ci` | 🔧 | Mudancas na configuracao de CI |
| `chore` | 🔨 | Outras mudancas (ferramentas, configs, etc.) |
| `revert` | ⏪ | Reverte um commit anterior |

### Breaking changes

Breaking changes sao indicadas por:

- Um `!` apos o tipo/escopo: `feat(api)!: remover endpoints depreciados`
- Um rodape `BREAKING CHANGE:` no corpo

A IA detecta breaking changes automaticamente a partir do diff e define `is_breaking_change` de acordo.

## Arquitetura

A ferramenta usa uma camada de abstracao de servico (contrato `AiService`) que permite trocar entre providers sem mudar a logica dos comandos:

- **`AnthropicAiService`** -- Usa o SDK da Anthropic com saida estruturada para a API da Anthropic
- **`OpenAiService`** -- Usa o SDK da OpenAI para a API da OpenAI
- **`ClaudeCodeAiService`** -- Invoca o CLI `claude` como subprocesso para usuarios com assinatura Claude

O provider e resolvido em tempo de execucao baseado na configuracao `provider` em `.git-ai.toml`. Todas as implementacoes retornam o mesmo formato de dict estruturado, garantindo comportamento consistente independente do provider.

## Desenvolvimento

```bash
# Clone e setup
git clone https://github.com/tharlesamaro/python-git-ai.git
cd python-git-ai
uv sync

# Executar testes
uv run pytest

# Formatacao e lint
uv run ruff format src tests
uv run ruff check src tests

# Type checking
uv run mypy src

# Executar testes com Docker
docker compose run --rm test
```

## Contribuindo

Contribuicoes sao bem-vindas! Por favor, siga Conventional Commits para suas mensagens de commit.

1. Fork o repositorio
2. Crie sua branch de feature (`git checkout -b feat/funcionalidade-incrivel`)
3. Faca commit das suas mudancas (`git-ai commit`)
4. Faca push para a branch (`git push origin feat/funcionalidade-incrivel`)
5. Abra um Pull Request

## Licenca

Licenca MIT (MIT). Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
