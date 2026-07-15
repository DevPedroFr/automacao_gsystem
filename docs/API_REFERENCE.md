# CONSULTINGS APD AUTOMATION — Referência da API REST

A API do backend é estruturada sobre o Node.js e o Express. Por padrão, a API é exposta na porta `3001` (configurável via variável de ambiente `PORT` no arquivo `.env`) e todos os endpoints respondem sob o prefixo `/api`. 

Todas as respostas JSON bem-sucedidas são envelopadas em um objeto `{ data: ... }` para manter a consistência de dados no cliente frontend.

---

## 📌 Tabela Resumo de Endpoints

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| **GET** | `/api/campaigns` | Lista todas as campanhas criadas. |
| **GET** | `/api/campaigns/:id` | Detalhes de uma campanha específica. |
| **POST** | `/api/campaigns` | Cria uma campanha e dispara varredura assíncrona. |
| **GET** | `/api/campaigns/:id/stats` | Estatísticas acumuladas da campanha. |
| **GET** | `/api/campaigns/:campaignId/leads` | Lista leads da campanha com filtros e ordenação. |
| **GET** | `/api/leads/:id` | Detalhes de um lead (incluindo diagnóstico se houver). |
| **GET** | `/api/campaigns/:campaignId/leads/export` | Exporta leads da campanha no formato CSV. |
| **POST** | `/api/leads/:leadId/diagnostic` | Gera e salva o diagnóstico por IA para o lead. |
| **GET** | `/api/leads/:leadId/diagnostic` | Retorna o diagnóstico gerado de um lead. |

---

## 🔍 Detalhes por Endpoint

### 1. Campanhas

#### `GET /api/campaigns`
* **Descrição:** Retorna a lista completa de campanhas em ordem cronológica reversa (mais recente primeiro).
* **Parâmetros:** Nenhum.
* **Resposta de Sucesso (200 OK):**
  ```json
  {
    "data": [
      {
        "id": "741f6d19-96fe-4b6a-a7c8-98ef546b6068",
        "niche": "Clínicas Odontológicas",
        "location": "Curitiba, PR",
        "status": "completed",
        "total_leads": 12,
        "created_at": "2026-06-23T23:00:00.000Z",
        "updated_at": "2026-06-23T23:00:00.000Z"
      }
    ]
  }
  ```
* **Uso no Frontend:** Chamado na Home (`app/page.js`) para alimentar a tabela geral de campanhas.

#### `GET /api/campaigns/:id`
* **Descrição:** Retorna as informações de uma única campanha através do ID informado.
* **Parâmetros:** `id` (parâmetro de URL).
* **Resposta de Sucesso (200 OK):**
  ```json
  {
    "data": {
      "id": "741f6d19-96fe-4b6a-a7c8-98ef546b6068",
      "niche": "Clínicas Odontológicas",
      "location": "Curitiba, PR",
      "status": "completed",
      "total_leads": 12,
      "created_at": "2026-06-23T23:00:00.000Z",
      "updated_at": "2026-06-23T23:00:00.000Z"
    }
  }
  ```
* **Resposta de Erro (404 Not Found):**
  ```json
  { "error": "not_found", "message": "Campanha não encontrada" }
  ```
* **Uso no Frontend:** Usado no detalhamento da campanha (`app/campaigns/[id]/page.js`) para obter o nome do nicho, a localização e controlar o status (polling em caso de status `processing`).

#### `POST /api/campaigns`
* **Descrição:** Cria uma campanha no banco de dados com status inicial `processing` e dispara a rotina assíncrona do Worker em background.
* **Payload (JSON Body):**
  ```json
  {
    "niche": "Clínicas Odontológicas",
    "location": "Curitiba, PR"
  }
  ```
* **Resposta de Sucesso (201 Created):**
  ```json
  {
    "data": {
      "id": "741f6d19-96fe-4b6a-a7c8-98ef546b6068",
      "niche": "Clínicas Odontológicas",
      "location": "Curitiba, PR",
      "status": "processing",
      "total_leads": 0,
      "created_at": "...",
      "updated_at": "..."
    }
  }
  ```
* **Resposta de Erro (400 Bad Request):**
  ```json
  { "error": "validation_error", "message": "Os campos \"niche\" e \"location\" são obrigatórios" }
  ```
* **Uso no Frontend:** Disparado pelo formulário do modal [`NewCampaignModal.js`](file:///c:/Users/55119/OneDrive/Documentos/AUTOMA%C3%87%C3%83O%20DE%20DIAGNOSTICO/frontend/components/campaigns/NewCampaignModal.js).

#### `GET /api/campaigns/:id/stats`
* **Descrição:** Retorna os dados analíticos compilados da campanha para renderização de gráficos.
* **Parâmetros:** `id` (parâmetro de URL).
* **Resposta de Sucesso (200 OK):**
  ```json
  {
    "data": {
      "total_leads": 12,
      "priority_a": 3,
      "priority_b": 6,
      "priority_c": 3,
      "avg_dms": 45.3,
      "avg_cos": 67.8
    }
  }
  ```
* **Uso no Frontend:** Chamado pela Home (`app/page.js`) em loop para cada campanha completed para computar o total de leads gerais, a média de DMS e desenhar o gráfico de prioridades do Dashboard.

---

### 2. Leads

#### `GET /api/campaigns/:campaignId/leads`
* **Descrição:** Retorna a lista de leads gerada pela campanha especificada, permitindo filtros de busca e ordenação.
* **Parâmetros:**
  * `campaignId` (parâmetro de URL).
  * **Query Params (opcionais):**
    - `priority`: Filtro exato por prioridade (`A`, `B`, `C`).
    - `search`: Busca textual parcial e insensível ao caso pelo nome do lead.
    - `sort_by`: Campo de ordenação (`cos`, `dms`, `google_rating`, `name`, `priority`, `google_reviews_count`, `pagespeed_score`, `created_at`). Default: `cos`.
    - `sort_order`: Direção (`ASC` ou `DESC`). Default: `DESC`.
* **Resposta de Sucesso (200 OK):**
  ```json
  {
    "data": [
      {
        "id": "uuid-do-lead",
        "campaign_id": "741f6d19-96fe-4b6a-a7c8-98ef546b6068",
        "name": "Clínica Sorriso & Saúde",
        "category": "clínicas odontológicas",
        "phone": "(41) 98888-7777",
        "website": null,
        "address": "Rua XV de Novembro, 100",
        "city": "Curitiba, PR",
        "google_rating": 4.8,
        "google_reviews_count": 89,
        "has_website": 0,
        "pagespeed_score": null,
        "lcp_ms": null,
        "inp_ms": null,
        "cls": null,
        "has_instagram": 0,
        "has_facebook": 0,
        "social_last_post_days": null,
        "dms": 25,
        "cos": 84,
        "priority": "A",
        "created_at": "..."
      }
    ],
    "total": 1
  }
  ```
* **Uso no Frontend:** Consumido em [`app/campaigns/[id]/page.js`](file:///c:/Users/55119/OneDrive/Documentos/AUTOMA%C3%87%C3%83O%20DE%20DIAGNOSTICO/frontend/app/campaigns/%5Bid%5D/page.js) para popular a tabela interativa de leads daquela campanha específica.

#### `GET /api/leads/:id`
* **Descrição:** Retorna todas as informações detalhadas e scores calculados de um único lead, acoplando o diagnóstico (se houver).
* **Parâmetros:** `id` (parâmetro de URL do lead).
* **Resposta de Sucesso (200 OK):**
  ```json
  {
    "data": {
      "id": "uuid-do-lead",
      "campaign_id": "uuid-da-campanha",
      "name": "Clínica Sorriso & Saúde",
      "...outrosCamposLeads": "...",
      "diagnostic": null // ou Objeto Diagnóstico se já gerado
    }
  }
  ```
* **Uso no Frontend:** Chamado pela tela de detalhe de lead (`app/leads/[id]/page.js`) para alimentar os cards de PageSpeed, Google Rating, e Core Web Vitals.

#### `GET /api/campaigns/:campaignId/leads/export`
* **Descrição:** Retorna os leads formatados como arquivo CSV para download direto.
* **Parâmetros:** `campaignId` (parâmetro de URL).
* **Resposta de Sucesso (200 OK):**
  * Cabeçalho HTTP: `Content-Type: text/csv; charset=utf-8`
  * Corpo: Texto bruto no formato CSV separado por vírgulas e com delimitadores de string de aspas duplas.
* **Uso no Frontend:** Acelerador de exportação acionado pelo botão "Exportar CSV" na tela da campanha.

---

### 3. Diagnósticos

#### `POST /api/leads/:leadId/diagnostic`
* **Descrição:** Inicia o gerador de diagnóstico (atualmente mockado via IA) para analisar os gaps do lead, criando e salvando os textos formatados em banco.
* **Parâmetros:** `leadId` (parâmetro de URL).
* **Resposta de Sucesso (201 Created):**
  ```json
  {
    "data": {
      "id": "uuid-do-diagnostico",
      "lead_id": "uuid-do-lead",
      "observed_facts": "• Avaliação Google: 4.8...\n• Site: ...",
      "inferences": "...",
      "recommendations": "...",
      "email_draft": "Assunto: ...\nCorpo: ...",
      "generated_at": "..."
    }
  }
  ```
* **Resposta de Erro (409 Conflict):**
  ```json
  { "error": "already_exists", "message": "Diagnóstico já gerado para este lead. Use GET para consultá-lo." }
  ```
* **Uso no Frontend:** Executado pelo botão "Gerar Diagnóstico com IA 🤖" na tela de detalhes do lead (`app/leads/[id]/page.js`).

#### `GET /api/leads/:leadId/diagnostic`
* **Descrição:** Consulta o banco em busca de um diagnóstico pré-gerado para o lead.
* **Parâmetros:** `leadId` (parâmetro de URL).
* **Resposta de Sucesso (200 OK):**
  ```json
  {
    "data": {
      "id": "uuid-do-diagnostico",
      "lead_id": "uuid-do-lead",
      "observed_facts": "...",
      "inferences": "...",
      "recommendations": "...",
      "email_draft": "...",
      "generated_at": "..."
    }
  }
  ```
* **Resposta de Erro (404 Not Found):**
  ```json
  { "error": "not_found", "message": "Diagnóstico ainda não gerado para este lead. Use POST para gerar." }
  ```
* **Uso no Frontend:** Carregado ao montar a página de detalhes do lead para decidir se renderiza as abas de diagnóstico ou se exibe o botão de geração.
