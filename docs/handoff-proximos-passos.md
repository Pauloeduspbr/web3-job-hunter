# Handoff — Estado do Projeto e Retomada em Novo Notebook

> **Data**: 2026-06-09. **Branch de trabalho**: `feature/web3-job-tailor-core`
> (3 commits à frente da `main`; PR ainda não aberto).

---

## 1. Estado atual (o que está PRONTO e commitado)

| Item | Onde | Status |
|---|---|---|
| Motor core (estágios 1-2 + 6-7-8) | `src/web3_job_tailor/` | ✅ código + smoke tests offline |
| **Fase 0 — render profissional** | `render.py`, `trace_report.py`, `jsonresume.py` | ✅ PDFs reais gerados e verificados (3 temas) |
| Rastreabilidade por bullet (`source_fact`) + guardrails determinísticos | `tailor.py`, `models.py` | ✅ |
| Arquitetura do motor (8 estágios) | `docs/motor-cv-tailor-arquitetura.md` | ✅ |
| **Plano SaaS (4 fases)** | `docs/saas-plano.md` | ✅ |
| Guia de uso | `docs/motor-cv-tailor-uso.md` | ✅ |
| Glossário PT/EN | `config/glossary.yaml` | ✅ |
| Pacote Typst vendorizado (fix Windows) | `vendor/typst_packages/` | ✅ não deletar |
| Contexto+regras do projeto | `CLAUDE.md` (raiz) | ✅ |

**Pendente da Fase 0 (ação do Paulo, requer API key)**: rodar `build-store` no CV
real → revisar `data/cv_master.json` (corrigir placeholder do GitHub!) → `tailor`
numa vaga real → aplicar (manual).

## 2. Setup no notebook novo (checklist)

```powershell
# 1. Clonar e entrar na branch
git clone https://github.com/Pauloeduspbr/web3-job-hunter.git
cd web3-job-hunter
git checkout feature/web3-job-tailor-core

# 2. Python >= 3.12 obrigatório (RenderCV). Instalar 3.13 se não houver: py -0 lista
py -3.13 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 3. Segredos (NÃO estão no git)
copy .env.example .env    # preencher ANTHROPIC_API_KEY

# 4. Smoke rápido do render (offline, sem API)
$env:PYTHONPATH = "src"
python -c "import sys; sys.path.insert(0,'src'); from web3_job_tailor import render; from web3_job_tailor.models import ResumeProfile, Contact; import tempfile; p=ResumeProfile(contact=Contact(full_name='Smoke Test')); print(render.render_pdf(render.build_rendercv_data(p,None), tempfile.mkdtemp(), 'smoke'))"
```

### O que NÃO está no git (levar/recriar manualmente)
- **`.env`** — `ANTHROPIC_API_KEY` (recriar do .env.example)
- **`data/`** — fact store (PII; recriar com `build-store` ou copiar via pendrive/criptografado)
- **`output/`** — CVs gerados (recriáveis)
- **`.venv/`** — recriável (passo 2)
- **CV em PDF original** do Paulo (não versionado — levar o arquivo)

## 3. Próximos passos (ordem recomendada)

1. **Concluir Fase 0 (dogfooding)**: build-store com o CV real → revisar fact store
   → tailor nas vagas BCB Group/Zinnia → aplicar (manual, com aprovação).
2. **Abrir PR** da branch para `main` quando quiser consolidar:
   https://github.com/Pauloeduspbr/web3-job-hunter/pull/new/feature/web3-job-tailor-core
3. **Fase 1 (MVP web)** — ver `docs/saas-plano.md` §3: FastAPI + Postgres
   (tenant_id desde o dia 1), upload CV → revisão do fact store na UI →
   tailor → preview → download; traceability view; beta fechado (Superteam).
4. Gate jurídico (advogado LGPD) **antes** de qualquer cliente pagante — Fase 2.

## 4. Decisões já tomadas (não rediscutir sem motivo)

- LinkedIn: **só** email-alerts + colagem manual; scraping proibido por design.
- PII: cloud Anthropic (Messages API **inline**; nunca Files/Batch p/ CV).
- Render: RenderCV/Typst (default `engineeringresumes`); HTML/CSS só p/ preview futuro.
- Multi-tenant futuro: pool model + Postgres RLS; Supabase + Stripe.
- Posicionamento SaaS: evidence-grounded tailoring; preço Pro US$12-15/mês + créditos.
- Modelos LLM: Haiku (extração) + Sonnet (tailor/judge/tradução), override por `WJT_MODEL_*`.

## 5. Limitações conhecidas (não são bugs novos)

- Username com `--` sofre smart-dash no TEXTO do PDF (hyperlink fica correto).
- Meses no PDF em inglês mesmo em CV PT (locale RenderCV não configurado).
- IDE pode acusar imports de `rendercv`/`pymupdf`/`docx` — falso positivo se o
  interpretador do IDE não apontar para `.venv` (configurar o interpreter no VS Code).
