# AUTOMAÇÃO DE LEADS — Manual de Integrações e Providers

Este documento explica a arquitetura de providers do sistema e como alternar entre o modo simulado (mocks) e futuros adaptadores de APIs reais de produção.

---

## 🔌 Estrutura de Providers

A arquitetura foi refatorada de modo a isolar as integrações em adapters intercambiáveis dentro do diretório [`backend/src/providers/`](file:///c:/Users/55119/OneDrive/Documentos/AUTOMA%C3%87%C3%83O%20DE%20DIAGNOSTICO/backend/src/providers). 

Cada categoria de integração possui:
1. `mock.js`: Implementação local que simula a API gerando dados plausíveis offline.
2. `index.js`: Fábrica que avalia as variáveis de ambiente e exporta o provider selecionado.
3. Arquivos adaptadores específicos (e.g. `apify.js`, `google.js`, `gemini.js`): Esqueletos preparados para a implementação de requisições de rede reais.

---

## ⚙️ Como Alterar os Providers

A seleção dos providers é feita modificando as variáveis correspondentes no arquivo [`.env`](file:///c:/Users/55119/OneDrive/Documentos/AUTOMA%C3%87%C3%83O%20DE%20DIAGNOSTICO/backend/.env) na raiz do backend:

```ini
# Configuração de Prospecção de Leads Locais
# Valores válidos: mock | apify | outscraper
LEAD_PROVIDER=mock

# Configuração de Análise de Performance de Sites
# Valores válidos: mock | google
PAGESPEED_PROVIDER=mock

# Configuração de Varredura de Redes Sociais
# Valores válidos: mock | basic
SOCIAL_PROVIDER=mock

# Configuração de Geração de Diagnóstico
# Valores válidos: mock | gemini
AI_PROVIDER=mock
```

Ao iniciar o servidor, o console logs exibirá qual adapter está carregado para cada serviço:
```text
🔌 Lead Provider carregado: MOCK
🔌 PageSpeed Provider carregado: MOCK
🔌 Social Provider carregado: MOCK
🔌 AI Provider carregado: MOCK
```

---

## 🛠️ Detalhes de Cada Categoria

### 1. Leads (`LEAD_PROVIDER`)
* **`mock`:** Retorna imediatamente entre 12 a 15 empresas locais simuladas de acordo com o nicho inserido.
* **`apify`:** (Esqueleto) Loga a chamada e direciona para o mock, preparado para integrar com o *Google Maps Scraper Task* via REST API do Apify.
* **`outscraper`:** (Esqueleto) Loga a chamada e direciona para o mock, preparado para integrar com o serviço de mapeamento comercial da Outscraper.

### 2. PageSpeed (`PAGESPEED_PROVIDER`)
* **`mock`:** Retorna dados de Core Web Vitals (LCP, INP, CLS) e score probabilísticos calculados offline.
* **`google`:** (Esqueleto) Loga a URL analisada e delega ao mock, preparado para fazer o request real de performance à *Google PageSpeed Insights API*.

### 3. Social (`SOCIAL_PROVIDER`)
* **`basic`:** (Esqueleto) Prepared para extrair links do Facebook/Instagram do website do lead ou de enriquecedores sociais.

### 4. AI (`AI_PROVIDER`)
* **`gemini`:** (Esqueleto) Prepared para receber as chaves e estruturar o payload com o SDK oficial da API do Gemini (`@google/generative-ai`), processando prompts de diagnóstico em formato JSON.
