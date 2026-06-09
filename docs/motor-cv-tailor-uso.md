# Web3 Job Tailor — Guia de Uso (núcleo de tailoring)

Implementação dos estágios **1-2 + 6-7-8** da arquitetura
([motor-cv-tailor-arquitetura.md](motor-cv-tailor-arquitetura.md)): ler o CV em
PDF → fact store → adaptar à vaga (colada manualmente) → traduzir/localizar →
exportar CV ATS-safe. Coleta automática de vagas (estágio 3) e LinkedIn ficam
para a próxima fase.

## 1. Instalação

```bash
cd c:\Projetos\Projeto_web3-job-hunter\web3-job-hunter
python -m venv .venv
.venv\Scripts\activate        # Windows PowerShell
pip install -r requirements.txt
copy .env.example .env         # e preencha ANTHROPIC_API_KEY
```

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

# ou cole no terminal (encerre com Ctrl+Z + Enter no Windows)
python -m web3_job_tailor.cli tailor
```

Saída em `output/`:
- `resume_<empresa>_<idioma>.md` (Markdown)
- `resume_<empresa>_<idioma>.docx` (ATS-safe, single-column)

E no terminal: **match score 0-100** + rationale, gaps honestos, nº de iterações
do Self-Refine, status do crítico (`traceable`/`approved`), avisos de glossário e
de ATS.

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
- **Crítico Self-Refine** (`tailor.py`): reprova se algum claim não rastreia ao store.
- **Guardrail determinístico** (`factstore.verify_traceability`): sinaliza métricas
  com `%` no output que não existem no store (possível invenção).
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
- **Não executei nenhuma chamada paga à API** ao escrever isto — rode você com sua chave.
