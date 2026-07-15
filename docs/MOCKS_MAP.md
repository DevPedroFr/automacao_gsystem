# CONSULTINGS APD AUTOMATION — Mapa de Mocks vs Realidade

Esta documentação descreve o mapeamento completo dos mocks utilizados no MVP da plataforma, explicando o comportamento atual e as variáveis configuradas para futura integração com APIs de produção.

---

## ⚖️ Mapeamento de Responsabilidades

| Componente | Status Atual | Implementação Atual |
| :--- | :--- | :--- |
| **Banco de Dados** | **Real** | SQLite (através do wrapper sql.js WebAssembly). |
| **Cálculo de DMS/COS** | **Real** | Lógica matemática exata rodando em Node.js. |
| **Rotas e API REST** | **Real** | Express rodando localmente na porta 3001. |
| **Interface e Gráficos** | **Real** | React (Next.js 14) + Tailwind CSS + Recharts. |
| **Busca de Empresas** | **Mock** | Gerador randômico com dicionário de termos nacionais. |
| **Análise de Performance** | **Mock** | Gerador probabilístico correlacionado com o score. |
| **Análise de Redes** | **Mock** | Gerador estatístico baseado na posse de site. |
| **Diagnóstico de IA** | **Mock** | Concatenação de templates lógicos e analíticos. |

---

## 🛠️ Detalhes das Integrações Mockadas

### 1. Busca de Empresas locais (Apify)
* **Arquivo do mock:** [`apifyService.js`](file:///c:/Users/55119/OneDrive/Documentos/AUTOMA%C3%87%C3%83O%20DE%20DIAGNOSTICO/backend/src/services/apifyService.js)
* **Comportamento no MVP:** O mock recebe o nicho (como *clínicas odontológicas* ou *restaurantes*) e a localização. Ele gera um array de 10 a 15 objetos de empresas utilizando pools de nomes adequados ao segmento. A nota do Google Maps é gerada de forma flutuante entre `2.0` e `5.0`, e a contagem de reviews pode ir de `0` a `500`.

### 2. Análise de Performance de Sites (Google PageSpeed API)
* **Arquivo do mock:** [`pagespeedService.js`](file:///c:/Users/55119/OneDrive/Documentos/AUTOMA%C3%87%C3%83O%20DE%20DIAGNOSTICO/backend/src/services/pagespeedService.js)
* **Comportamento no MVP:** Se o lead gerado na busca possui um site (ex: `odontosmile.com.br`), o mock gera métricas do Core Web Vitals. Ele distribui os scores geral de performance em faixas de probabilidade de forma realista (a maioria das pequenas empresas fica na faixa de performance ruim-média de `35` a `70`). Além disso, calcula de forma lógica as métricas de LCP, INP e CLS de forma reversa ao score (um score baixo garante LCP e CLS ruins na resposta).

### 3. Presença em Redes Sociais
* **Arquivo do mock:** [`socialService.js`](file:///c:/Users/55119/OneDrive/Documentos/AUTOMA%C3%87%C3%83O%20DE%20DIAGNOSTICO/backend/src/services/socialService.js)
* **Comportamento no MVP:** O algoritmo simula a análise de presença em mídias digitais. Se a empresa tem site estruturado, ela ganha um bônus de probabilidade de `15%` de possuir redes sociais. Ele atribui `has_instagram` e `has_facebook` como binários (`0` ou `1`) e calcula o tempo decorrido desde o último post de forma randômica de `1` a `180` dias (com `30%` de chance de a empresa ser ativa e ter postado nos últimos 15 dias).

### 4. Diagnóstico Analítico e E-mail (IA)
* **Arquivo do mock:** [`aiService.js`](file:///c:/Users/55119/OneDrive/Documentos/AUTOMA%C3%87%C3%83O%20DE%20DIAGNOSTICO/backend/src/services/aiService.js)
* **Comportamento no MVP:** Ele não chama APIs como OpenAI ou Anthropic. Em vez disso, o mock lê os dados do lead em banco e monta as strings de diagnóstico condicionalmente:
  * Se o lead não possui site, gera um parágrafo detalhando o impacto de não ter uma landing page própria.
  * Se o lead tem site lento (PageSpeed < 50), gera um diagnóstico detalhando o abandono de usuários mobile em razão do LCP alto.
  * Se possui reputação local excelente (avaliação >= 4.0), mas baixa maturidade digital (DMS < 40), infere que há uma desconexão evidente entre a qualidade do atendimento presencial e a atração online.
  * Gera de forma determinística um template de e-mail profissional, inserindo as variáveis do lead de forma fluida.

---

## ⚙️ Variáveis de Ambiente de Integração

O arquivo [`.env`](file:///c:/Users/55119/OneDrive/Documentos/AUTOMA%C3%87%C3%83O%20DE%20DIAGNOSTICO/backend/.env) já possui o chaveador central preparado para a transição futura:

```ini
PORT=3001
FRONTEND_URL=http://localhost:3000
APIF_API_KEY=your_apify_key_here
PAGESPEED_API_KEY=your_pagespeed_key_here
OPENAI_API_KEY=your_openai_key_here
USE_REAL_API=false  # Chaveador central: mude para true para ativar conexões reais
```

A arquitetura do backend é projetada para que, ao alterar `USE_REAL_API` para `true`, os arquivos de serviço possam consultar as variáveis `APIF_API_KEY`, `PAGESPEED_API_KEY` e `OPENAI_API_KEY` para iniciar as chamadas HTTP reais correspondentes sem impactar a assinatura das funções do worker e das rotas.
