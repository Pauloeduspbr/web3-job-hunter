# Job Hunter Pipeline — Automacao de Busca e Tailoring de CV

Pipeline automatizado: **scraping de vagas → score de match → briefing → CV alinhado a vaga**.
Padrao de orquestracao: prompt chaining (Anthropic "Building Effective Agents").

## Aplicacao Web (FastAPI + React)

```powershell
# Backend (porta 8000 — tambem serve o frontend buildado em /)
python -m uvicorn backend.app:app --port 8000

# Frontend dev com hot-reload (opcional, porta 5173 com proxy /api -> 8000)
cd frontend; npm run dev

# Rebuild do frontend apos mudancas
cd frontend; npm run build
```

Abra **http://localhost:8000** — o dashboard permite:
- **Upload** de curriculo (.pdf/.md/.docx/.txt) → `Curriculo/`
- **Colar links** de vagas → `Links_Empregos/from_app.txt`
- **Disparar pipeline**: scrape (Apify), boards gratis, busca LinkedIn, score —
  **toda coleta pontua automaticamente** (as vagas aparecem direto na tabela)
- **Funil em 2 etapas**: a busca LinkedIn traz so a listagem (sem descricao/modalidade —
  aparecem como "❔ Detalhar"); o botao **🔍 Detalhar** enriquece as vagas filtradas
  ($0.005/vaga) com descricao completa + modalidade remote/hibrida/presencial e re-pontua
- **Filtros na tabela**: modalidade (🏠 remote / 🏢 hibrida / 🏬 presencial), score minimo, texto
- **Gerar CV** por vaga (botao na tabela):
  - com `ANTHROPIC_API_KEY` no `.env` → CV gerado automaticamente via Claude API
    (modelo claude-opus-4-8, ~$0.05-0.15/CV)
  - sem a key (modo manual) → gera o brief; voce pede o CV ao Claude Code
- **Download** dos CVs em `.md`, `.docx` (melhor parse em ATS Workday) e `.pdf`
  (text-based, Arial, 2 paginas — formato para Greenhouse/Lever/Ashby e envio direto)

API: `GET /api/status|jobs|briefs|resumes`, `POST /api/pipeline/{scrape|search|boards|score}`,
`POST /api/links`, `POST /api/resume/upload`, `POST /api/cv/generate`,
`GET /api/download/resume/{nome}?fmt=md|docx|pdf`.

## Arquitetura

```
Links_Empregos/*.txt ──┐
LinkedIn search ───────┼──► data/jobs/raw/*.json ──► score ──► data/jobs/scored/scored_jobs.json
Free boards ($0) ──────┘                                            │
                                                                    ▼
output/resumes/*.md ◄── Claude Code (etapa LLM) ◄── output/analysis/brief_*.md
```

| Etapa | Modulo | Fonte | Custo |
|-------|--------|-------|-------|
| `scrape` | `src/scrape_jobs.py` | Actor `apimaestro/linkedin-job-detail` (0 falhas/109k runs, sem cookies) | ~$0.005/vaga |
| `search` | `src/scrape_jobs.py` | Actor proprio `viralanalyzer/linkedin-jobs-multi-country` | compute units (creditos do plano) |
| `boards` | `src/free_boards.py` | Greenhouse/Ashby/Lever APIs + RemoteOK + RSS cryptocurrencyjobs | $0 |
| `score` | `src/score_jobs.py` | Lexico de ~70 skills c/ aliases vs `config/profile.yaml` | $0 |
| `brief` | `src/tailor_resume.py` | Gap analysis + keywords ATS + evidencias | $0 |
| CV final | Claude Code | Brief + resume base + praticas ATS | sessao Claude |

## Uso

```powershell
# 1. Adicione URLs de vagas LinkedIn em Links_Empregos/*.txt (1 por linha), depois:
python main.py scrape          # detalhe completo de cada vaga

# 2. Colete vagas das boards gratis (empresas em config/companies_watchlist.yaml):
python main.py boards

# 3. Busca por keyword no LinkedIn (actor proprio, anonimo):
python main.py search          # default: "data engineer" / United States

# 4. Score de todas as vagas raw contra o perfil:
python main.py score           # [APPLY] >= 60

# 5. Briefing de tailoring da N-esima melhor vaga:
python main.py brief 0

# 6. Etapa LLM — no Claude Code:
#    "Gere o CV alinhado usando output/analysis/brief_<vaga>.md"
```

## Configuracao

- **`.env`** — `APIFY_TOKEN` (NUNCA commitar; ja esta no .gitignore)
- **`config/profile.yaml`** — perfil canonico de skills/conquistas (fonte de verdade do matching
  e limite de veracidade do CV: o LLM nao pode reivindicar nada fora dele)
- **`config/companies_watchlist.yaml`** — slugs Greenhouse/Ashby/Lever de empresas-alvo;
  adicione empresas crypto novas aqui (verificadas: consensys, ripple, fireblocks,
  kraken.com, chainalysis-careers, ledger)

## Scoring

`score = 0.8 * skill_match + bonus`. Skill match = cobertura ponderada (peso 1-3 por skill
do perfil) das skills demandadas na descricao. Bonus: titulo-alvo (+10), dominio web3/fintech
(+5), remote (+5). Penalidade: role excluida (-40), onsite/hybrid (-15).

PROIBIDO avaliar vaga apenas por salario ou titulo — o score pondera todas as dimensoes.

## Regras de veracidade do CV (invioláveis)

1. Nenhuma skill/ferramenta fora de `config/profile.yaml` ou dos curriculos base.
2. Numeros/percentuais exatamente como nas fontes (99.9%, 40%, 60%, 50%, 70%).
3. Gaps da vaga sao mitigados por experiencia adjacente ou portfolio — nunca inventados.
4. Formato ATS-safe: coluna unica, headers padrao, contato no corpo, datas "Mon YYYY",
   sem tabelas/imagens, max 2 paginas.

## Limitacoes conhecidas

- Vagas vindas de RSS (cryptocurrencyjobs.co) tem descricao truncada → score subestimado.
  Mitigacao: abrir a URL da vaga e scrapear o detalhe antes de descartar.
- RemoteOK ToS exige atribuicao com link se os dados forem republicados (uso pessoal ok).
- `web3.career` tem API gratis mas exige signup (token proprio) — pendente de cadastro.
- Actor `viralanalyzer/linkedin-jobs-multi-country` e da propria conta: validar output
  schema na primeira execucao de `search` (normalizador cobre formatos comuns + LinkedIn detail).

## Manutencao

- Novas vagas: append em `Links_Empregos/*.txt` e rode `python main.py all`.
- Novas empresas-alvo: adicionar slug em `companies_watchlist.yaml` (testar com
  `python src/free_boards.py`).
- Recorrencia: agendar `python main.py boards && python main.py score` (diario) —
  as APIs publicas sao gratuitas; so o scrape LinkedIn custa creditos Apify.
