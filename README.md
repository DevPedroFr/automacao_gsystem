# Consultings APD - Automação de Diagnóstico de Presença Digital

Bem-vindo ao monorepo da plataforma **Consultings APD**! 🚀

Este repositório contém todo o ecossistema da nossa plataforma B2B de prospecção consultiva, além dos templates de Landing Pages de alta conversão oferecidos aos nossos clientes como parte do serviço.

## 📁 Estrutura do Monorepo

O projeto está dividido em módulos independentes:

### 1. Sistema Principal (A Plataforma)
- **`/backend`**: Nossa API REST em Node.js com Express e banco de dados local (SQLite). Responsável por varrer o Google Maps e calcular a nota de Presença Digital dos Leads.
- **`/frontend`**: O painel administrativo (Dashboard) em Next.js 14, React 18 e Tailwind CSS. É aqui que geramos os diagnósticos com IA e gerenciamos as campanhas.

### 2. Produtos Entregáveis (Landing Pages)
- **`/mota-tobias-landing`**: Template de site construído em Next.js 16 para o cliente (Nicho Odontológico).
- **`/renata-flora-landing`**: Template de site construído em Next.js 16 para a cliente Renata Flora.

### 3. Documentação
- **`/docs`**: Documentação profunda da arquitetura, fluxo de processos e mapeamento da IA. Recomendamos fortemente a leitura dos arquivos nesta pasta.

---

## 🚀 Como Rodar o Projeto Localmente

Siga os passos abaixo para rodar o sistema no seu computador.

### 1. Rodando o Backend (API)
Abra um terminal e acesse a pasta do backend:
```bash
cd backend
npm install
npm run dev
```
O servidor rodará na porta `3001`.

### 2. Rodando o Frontend (Painel)
Abra um **novo terminal** e acesse a pasta do frontend:
```bash
cd frontend
npm install
npm run dev
```
Acesse o painel em `http://localhost:3000`.

### 3. Rodando uma Landing Page (Opcional)
Se precisar testar ou modificar um dos sites dos clientes:
```bash
cd mota-tobias-landing # ou renata-flora-landing
npm install
npm run dev
```
A Landing Page rodará em `http://localhost:3000` (ou `3002` se a porta 3000 já estiver em uso pelo frontend).

---

## 📖 Primeiros Passos para Novos Desenvolvedores

Se você acabou de chegar no time:
1. Leia o arquivo [PROJECT_OVERVIEW.md](./docs/PROJECT_OVERVIEW.md) para entender as regras de negócio da prospecção e os cálculos (DMS e COS).
2. Leia o arquivo [ONBOARDING.md](./docs/ONBOARDING.md) para as instruções iniciais e setup da máquina.
3. Se precisar entender como o frontend se comunica com o backend, veja [ARCHITECTURE_CURRENT.md](./docs/ARCHITECTURE_CURRENT.md).

Bom código! ☕
