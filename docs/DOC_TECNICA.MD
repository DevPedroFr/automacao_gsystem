# 🤖 Automação APD — Justificativa Técnica

> Documento de referência técnica do projeto **Automação APD**. Registra o racional por trás de cada escolha de stack e de API, amarrando as decisões às responsabilidades técnicas de Pedro definidas no Acordo de Ciência e Alinhamento (cláusula 8) e à avaliação técnica/orçamentária do piloto.

## 📑 Sumário

- [1. Visão geral do fluxo](#1-visão-geral-do-fluxo)
- [2. Stack de backend e por que cada peça foi escolhida](#2-stack-de-backend-e-por-que-cada-peça-foi-escolhida)
- [3. APIs externas por etapa e justificativa](#3-apis-externas-por-etapa-e-justificativa)
- [4. Relação com as responsabilidades técnicas de Pedro](#4-relação-com-as-responsabilidades-técnicas-de-pedro-cláusula-8)
- [5. Riscos técnicos reconhecidos](#5-riscos-técnicos-reconhecidos)
- [6. Custo estimado de infraestrutura](#6-custo-estimado-de-infraestrutura)
- [7. Próximos passos técnicos](#7-próximos-passos-técnicos)

---

## 1. Visão geral do fluxo

O sistema executa cinco etapas em sequência:

1. Busca de leads a partir de palavras-chave e localização.
2. Triagem automática da presença digital (site, Instagram, SSL/domínio).
3. Geração de diagnóstico e recomendações.
4. Geração de um prompt estruturado para o Google Stitch.
5. Geração do site pelo Stitch.

Cada escolha de stack e de API abaixo existe para sustentar esse fluxo dentro do escopo do piloto (MVP, prazo até 31/08/2026), sem sobre-engenharia.

```
Busca de leads → Triagem digital → Diagnóstico/Recomendações → Prompt Stitch → Geração do site
   (Places API)      (site/IG/SSL)         (Claude API)         (Claude API)     (Stitch API)
```

---

## 2. Stack de backend e por que cada peça foi escolhida

| Componente | Papel no sistema | Justificativa |
|---|---|---|
| **Python** | Linguagem principal de toda a lógica de negócio | Alinhado ao stack em que Pedro programa exclusivamente; reduz risco de retrabalho e mantém uma única linguagem para API, filas, scraping e integrações. |
| **FastAPI** | API e painel de controle (disparo manual do prompt do Stitch) | Framework Python leve, assíncrono nativo (bom para chamadas de I/O como APIs externas), com geração automática de documentação — útil para o painel que Gianmarco vai operar. |
| **PostgreSQL** | Armazenamento de leads, triagens, diagnósticos e status | Banco relacional maduro, com bom suporte a JSON para dados semiestruturados (respostas de API) e forte garantia de integridade — importante para evitar duplicidade de leads, exigência explícita do acordo (cláusula 4 e 8). |
| **Celery + Redis** | Filas assíncronas e agendamento (Celery Beat) | As etapas do fluxo (busca, triagem, chamadas de IA) são operações de I/O que não devem bloquear a API; filas permitem reprocessamento, retry e agendamento de buscas periódicas sem acoplar tudo a um único processo. Uso condicionado à confirmação de necessidade real no MVP (cláusula 5). |
| **httpx / requests** | Cliente HTTP para todas as integrações externas | Biblioteca padrão do ecossistema Python para chamadas HTTP; `httpx` foi indicado por suportar chamadas assíncronas, compatíveis com FastAPI. |
| **Playwright (fallback pontual)** | Coleta de dados não cobertos por nenhuma API | Usado apenas como exceção, nunca como regra — reduz risco de bloqueio/banimento e mantém a arquitetura baseada em APIs oficiais sempre que possível. Só é acionado após aprovação, conforme cláusula 15 do acordo. |
| **Docker + EasyPanel + VPS** | Deploy e operação 24/7 | Permite deploy contínuo a partir do Git compartilhado (exigência da cláusula 5 — acesso de ambas as partes), isolamento de serviços (API, banco, filas) em containers, e operação de baixo custo (~R$ 43/mês de VPS). |

---

## 3. APIs externas por etapa e justificativa

| Etapa | API escolhida | Por que essa escolha | Custo de referência |
|---|---|---|---|
| 1. Busca de leads | Google Places API (New) — Text Search Pro + Place Details | Fonte primária estruturada de estabelecimentos por palavra-chave e localização, com SLA da Google; evita depender de scraping como fonte principal. | Dentro do limite gratuito mensal para o volume estimado (30–150 leads/mês) |
| 2. Triagem — site | Google PageSpeed Insights API | Gratuita, mede velocidade, SEO básico e mobile-friendliness — dado objetivo para embasar a recomendação, sem custo de API. | Gratuito (até 25 mil req/dia) |
| 2. Triagem — SSL/domínio | Verificação própria em Python (`ssl`, `socket`, `whois`) | Não depende de terceiros, roda na própria VPS, sem custo por chamada. | Gratuito |
| 2. Triagem — Instagram | Meta Graph API (Business Discovery) + fallback pago (ex. ScrapeCreators/RapidAPI) | Business Discovery é oficial e gratuita, mas só alcança perfis Business/Creator; o fallback cobre os demais perfis sem violar limites da Meta. | Gratuito (oficial) + US$ 0,003–0,01/perfil (fallback) |
| 3. Diagnóstico e recomendações | Claude API (Anthropic) — Haiku 4.5 | Custo baixo por lead, adequado para classificação/resumo em lote a partir dos dados já coletados. | US$ 1,00/MTok entrada, US$ 5,00/MTok saída |
| 4. Prompt para o site | Claude API (mesmo modelo) | Reaproveita a mesma triagem para gerar um prompt estruturado para o Stitch, sem custo adicional relevante. | Incluso no item acima |
| 5. Geração do site | Google Stitch API/SDK oficial | Único serviço com API oficial hoje para gerar UI/site a partir de prompt; gratuito enquanto estiver em beta (Google Labs). | Gratuito hoje — **sem plano pago definido** |

> Valores levantados em julho/2026; APIs de terceiros reajustam sem aviso prévio — revisão recomendada a cada 3–6 meses (conforme cláusula 16 do acordo).

---

## 4. Relação com as responsabilidades técnicas de Pedro (cláusula 8)

A arquitetura acima foi desenhada para cobrir, ponto a ponto, as obrigações técnicas de Pedro no acordo:

- **Arquitetura adequada ao estágio do projeto** → stack enxuto (FastAPI + PostgreSQL + Celery/Redis), sem serviços desnecessários para um MVP.
- **Banco de dados, filas, backend e integrações** → PostgreSQL para persistência, Celery/Redis para filas, httpx para integrações.
- **Conexões com APIs aprovadas e fallbacks autorizados** → cada etapa tem uma API primária gratuita/barata e, quando necessário, um fallback pago explicitamente sinalizado (Instagram e, potencialmente, Stitch).
- **Validações, tratamento de erros, logs, prevenção de duplicidades** → responsabilidade coberta pelo desenho do PostgreSQL com constraints e pela camada de filas (retry/erro no Celery).
- **Apoio ao deploy e configuração da VPS/EasyPanel** → Docker + EasyPanel escolhidos justamente por permitir deploy contínuo simples a partir do Git compartilhado.
- **Alertas de orçamento** → todas as APIs pagas (Instagram fallback, Claude API, e Stitch caso monetize) devem ter budget alert configurado no provedor antes de produção — mitigação direta do risco de loop/bug gerar custo descontrolado.
- **Comunicação de riscos e mudanças de custo** → riscos técnicos já mapeados na seção 5 abaixo, para acompanhamento contínuo nas reuniões semanais.

---

## 5. Riscos técnicos reconhecidos

- **Google Stitch**: gratuito apenas em fase beta, sem SLA e sem plano pago anunciado — maior risco de custo futuro do projeto.
- **Instagram**: não existe API oficial para qualquer perfil público; Business Discovery cobre só contas Business/Creator, exigindo fallback pago para cobertura completa.
- **Google Places API**: cobrança por campo solicitado (SKU) — pedir apenas os campos essenciais evita faixas de preço mais caras.
- **Dependência de serviços externos** (Google Stitch, Google Places, Meta, Anthropic, provedores de scraping): qualquer um pode mudar preço, limite ou disponibilidade sem aviso — mitigação via fallback, redução de escopo ou substituição de ferramenta, decidida em conjunto.

---

## 6. Custo estimado de infraestrutura

| Item | Recomendação | Custo mensal |
|---|---|---|
| VPS | Hostinger VPS (suporta FastAPI + PostgreSQL + Redis + Celery) | R$ 42,99 |
| EasyPanel | Painel de gerenciamento conectado ao Git | Incluso no valor acima |
| **Total estimado (com APIs)** | 30–150 leads/mês, já com margem de segurança | **R$ 200 a R$ 300/mês** |

---

## 7. Próximos passos técnicos

- [ ] Criar contas e chaves de API (Google Cloud, Meta Developers, Anthropic Console, Stitch)
- [ ] Provisionar VPS e instalar EasyPanel
- [ ] Implementar busca + triagem (etapas 1 e 2) e validar qualidade dos dados
- [ ] Plugar geração de recomendações e fluxo do Stitch
- [ ] Configurar alertas de orçamento em cada provedor antes de produção

---

<sub>Última atualização: julho/2026 · Referência de custos e limites de API sujeita a revisão a cada 3–6 meses.</sub>