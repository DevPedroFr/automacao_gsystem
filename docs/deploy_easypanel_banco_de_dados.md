# 🚀 Guia de Deploy e Configuração de Banco de Dados no Easypanel

Este guia explica qual banco de dados utilizar, como provisioná-lo com 1 clique no **Easypanel**, como conectar o **Backend Python (FastAPI)** e como configurar o **Frontend (Next.js)** para encerrar o uso de arquivos locais (`database.sqlite`) e operar em ambiente de produção escalável.

---

## 1. Qual Banco de Dados Escolher?

O banco recomendado e padrão para o projeto é o **PostgreSQL**:
- **Compatibilidade Nativa:** Totalmente integrado com o SQLAlchemy e FastAPI (`psycopg2-binary`).
- **Nativo no Easypanel:** Provisionamento com 1 clique, com backups e isolamento por container Docker.
- **Transacional e Robusto:** Suporta concorrência real para processamento de múltiplos leads e campanhas simultâneas.

> 💡 **Nota de Compatibilidade:** O código do backend já foi preparado para detectar automaticamente:
> - Se `DATABASE_URL` for informada no `.env` (PostgreSQL), ele conecta ao banco do Easypanel.
> - Se não houver `DATABASE_URL` (desenvolvimento local sem Docker), ele usa o `database.sqlite` como fallback automático.

---

## 2. Passo a Passo de Configuração no Easypanel

### Passo 1: Criar o Projeto no Easypanel
1. Acesse o painel do seu Easypanel.
2. Clique em **+ New Project** (ou selecione seu projeto existente, ex: `automacao-gp`).

---

### Passo 2: Provisionar o Banco de Dados PostgreSQL (1 Clique)
1. Dentro do projeto no Easypanel, clique em **+ Service**.
2. Na aba **Databases**, selecione **PostgreSQL**.
3. Defina as configurações básicas:
   - **Service Name:** `postgres` (ou `database`)
   - **Database Name:** `automacao_gp`
   - **User:** `postgres`
   - **Password:** Escolha uma senha forte (ou use a gerada automaticamente).
4. Clique em **Create**.
5. O Easypanel criará o container do PostgreSQL e disponibilizará a URL de conexão interna.

> 📌 **Como obter a URL de conexão no Easypanel:**
> Dentro do serviço `postgres` que você acabou de criar:
> - Vá na aba **Connection** (ou **Environment**).
> - Você verá a variável de conexão interna:
>   `postgresql://postgres:SUA_SENHA@postgres:5432/automacao_gp`

---

### Passo 3: Deploy do Backend Python (FastAPI)
1. No mesmo projeto do Easypanel, clique em **+ Service** > **App**.
2. **Service Name:** `backend` (ou `api`)
3. **Source (Código-fonte):**
   - Conecte seu repositório GitHub (`automacao_gp` ou similar).
   - **Root Directory:** `/backend_python` (onde está o `Dockerfile` e `requirements.txt`).
   - **Build Type:** Selecione `Dockerfile` (o Easypanel usará o `Dockerfile` otimizado já existente).
4. **Environment Variables (Variáveis de Ambiente):**
   Vá na aba **Environment** do serviço `backend` e adicione:

```env
# Banco de dados PostgreSQL (Conexão interna do Easypanel)
DATABASE_URL=postgresql://postgres:SUA_SENHA@postgres:5432/automacao_gp

# Porta do FastAPI
PORT=8000
DEBUG=False

# Chaves das APIs (Preencha com suas chaves de produção)
GOOGLE_PLACES_API_KEY=AIzaSy...
GOOGLE_PAGESPEED_API_KEY=
META_GRAPH_ACCESS_TOKEN=EAAZAW...
META_INSTAGRAM_ACCOUNT_ID=17841437938461200
ANTHROPIC_API_KEY=sk-ant-api03-...
```

5. **Domínio e Porta:**
   - Na aba **Domains**, configure o subdomínio da sua API (ex: `api.seudominio.com.br`).
   - **Container Port:** `8000`.
6. Clique em **Deploy**.

> ✨ **Criação Automática de Tabelas:**  
> Ao iniciar, o backend executa o `init_db()` do SQLAlchemy e cria todas as tabelas (`campaigns`, `leads`, `diagnostics`, `api_call_logs`, `settings`) **automaticamente no PostgreSQL**, sem você precisar rodar nenhum script SQL manual!

---

### Passo 4: Deploy do Frontend (Next.js)
1. No mesmo projeto do Easypanel, clique em **+ Service** > **App**.
2. **Service Name:** `frontend` (ou `web`)
3. **Source:**
   - Mesmo repositório GitHub.
   - **Root Directory:** `/frontend`
   - **Build Type:** `Nixpacks` ou `NodeJS` (Node 18 ou 20).
4. **Environment Variables:**
   - Adicione a URL pública do seu backend:
```env
NEXT_PUBLIC_API_URL=https://api.seudominio.com.br/api
```
   - Como essa variável é pública e é embutida pelo Next.js durante `next build`, ela precisa estar disponível também na etapa de build da imagem. Se usar o `frontend/Dockerfile`, configure-a como build argument `NEXT_PUBLIC_API_URL`; definir somente uma variável de runtime não altera o bundle já compilado.
5. **Domínio e Porta:**
   - Na aba **Domains**, configure o domínio principal do painel (ex: `app.seudominio.com.br`).
   - **Container Port:** `3000`.
6. Clique em **Deploy**.

---

## 3. Checklist Pré-Lançamento

- [x] O código do backend suporta `DATABASE_URL` dinâmica com fallback para SQLite.
- [x] Driver `psycopg2-binary` incluído no `requirements.txt`.
- [x] `Dockerfile` do backend configurado e exposto na porta `8000`.
- [x] Criação automática de tabelas (`init_db`) no evento de startup do FastAPI.
- [x] Frontend configurado para consumir a variável `NEXT_PUBLIC_API_URL`.
