# Motor "Web3 Job Tailor" — Método e Lógica (Arquitetura)

> **Status**: design aprovado para construção (pendente decisões de escopo — ver §10).
> **Data**: 2026-06-09.
> **Objetivo**: dado o CV do Paulo (PDF) + uma vaga, produzir um **CV adaptado e
> traduzido (PT/EN) compatível com a descrição da vaga**, sem inventar experiência.
> **Embasamento de técnicas (KB `prompt-engineering-kb`)**: Self-Refine (Madaan et al.
> 2023, arXiv:2303.17651), RAG (`RAG_for_LLMs__A_Survey`), orchestrator-workers +
> prompt chaining (`Anthropic_Building_Effective_Agents`), structured output
> (OpenAI/Anthropic docs). Demais claims = pesquisa web com URL + nível de confiança
> (ver §11). Material técnico/compliance — **não é parecer jurídico**.

---

## 1. Princípio nuclear: FACT STORE imutável (anti-alucinação by design)

Tudo gira em torno de uma **fonte única de verdade**: `cv_master.json` (+ `repos_portfolio.json`),
extraída **uma vez** do CV PDF real e **curada manualmente** pelo Paulo. Nenhum estágio
downstream pode introduzir um fato sem origem rastreável nesse store.

- `[FATO]` Padrão RAG: gerar **só** a partir de contexto recuperado (`RAG_for_LLMs__A_Survey`).
- `[DECISÃO]` O tailoring (estágio 6) **reordena / enfatiza / reescreve** fatos do store
  e **espelha a linguagem da vaga**; **nunca cria** skill, métrica ou nível inexistente.
- `[DECISÃO]` Se não atingir o match-alvo (≥75%) sem inventar → **reportar o gap honestamente**.

### Pré-requisitos do fact store (correções já detectadas no CV atual)
- `[FATO]` `Resume_Paulo_Eduardo_Web3_v2.md` linha 6: GitHub está como `github.com/[SEU_USER]`
  (placeholder) → deve ser `github.com/Pauloeduspbr`. Validação de placeholders é passo obrigatório no export.
- `[FATO]` Email no CV (`paulo_eduardosp@yahoo.com.br`) ≠ email da sessão (`pauloedusp@gmail.com`).
  `[HIPÓTESE]` pode ser contato profissional intencional — **confirmar com o owner**, não auto-corrigir.
- `[FATO]` Métricas reais a priorizar no tailoring: 99.9% uptime (Banco do Brasil), −40% manutenção,
  −60% storage, −50% processamento (Claro); portfolio crypto-data-pipeline (100 coins, 1.74s, 7/7 checks).

---

## 2. Pipeline end-to-end (8 estágios)

Arquitetura **orchestrator-workers + prompt chaining** (`Anthropic_Building_Effective_Agents`).

```
[1] INGEST CV (PDF)      PyMuPDF4LLM -> markdown layout-aware
        v
[2] STRUCTURE            LLM + schema Pydantic -> cv_master.json -> [GATE revisão humana] -> FACT STORE
        v
[3] COLETA DE VAGAS      Greenhouse + Lever (ATS, sem auth) + web3.career + RemoteOK + RSS + agregadores
        |                LinkedIn: SO email-alerts + colagem manual (ZERO scraping)
        v
[4] PARSE JOB            extrai title/hard-skills/soft-skills/anos/knockouts -> normaliza (ESCO/Lightcast)
        v
[5] MATCH & GAP          score 0-100 explicável = 0.30 semantic + 0.30 skill_coverage + 0.40 LLM-judge
        v
[6] TAILOR               RAG-grounded + Self-Refine (gera->critica->refina), NUNCA inventa
        v
[7] TRANSLATE/LOCALIZE   idioma da vaga; glossário DO-NOT-TRANSLATE; localização US determinística
        v
[8] EXPORT ATS-SAFE      single-column DOCX + PDF; QA re-extrai e valida ordem + glossário
```

> **HARD STOP**: submeter candidatura e disparar coleta paga (proxy/Apify) são **outward-facing**
> → exigem aprovação explícita do owner. O motor **gera e exibe**; o **envio é sempre manual**.

---

## 3. Estágio 1-2 — Ingestão e estruturação do CV (PDF → fact store)

| Item | Escolha | Fonte / nota |
|---|---|---|
| Extração de texto | **PyMuPDF4LLM** `to_markdown('cv.pdf')` (ordem multi-coluna + headings) | pymupdf4llm GitHub — **licença AGPL v3** (ok pessoal/OSS; comercial fechado exige licença Artifex) |
| Alternativa MIT/local | **Docling** (IBM, MIT) → markdown/JSON, 100% local, ~97.9% célula em tabelas | docling-project.github.io |
| Alternativa controle fino | **pdfplumber** (MIT, sem OCR, ideal p/ PDF digital) | github.com/jsvine/pdfplumber |
| Fallback layout difícil | PDF direto ao Claude como `DocumentBlock` (vision), mesmo schema | platform.claude.com/docs structured-outputs |
| Estruturação | `client.messages.parse(output_format=Resume)` com **Pydantic v2** | Haiku 4.5 basta p/ CV (fração de centavo) |
| Validators | ordem cronológica, sobreposição de datas (Pydantic só pega tipo/obrigatório) | arXiv 2510.09722 |

`[DECISÃO]` Output do estágio 2 → **GATE de revisão humana** → vira fact store versionado (git/SQLite).

---

## 4. Estágio 3 — Coleta de vagas (fontes ToS-friendly, ZERO scraping LinkedIn)

`[FATO]` Camada mais robusta: empresas Web3/FinTech publicam vagas via **ATS público sem auth**.

| Fonte | Acesso | Status |
|---|---|---|
| **Greenhouse** (espinha dorsal) | `GET boards-api.greenhouse.io/v1/boards/{token}/jobs` (sem auth, JSON) | ✅ verificado (Coinbase ~43 vagas) |
| **Lever** (espinha dorsal) | `GET api.lever.co/v0/postings/{empresa}?mode=json` (traz `salaryRange`, `workplaceType`) | ✅ verificado |
| **web3.career** | API oficial gratuita (registro por email; filtros stack/role/remote) | ✅ confirmar contrato após cadastro |
| **RemoteOK** | `GET remoteok.com/api` (JSON) | ✅ **OBRIGATÓRIO** link follow + atribuição "Remote OK" por linha (termo legal) |
| **CryptoJobsList** | RSS `api.cryptojobslist.com/jobs.rss` (Crawl-delay 1, sem params `utm_/ref=`) | ⚠️ validar filtros empíricamente |
| **Adzuna / USAJobs / Jooble** | APIs licenciadas (free tier / API key) | ✅ alternativa legítima de volume |
| **Blueprint de handlers** | `github.com/wslyvh/useWeb3` (open-source, padrão Greenhouse/Lever/Workable) | referência de implementação |
| ❌ cryptocurrencyjobs.co | robots.txt `ai-train=no` bloqueia ClaudeBot/GPTBot | **excluído** |
| ❌ Wellfound/AngelList | anti-bot ativo, sem API pública viável | **excluído** |
| ⚠️ Superteam Earn | endpoint de listings passou a exigir auth (401) | bounties via UI; confirmar README |

**Schema único de vaga**: `{title, company, description, stack[], salary_min, salary_max, remote, location, url, source, posted_at}`; dedupe por `url+empresa`; persistir; agendar respeitando Crawl-delay.

### LinkedIn — política do projeto (compliance)
`[FATO]` User Agreement §8.2 proíbe scraping/bots ("scrape or copy the Services... profiles and other data").
`[FATO]` hiQ v. LinkedIn **não liberou** scraping: terminou em judgment de **US$500k** + injunção permanente + destruição de dados (settlement dez/2022). CFAA ≠ contrato; ToS aplica por contrato.
`[FATO]` Job Posting API é **partner-only e não aceita novos parceiros** → inviável p/ indivíduo.
`[DECISÃO]` LinkedIn **apenas** via: (a) **job-alerts nativos por email** (até 20 buscas salvas, diário) parseados via Gmail/IMAP com OAuth do próprio Paulo (dado pessoal dele, consentimento próprio); (b) **colagem manual** de URL/descrição para vagas de alto match. **Scraping de LinkedIn = proibido por design.**

Fontes: linkedin.com/legal/user-agreement; privacyworld.blog (hiQ judgment); learn.microsoft.com/linkedin/talent.

---

## 5. Estágio 4 — Parse da vaga (descrição → requisitos estruturados)

- Extrair: **job title exato**, hard skills/ferramentas, soft skills, anos de experiência, **knockouts**
  (work authorization/visto, idioma, certificação, on-call) — `[FATO]` os knockouts são o que **de fato**
  auto-rejeita em Greenhouse/Lever (não há scoring algorítmico de keyword que descarte).
- Normalizar skills: **`ojd-daps-skills`** (Nesta, MIT) → ESCO (~13.890 skills) ou Lightcast (~32k) +
  **dicionário custom crypto/data-eng** (ESCO/Lightcast tem cobertura fraca de termos Web3 recentes).

Fontes: github.com/nestauk/ojd_daps_skills; lightcast.io/open-skills; jobscan.co/blog/greenhouse-ats.

---

## 6. Estágio 5 — Match & Gap (score 0-100 explicável)

`[DECISÃO]` **Híbrido de 3 camadas** (cada uma resolve uma fraqueza da outra):

```
score_final = 0.30 * semantic_score      # cosine de embeddings (CV vs vaga)
            + 0.30 * skill_coverage       # skills_da_vaga_no_fact_store / skills_da_vaga (auditável)
            + 0.40 * llm_judge            # JSON {score, must_haves, gaps, justificativa}
```

- **semantic**: `sentence-transformers` `all-MiniLM-L6-v2` (grátis/local) ou OpenAI `text-embedding-3-small` ($0.02/1M).
- **skill_coverage**: saída direta de `ojd-daps-skills` (gap auditável, sem alucinação).
- **llm_judge**: LLM-as-judge **sempre com justificativa textual**; nunca decisão autônoma final
  (vieses position/verbosity/self-preference conhecidos).
- **Ranking em escala**: retrieval híbrido **BM25 + dense fundidos por RRF (k=60)** → só top-N vai ao judge (economia de tokens).
- **Gates duros**: must-have ausente penaliza; filtro booleano **$100k+ e remote**.
- **Meta**: ≥75% (ref. Jobscan; sucesso comum ≥65%).

`[HIPÓTESE]` Pesos 0.30/0.30/0.40 = recomendação de engenharia → **calibrar com ~10 vagas rotuladas** manualmente antes de confiar no ranking.

Fontes: arXiv 2504.02870 (multi-agente explicável, Pearson 0.84); evidentlyai.com (LLM-as-judge); blog RRF; mdpi 14/4/794.

---

## 7. Estágio 6 — Tailoring (RAG-grounded + Self-Refine) — o coração anti-alucinação

Loop **generate → critique → refine** (Self-Refine, arXiv:2303.17651; crítica inspirada em Constitutional AI, Bai et al.):

1. **GERA** reescrita usando **só o fact store** como contexto (RAG grounding).
2. **CRITICA** verifica:
   - (a) cada claim **rastreia a um fato do store** → senão **bloqueia/flag** p/ revisão humana;
   - (b) match ≥ 75%;
   - (c) cada bullet = **verbo de ação + tarefa + resultado quantificado** (padrão Harvard);
   - (d) **anti-stuffing**: keyword ≤ 2-3x, sem bloco solto, **sem white-text**;
   - (e) job title espelha a vaga **só se verdadeiro** (nunca promover de nível).
3. **REFINA** e repete até aprovar ou N iterações.

Regras concretas de tailoring (sobre fatos reais):
- Espelhar linguagem: `PySpark` → `Apache Spark` se a vaga usar esse termo (legítimo); inserir skill ausente (ilegítimo).
- Reordenar por relevância: bullets/skills que casam com a vaga vão ao topo.
- Seção Skills explícita com hard skills da vaga **que o Paulo realmente possui** (recrutador busca por skill).

Fontes: jobscan.co/blog/ats-resume; tealhq.com (tailoring 6x); careerservices.fas.harvard.edu.

---

## 8. Estágio 7 — Tradução e localização (PT↔EN conforme a vaga)

`[DECISÃO]` **Ordem de ouro**: **tailor → traduzir → localizar**, no idioma-alvo, **sem dupla tradução**.

- **Idioma-alvo**: detectado pela vaga (Web3 remoto $100k+ ≈ EN/US).
- **Tradução via LLM** (Claude preferido: janela longa + alta aderência a glossário) com **glossário YAML versionado**:
  - **DO-NOT-TRANSLATE** (protegidos por **placeholder determinístico**, não só instrução no prompt):
    stacks (`Python, PySpark, Airflow, dbt, Spark, Kafka, AWS, Azure, GCP, BigQuery, Terraform`),
    empresas (`Itau, Banco do Brasil, Natura, Cielo, Claro, Vivo, Enel, Hospital Sirio-Libanes`),
    nome próprio, URLs/repos.
  - **Mapa de cargos** PT→EN (`Engenheiro de Dados Senior → Senior Data Engineer`).
- **Localização US determinística** (Python): remover foto/idade/estado civil/nascimento;
  datas `MM/YYYY`; telefone internacional; 1-2 páginas; voz ativa.
  `[HIPÓTESE]` confirmar **país da empresa** antes — normas EU/UK diferem de US.
- **QA**: validar que cada termo do glossário aparece **intacto** no output.

Fontes: asaptranslate.com; bluente.com; lokalise.com/blog (glossário determinístico); github.com/rockbenben/md-translator.

---

## 9. Estágio 8 — Export ATS-safe + QA

- Renderizar markdown → **DOCX** (legados Taleo/iCIMS parseiam melhor) + **PDF não-escaneado**,
  **single-column**, headings padrão (`Experience/Education/Skills`), **sem** tabelas/colunas/ícones/text-boxes.
- **QA**: re-extrair o texto do output e validar (a) ordem de leitura, (b) glossário intacto,
  (c) cada hard skill aparece ≥1x dentro de bullet com contexto.
- Ferramentas: `python-docx`, `WeasyPrint`/`ReportLab`, re-extração com PyMuPDF/pdfplumber.

`[FATO]` Correção de mito: Greenhouse/Lever **não** auto-rejeitam por score de keyword — ATS-safe serve para
o parser ler certo e o recrutador **humano** priorizar (76,4% começam a busca por skill).

---

## 10. Decisões em aberto (a confirmar antes do build)

| # | Decisão | Recomendação |
|---|---|---|
| D1 | Escopo do MVP / por onde começar | **Núcleo de tailoring** (1-2 + 6-7-8 com colagem manual da vaga) — entrega o "CV compatível" mais rápido |
| D2 | LinkedIn | **email-alerts + colagem manual** (zero scraping) |
| D3 | PII: cloud LLM vs 100% local | **Cloud Anthropic** (próprio CV, consentimento próprio, custo ínfimo); local só se processar CV de terceiros |
| D4 | Persistência/orquestração | **Postgres + Airflow** (vira 4ª peça de portfolio); SQLite+cron p/ MVP rápido |
| D5 | Lib de PDF | **PyMuPDF4LLM** (CV é digital/simples); Docling (MIT) plugável |
| D6 | Modelos por estágio | **Haiku** p/ extração (2,4) + **Sonnet** p/ judge/tailor/tradução (5,6,7); confirmar pricing atual |

---

## 11. Riscos principais + mitigações

1. **Alucinação de experiência (#1, fatal)** → fact store imutável + validador de rastreabilidade + crítico Self-Refine; se não atinge 75% sem inventar, reporta gap.
2. **Violação de ToS / legal** → excluir cryptocurrencyjobs.co/Wellfound; LinkedIn só email+colagem; honrar atribuição RemoteOK e Crawl-delay; ler `/terms` (não só robots.txt) antes de uso recorrente.
3. **Ação outward-facing sem aprovação** → HARD STOP em envio de candidatura e coleta paga.
4. **Fontes instáveis** → cada conector plugável, validado empiricamente, tolerante a falha individual.
5. **Parsing ATS quebrado** → só single-column + QA que re-extrai e valida ordem.
6. **Viés/opacidade do LLM-judge** → só ranking relativo + justificativa; calibrar com ground truth.
7. **Glossário quebrado na tradução** → placeholder determinístico + QA de aderência.
8. **Drift de localização por país** → detectar país da empresa e parametrizar por jurisdição.

### Nota sobre confiança das fontes
`[FATO]` Técnicas LLM ancoradas na KB `prompt-engineering-kb` (doc_id citados).
`[HIPÓTESE/confidence média]` Métricas de vendors (Jobscan 10.6x/99.7%, Teal 6x, aderência glossário Claude 98%)
vêm de relatórios proprietários com conflito de interesse e datasets que **não são CVs** — tratar como ordem de
grandeza, não fato peer-reviewed. Pricing de LLM/embeddings veio de cache (2026-05-26) — confirmar ao vivo antes de orçar volume.
