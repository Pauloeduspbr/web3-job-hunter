# Projeto Web3 + IA - Paulo Eduardo dos Santos

## Quem: Paulo
- Senior Data Engineer (9+ anos)
- Stack: Python, SQL, PySpark, Airflow, dbt, Spark, Kafka, AWS/Azure/GCP
- Empresas: Itau, Banco do Brasil, Natura, Cielo, Hospital Sirio-Libanes, Claro, Vivo, Enel
- GitHub: github.com/Pauloeduspbr
- Perfil Superteam Earn: ativo

## Objetivo Principal
Conseguir vaga remota de Data Engineer em empresa Web3/FinTech/crypto ($100k+).
Secundario: bounties Superteam Earn como side income.

## GitHub Portfolio (LIVE)

### 1. crypto-data-pipeline
- URL: github.com/Pauloeduspbr/crypto-data-pipeline
- Stack: Python, Airflow, PostgreSQL, Docker, CoinGecko API
- Destaque: Pipeline completo com dados reais, 100 coins, 1.74s execucao
- Testado: 7/7 quality checks passaram com dados reais (18 Mar 2026)

### 2. medallion-data-lake
- URL: github.com/Pauloeduspbr/medallion-data-lake
- Stack: Python, Airflow, dbt, Terraform (AWS + GCP), Docker/MinIO
- Destaque: Template production-ready Bronze/Silver/Gold com SCD Type 2, 36 testes

### 3. dune-analytics-queries
- URL: github.com/Pauloeduspbr/dune-analytics-queries
- Stack: SQL (PostgreSQL/Dune Analytics)
- Destaque: 12 queries blockchain analytics (DeFi, NFT, Solana, Ethereum, cross-chain)

## Vagas Alvo

### Prioridade 1: BCB Group - Data Engineer ($105k-$120k, Remote)
- Match: 95% — SQL, ETL, GCP, dbt, dashboards
- Cover letter: Cover_Letter_BCB_Group.md
- CV otimizado: Resume_Paulo_Eduardo_Web3_v2.md

### Prioridade 2: Zinnia - Senior Data Engineer ($122k-$123k, Remote)
- Match: 90% — Python, SQL, Airflow, dbt, GCP, BigQuery, Terraform

## Documentos Criados
- Resume_Paulo_Eduardo_Web3_v2.md — CV otimizado para vagas Web3/FinTech
- Cover_Letter_BCB_Group.md — Cover letter personalizada BCB Group
- Interview_QA_Data_Engineer.md — 45+ perguntas com respostas (tecnico, comportamental, crypto)

## Historias AWS Ativas (trabalho atual)

### Tipo A: Ingestao de Arquivo (GCP -> AWS Bronze)
1. agrupamentos_cliente - [Revenue Management]
2. dp_grupo_grc_de_grupo - [Revenue Management]
3. depara_dp_feriados - [Retirada, Uso e Dev.]

### Tipo B: Ingestao de Banco de Dados (DB -> AWS Bronze)
4. checkouts - [Retirada, Uso e Dev.]
5. contrato_handheld - [Retirada, Uso e Dev.]
6. ncf_solicitacao_bloqueio - [Retirada, Uso e Dev.]

## Pipeline de Automacao (LIVE — ver README_PIPELINE.md)

- **App web**: `python -m uvicorn backend.app:app --port 8000` -> http://localhost:8000 (FastAPI + React; upload de CV, links, pipeline, download .md/.docx). Geracao de CV hibrida: ANTHROPIC_API_KEY presente -> Claude API (claude-opus-4-8); ausente -> brief + Claude Code
- **Funil de busca em 2 etapas**: busca LinkedIn (actor proprio) traz SO a listagem (titulo/empresa/cidade, sem descricao nem modalidade) -> toda coleta pontua automatico -> botao "Detalhar" enriquece vagas promissoras via apimaestro/linkedin-job-detail ($0.005/vaga) trazendo descricao + remote/hybrid/onsite -> re-score. Filtros na tabela: modalidade, score minimo, texto. Dedupe: registro com detalhe SEMPRE vence listagem (score_jobs.py)
- `python main.py scrape|search|boards|score|brief` — vagas (Apify + boards gratis) -> score vs config/profile.yaml -> brief de tailoring -> CV gerado pelo Claude Code
- Actors validados: `apimaestro/linkedin-job-detail` ($0.005/vaga, scrape por URL) e `viralanalyzer/linkedin-jobs-multi-country` (actor PROPRIO da conta, busca por keyword, so compute units)
- Boards gratis ($0): Greenhouse/Ashby/Lever APIs (slugs em config/companies_watchlist.yaml), RemoteOK, RSS cryptocurrencyjobs
- CVs tailorizados em output/resumes/; NUNCA inventar skill/numero fora de config/profile.yaml
- Ingles do Paulo: B2 upper-intermediate — NUNCA inflar para "advanced/fluent" em CV

## Regras para o Claude

1. **Priorize eficiencia**: menos conversa, mais resultado
2. **Portugues** para estrategia, **ingles** para codigo/CVs/cover letters
3. **Vagas Web3**: foque em Data Engineer, nao dev Solidity/Rust
4. **Pipelines AWS**: siga padrao bronze sem over-engineering
5. **Use o background de Data Engineer** como diferencial competitivo
6. **GitHub**: manter repos com dados reais e outputs evidenciados
