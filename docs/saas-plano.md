# Web3 Job Tailor — Plano SaaS (Roadmap em Fases)

> **Data**: 2026-06-09. **Status**: plano aprovado para Fase 0 (dogfooding); fases
> seguintes condicionadas a gates explícitos.
> **Produto final**: um **currículo profissional** — PDF Tagged/ATS-safe + DOCX,
> bonito, single-column, adaptado à vaga, PT ou EN — **sem inventar experiência**.
> **Base**: pesquisa web 2026-06-09 (3 frentes: mercado, arquitetura/LGPD, render)
> + motor core já commitado (`src/web3_job_tailor/`). Claims marcados
> `[FATO]` (fonte verificada), `[FATO-médio]` (fonte secundária) ou `[DECISÃO/HIPÓTESE]`.
> Pesquisa **não substitui consultoria jurídica**.

---

## 1. Visão e posicionamento

`[DECISÃO]` **"Evidence-grounded resume tailoring"** para profissionais tech/Web3/dados:
*cada bullet do seu CV é rastreável a um fato real do seu histórico — nunca inventamos
experiência*. O traceability report (bullet → fato-fonte) é o artefato de prova, visível
no produto e no marketing.

Por quê esse ângulo:
- `[FATO-médio]` A queixa #1 da categoria é IA genérica/inventada que recrutador detecta
  (74% dizem que IA reduz autenticidade; aiapply.co — estatística agregada por vendor,
  rastrear fonte primária antes de usar em copy).
- `[FATO-médio]` **Nenhum** incumbente (Rezi, Teal, Huntr, Jobscan, Kickresume, Enhancv,
  Careerflow) comercializa anti-alucinação/rastreabilidade como feature central (lacuna
  confirmada por ausência em buscas, não por auditoria exaustiva).
- `[FATO-médio]` Não existe tooling de tailoring dedicado a Web3 — os job boards
  (web3.career, cryptojobslist) só publicam dicas em blog.
- `[DECISÃO]` Web3 é **cunha de entrada** (distribuição via job boards e Superteam),
  não teto — nicho cripto é cíclico; expandir para tech/dados em geral.
- `[DECISÃO]` Segundo wedge: corredor **LATAM→remoto global** com localização PT→EN
  real (cargos, métricas, contexto BR) — superior à tradução genérica do Kickresume
  (8 idiomas, sem grounding).

## 2. Mercado (referência competitiva)

| Player | Free | Pago | Confiança |
|---|---|---|---|
| Rezi | 1 CV, 3 PDFs | US$29/mês; Lifetime US$149 | alta (página oficial) |
| Kickresume | 4 templates | US$19/mês; US$54/ano | alta (oficial) |
| Huntr | 2 tailorings, 100 vagas | US$40/mês | alta (oficial) |
| Teal | tracking ilimitado + ~10 créditos | ~US$29/mês | média (oficial 403; reviews 2026) |
| Jobscan | 5 scans/mês | ~US$49,95/mês | média (SPA; reviews 2026) |
| Enhancv | trial 7d | ~US$19,99/mês | média |
| Careerflow | LinkedIn optimizer | ~US$23,99/mês | média (página 404; reviews) |

`[FATO]` Table stakes da categoria: tailoring por vaga colada, score ATS/keyword,
templates, cover letter IA, free tier. `[DECISÃO]` Não competir como generalista —
categoria saturada.

**Pricing recomendado** `[HIPÓTESE]`: Free = 1 CV-base + 2-3 tailorings/mês;
**Pro US$12-15/mês ou US$79-99/ano** (abaixo de Teal/Rezi/Huntr, acima do piso
commodity); **créditos one-off ~US$9/10 tailorings** (job search é episódica; churn
pós-contratação é estrutural); BR em BRL (R$29-49/mês, Pix); lifetime early-bird
US$99-149 opcional p/ caixa inicial. Validar preços de Teal/Jobscan/Careerflow no
browser antes de usar comparativo público.

## 3. Roadmap em fases (cada fase entrega valor sozinha)

### Fase 0 — Dogfooding polido: render profissional local (~2-4 fins de semana)
**Goal**: o CV do Paulo sai do pipeline com qualidade visual profissional e ele aplica
a vagas reais (BCB Group, Zinnia) com PDF gerado + traceability report.
- Schema canônico do fact store mapeável 1:1 para **JSON Resume v1.0.0** (interop,
  zero lock-in; não usar os temas npm como render).
- **Render PDF via RenderCV como biblioteca** (gerar o YAML dele a partir do fact
  store) — `[FATO]` RenderCV é MIT, 9 temas, e publica relatório ATS: Tagged PDF,
  99,1% extração, aprovado em parsers comerciais Affinda/Extracta/Klippa
  (docs.rendercv.com/ats_compatibility — vendor claim; **reproduzir teste localmente**).
- 2 temas: **EngineeringResumes** (tech denso) + **Classic/Harvard** (conservador/fintech).
- DOCX paralelo (python-docx, já no core) + **traceability report** por CV (bullet → fato).
- CLI fim-a-fim: colar vaga → tailor → PDF + DOCX + report, PT e EN.
- Cada candidatura real = aprovação explícita (protocolo do projeto).

### Fase 1 — MVP web single-user, beta fechado (~4-6 fins de semana)
**Goal**: 10-20 betas convidados (comunidades Web3/dados, Superteam) usam pelo browser, sem billing.
- Monólito **FastAPI + Postgres** já em pool model: `tenant_id` (UUID) em toda tabela
  com PII **desde o dia 1** + índice composto liderado por tenant_id.
- Upload CV → extração (Haiku) → **tela de revisão do fact store** (humano valida) →
  colar vaga → tailoring (Sonnet+judge) → preview → PDF/DOCX.
- **Traceability view na UI**: bullet clicável mostra o fato-fonte (o diferencial visível).
- `[FATO]` Privacidade: CV **inline na Messages API** — Anthropic não treina com
  conteúdo de cliente comercial (Commercial Terms) e retém inputs/outputs por até 30
  dias; **não usar Files/Batch API** para CV (retenção própria, não-ZDR). ZDR existe
  mas exige sales e não cobre Fable 5/Mythos 5 (retenção obrigatória 30d).
- Auth Supabase free (convites); deploy Railway Hobby US$5/mês ou Render ~US$7/mês.

### Fase 2 — Multi-tenant + billing, self-serve pago (~6-10 fins de semana)
**Goal**: estranho cria conta, paga, gera CV e exporta/exclui os próprios dados sozinho.
- **RLS completa**: `ENABLE` + `FORCE ROW LEVEL SECURITY`, app com role **não-owner**
  (`[FATO]` owners ignoram RLS por padrão — postgresql.org/docs ddl-rowsecurity),
  `SET LOCAL app.current_tenant` por transação (compatível com pooling transaction-mode;
  padrão AWS), testes automatizados de isolamento cross-tenant.
- Stack: **Supabase Pro US$25/mês** (Postgres+Auth+Storage, JWT integra RLS) +
  **Stripe BR** (`[FATO]` cartão 3,99%+R$0,39; Pix 1,19%; sem mensalidade) com
  Checkout + Customer Portal e **cancelamento sem fricção** (anti-padrão Teal: 12%
  das reviews 1 estrela por billing pós-cancelamento).
- **LGPD by design**: endpoints "exportar meus dados" e "excluir conta"; minimização
  no fact store (só campos profissionais — CV pode conter dado sensível acidental,
  Art. 11); registro simplificado (Resolução CD/ANPD 2/2022 — dispensa DPO p/ pequeno
  porte, prazos em dobro; NÃO dispensa bases legais); aviso de privacidade nomeando
  Anthropic como suboperador (EUA).
- `[FATO-médio]` **Mudança de base legal**: processando CV de pagantes, Paulo vira
  **CONTROLADOR**; base nuclear = **execução de contrato (LGPD Art. 7, V)**;
  consentimento só para usos acessórios (nunca ancorar o serviço em consentimento
  revogável). Direitos do Art. 18 viram obrigação. *(Art. 7/18 citados do espelho
  lgpd-brasil.info — Planalto recusou conexão; validar no texto oficial.)*
- **GATE OBRIGATÓRIO: revisão com advogado antes do 1º pagante** — maior gap aberto:
  mecanismo de **transferência internacional** (Art. 33+, Resolução ANPD 19/2024)
  para o fluxo CV → Anthropic (EUA).

### Fase 3 — Coleta de vagas integrada, legal-first (~6-8 fins de semana)
**Goal**: fila de vagas compatíveis + CV adaptado em 1 clique. **Zero scraping de LinkedIn, sempre.**
- Conectores **Greenhouse/Lever** (APIs públicas JSON, verificadas na pesquisa da
  arquitetura) + web3.career — cada fonte ativada só após revisão de ToS documentada.
- **Parser de email-alerts do LinkedIn**: usuário encaminha o e-mail ao app.
- Score de match **fato-baseado** com lacunas explícitas ("você não tem evidência de X")
  — diferenciado do keyword score genérico criticado no Jobscan.

## 4. Decisões-chave (resolvidas pela pesquisa)

| Decisão | Escolha |
|---|---|
| Motor de render | **Fase 0: RenderCV-as-library** (dias) → Fases 1-2: 2-4 templates **Typst** próprios (bindings PyPI `typst`, Apache-2.0). HTML/CSS só preview (PDF do Chromium sem garantia Tagged PDF). Evitar LaTeX e react-pdf. Licenças todas permissivas (MIT/Apache/BSD). |
| Multi-tenancy | **Pool model + RLS** (1 Postgres, tenant_id em tudo). Schema/DB-per-tenant rejeitados nesta escala. |
| Auth + hosting | **Supabase** (unifica banco/auth/storage; Auth integra RLS). Custo de entrada ~US$5-30/mês + consumo Anthropic. |
| Privacidade LLM | **Messages API inline** (30d retenção, sem treinamento por contrato). Sem Files/Batch p/ CV. Nunca conta consumer no produto. |
| Monetização | **Híbrido** assinatura + créditos one-off (+ lifetime early-bird opcional). |
| Jurídico | Beta gratuito (Fase 1) = termo de beta + minimização; **advogado é gate da Fase 2**. |

## 5. Riscos principais

1. **Barreira de cópia baixa no posicionamento** — qualquer player copia o marketing;
   a defesa é a implementação (fact store + traceability report público + testes ATS
   próprios). Por isso a Fase 0 produz o **artefato de prova**, não só o PDF.
2. **Churn estrutural** (usuário cancela ao ser contratado) → créditos one-off + anual
   + cancelamento sem fricção como diferencial de confiança.
3. **Gap jurídico**: transferência internacional (Cap. V LGPD) não pesquisada a fundo;
   Art. 7/18 citados de espelho → bloquear Fase 2 até revisão com advogado.
4. **Nicho Web3 cíclico** → cunha, não teto.
5. **Claims de terceiros não auditados** (relatório ATS do RenderCV é vendor claim;
   preços Teal/Jobscan de reviews) → reproduzir/validar antes de material público.
6. **Solo founder com emprego full-time** → cada fase cortável e com valor próprio
   (a Fase 0 já paga o projeto via dogfooding na busca do Paulo).
7. **rendercv.com opera app próprio** (concorrente potencial no mesmo motor) → manter
   rota de saída via templates Typst próprios.
8. **RLS x ORM**: `SET LOCAL` exige disciplina de transação; query sem contexto retorna
   0 linhas (fail-safe que mascara bug) → testes de isolamento obrigatórios.
9. **Dados sensíveis acidentais no CV** (Art. 11) → minimização no fact store desde a Fase 1.

## 6. Fontes principais (acesso 2026-06-09)

- Anthropic: anthropic.com/legal/commercial-terms; privacy.claude.com (retenção 30d);
  platform.claude.com/docs api-and-data-retention (ZDR)
- LGPD: lgpd-brasil.info (espelho — validar no Planalto); gov.br/anpd Resolução CD/ANPD 2/2022
- Postgres RLS: postgresql.org/docs/current/ddl-rowsecurity.html; AWS blog multi-tenant RLS
- Render: github.com/rendercv/rendercv; docs.rendercv.com/ats_compatibility;
  pypi.org/project/typst; jsonresume.org/schema; github.com/Kozea/WeasyPrint
- Pricing concorrentes: rezi.ai/pricing; kickresume.com/en/pricing; huntr.co/pricing
  (oficiais); Teal/Jobscan/Careerflow via reviews 2026 (confiança média)
- Infra: railway.com/pricing; supabase.com/pricing; clerk.com/pricing; stripe.com/br/pricing
