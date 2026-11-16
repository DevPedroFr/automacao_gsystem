# Guia de Onboarding para Desenvolvedores 🚀

Bem-vindo ao projeto **Automação de Leads**! Este guia foi feito para que o seu "Primeiro Dia" seja o mais rápido e indolor possível. Siga os passos abaixo para preparar a sua máquina.

## 🛠️ 1. Pré-requisitos de Instalação
Certifique-se de ter as seguintes ferramentas instaladas na sua máquina local:
- [Node.js](https://nodejs.org/en/) (Versão 18 ou 20+ recomendada)
- [Git](https://git-scm.com/) (Para versionamento de código)
- [Visual Studio Code](https://code.visualstudio.com/) (Editor oficial do projeto)

### Extensões Recomendadas (VS Code)
- **ESLint:** Para verificação de erros e padronização do código.
- **Prettier:** Para formatação automática.
- **Tailwind CSS IntelliSense:** Indispensável para o auto-complete das classes no frontend e nas landing pages.
- **SQLite Viewer:** Para inspecionar rapidamente o arquivo de banco de dados (`database.sqlite`) no backend.

---

## ⚙️ 2. Configuração do Backend
O backend utiliza um banco de dados SQLite local, então não há necessidade de subir containeres Docker ou instalar Postgres localmente. Tudo funciona "Out-of-the-Box".

1. Navegue até a pasta do backend:
   ```bash
   cd backend
   ```
2. Instale as dependências:
   ```bash
   npm install
   ```
3. **Variáveis de Ambiente:** Existe um arquivo `.env.example`. Você precisa duplicá-lo e renomeá-lo para `.env`.
   - Se você estiver rodando apenas para visualizar o painel, não precisa preencher as chaves de API pagas.
   - O banco `database.sqlite` já está pré-criado na raiz do `/backend` com a estrutura das tabelas pronta (sem necessidade de rodar migrations complexas inicialmente).
4. Inicialize o servidor:
   ```bash
   npm run dev
   ```

---

## 🎨 3. Configuração do Frontend
O frontend é construído em Next.js (App Router). 

1. Em um terminal separado, navegue até a pasta do frontend:
   ```bash
   cd frontend
   ```
2. Instale as dependências:
   ```bash
   npm install
   ```
3. Inicialize o painel:
   ```bash
   npm run dev
   ```

O painel abrirá em [http://localhost:3000](http://localhost:3000). Caso o backend não esteja rodando (porta 3001), você verá erros de fetch na tela inicial. Portanto, mantenha sempre os dois terminais abertos.

---

## 🏗️ 4. Padrões de Código e Stack

- **Sem CSS customizado solto:** Toda a estilização deve ser feita através de classes do **Tailwind CSS**. Não crie arquivos `.css` avulsos, exceto o `globals.css` principal.
- **Componentização:** Se um botão ou card for usado mais de duas vezes, crie um componente dentro de `components/ui/` no frontend.
- **Comunicação de API:** Sempre utilize o `fetchApi` contido no arquivo `frontend/lib/api.js` para fazer requisições. Ele já lida com o formato base da URL do servidor.

Se precisar entender mais sobre como as pastas estão divididas e o fluxo das informações (ex: como o Worker assíncrono processa os Leads), por favor leia a documentação [ARCHITECTURE_CURRENT.md](./ARCHITECTURE_CURRENT.md).

Bora codar! 💻
