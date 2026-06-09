# Web3 Job Tailor — Guia de Uso (núcleo + Fase 0: render profissional)

Implementação dos estágios **1-2 + 6-7-8** da arquitetura
([motor-cv-tailor-arquitetura.md](motor-cv-tailor-arquitetura.md)) + **Fase 0**
do [plano SaaS](saas-plano.md): ler o CV em PDF → fact store → adaptar à vaga
(colada manualmente) com **rastreabilidade por bullet** → **PDF profissional**
(RenderCV/Typst) + DOCX + **traceability report**, PT ou EN. Coleta automática
de vagas (estágio 3) e LinkedIn ficam para a próxima fase.

## 1. Instalação

**Requer Python ≥ 3.12** (constraint do RenderCV). Use o launcher para criar o
venv com 3.13:

```bash
cd c:\Projetos\Projeto_web3-job-hunter\web3-job-hunter
py -3.13 -m venv .venv
.venv\Scripts\activate        # Windows PowerShell
pip install -r requirements.txt
copy .env.example .env         # e preencha ANTHROPIC_API_KEY
```

> O diretório `vendor/typst_packages/` (fontawesome, MIT) é exigido pelo render
> no Windows — já vem no repo; não delete.

> Se aparecer `AttributeError: 'Messages' object has no attribute 'parse'`, rode
> `pip install -U anthropic` (o structured output `messages.parse` exige versão recente).

O pacote vive em `src/`. Rode a partir da raiz com `PYTHONPATH=src`:

```powershell
$env:PYTHONPATH = "src"
```

## 2. Construir o fact store (uma vez, depois REVISAR)

```bash
python -m web3_job_tailor.cli build-store caminho\do\seu_cv.pdf
# layout difícil / PDF escaneado:
python -m web3_job_tailor.cli build-store caminho\do\seu_cv.pdf --vision
```

Gera `data/cv_master.json`. **Revise o JSON manualmente** — ele é a fonte única
de verdade; o tailoring só pode reafirmar o que está aqui. O comando avisa sobre
placeholders não preenchidos (ex.: `github.com/[SEU_USER]`).

## 3. Adaptar o CV a uma vaga

```bash
# vaga num arquivo .txt (cole a descrição do LinkedIn/board ali)
python -m web3_job_tailor.cli tailor --jd vaga_bcb.txt

# tema do PDF (default: engineeringresumes; opções: classic, harvard,
# engineeringclassic, sb2nov, moderncv, ink, opal, ember)
python -m web3_job_tailor.cli tailor --jd vaga_bcb.txt --theme classic

# ou cole no terminal (encerre com Ctrl+Z + Enter no Windows)
python -m web3_job_tailor.cli tailor
```

Saída em `output/`:
- `resume_<empresa>_<idioma>.pdf` — **PDF profissional** (RenderCV/Typst, Tagged PDF)
- `resume_<empresa>_<idioma>.docx` (ATS-safe, single-column)
- `resume_<empresa>_<idioma>.md` (Markdown)
- `trace_report_<empresa>_<idioma>.md` — **rastreabilidade bullet → fato-fonte** + gaps honestos

E no terminal: **match score 0-100** + rationale, gaps honestos, nº de iterações
do Self-Refine, status do crítico (`traceable`/`approved`), avisos de glossário,
QA de ATS e o **ATS self-check** (re-extrai o texto do PDF e confirma que
nome/empresas/skills estão na camada de texto — não confiamos só no claim do
RenderCV).

## 4. Uso programático

```python
import sys; sys.path.insert(0, "src")
from web3_job_tailor import pipeline, factstore

# uma vez:
profile, path, placeholders = pipeline.build_fact_store("seu_cv.pdf")

# por vaga:
result = pipeline.run(open("vaga_bcb.txt", encoding="utf-8").read())
print(result["match"].score, result["md_path"])
```

## 5. Garantias anti-alucinação (o núcleo)

- **Fact store imutável**: o gerador recebe só o JSON revisado como contexto (RAG).
- **`source_fact` por bullet** (Fase 0): o tailor emite JSON estruturado onde cada
  bullet cita verbatim o fato do store de onde deriva — bullet sem fonte não existe.
- **Educação/certificações/idiomas nunca passam pelo LLM** — copiados verbatim do
  store no render (superfície zero de alucinação).
- **Crítico Self-Refine** (`tailor.py`): reprova se algum claim não rastreia ao store.
- **Guardrails determinísticos** (`tailor.deterministic_guardrails`): empregador fora
  do store, bullet sem `source_fact` e métrica `%` inexistente são bloqueados por
  código, independente do LLM.
- **Traceability report**: artefato anexável à candidatura com bullet → fato-fonte.
- Se não atinge match ≥ 75% sem inventar, **reporta o gap honestamente** (não promove nível).

## 6. Decisões e fronteiras

| Item | Decisão |
|---|---|
| Modelos | Haiku (extração) + Sonnet (tailor/judge/tradução). Override por env (`WJT_MODEL_*`); suba p/ `claude-opus-4-8` se quiser. |
| PII | Cloud Anthropic (CV próprio, consentimento próprio). 100% local seria Docling + LLM local. |
| LinkedIn | **Sem scraping.** A vaga chega por colagem manual / email-alerts. Este módulo só recebe o texto. |
| Match semântico | Embeddings (sentence-transformers) **omitidos no núcleo**; score = 0.4·skill_coverage + 0.6·LLM-judge. Ver arquitetura §6 para adicionar. |
| Envio da candidatura | **Manual** — o motor gera e exibe; submeter é ação outward-facing (exige sua ação). |

## 7. Limitações conhecidas

- O guardrail de métricas é heurístico (foca em `%`); o crítico LLM é a checagem principal.
- `messages.parse` exige modelos com structured outputs (Haiku 4.5 / Sonnet 4.6 / Opus 4.8) — ok com os defaults.
- DOCX é gerado por um conversor markdown simples (headings/bullets/parágrafos); revise o layout antes de enviar.
- **Smart-dash no texto exibido**: username com `--` (ex.: `paulo--eduardo`) aparece
  como `–` no texto do PDF (Typst); o **hyperlink real preserva** o `--` correto.
- Nomes de mês no PDF saem em inglês mesmo com seções PT (locale do RenderCV não
  configurado nesta fase).
- O claim ATS do RenderCV é do próprio vendor; nosso `ats_selfcheck_pdf` re-extrai a
  camada de texto a cada geração como verificação independente mínima.
- **Não executei nenhuma chamada paga à API** ao escrever isto — rode você com sua chave.
