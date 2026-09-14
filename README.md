<p align="center">
  <img src="docs/assets/logo.svg" alt="RedPrompt logo" width="120" />
</p>

<p align="center">
  <img src="docs/assets/banner.svg" alt="RedPrompt" width="920" />
</p>

<p align="center">
  <strong>Authorized LLM red-team assessment</strong><br/>
  Probe · Measure · Remediate — for Cybersecurity &amp; AI Engineering teams
</p>

<p align="center">
  <a href="https://elpi97.github.io/RedPrompt/"><img src="https://img.shields.io/badge/GitHub%20Pages-Live-e11d48?style=for-the-badge&labelColor=0b0f14" alt="GitHub Pages" /></a>
  <a href="https://github.com/Elpi97/RedPrompt/releases"><img src="https://img.shields.io/badge/Release-v1.1.0-f59e0b?style=for-the-badge&labelColor=0b0f14" alt="Release" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge&labelColor=0b0f14" alt="MIT" /></a>
  <a href="requirements.txt"><img src="https://img.shields.io/badge/Python-3.14%20baseline-38bdf8?style=for-the-badge&labelColor=0b0f14" alt="Python" /></a>
  <a href="https://atlas.mitre.org/"><img src="https://img.shields.io/badge/Mapped-ATLAS%20%2F%20OWASP-f59e0b?style=for-the-badge&labelColor=0b0f14" alt="ATLAS OWASP" /></a>
</p>

<p align="center">
  <a href="https://elpi97.github.io/RedPrompt/">Website</a> ·
  <a href="https://github.com/Elpi97/RedPrompt/releases">Releases</a> ·
  <a href="#quick-start">Quick start</a> ·
  <a href="#gui">GUI</a> ·
  <a href="STANDARD_OPERATING_PROCEDURE.md">SOP</a> ·
  <a href="ROADMAP.md">Roadmap</a>
</p>

---

## What is RedPrompt?

**RedPrompt** is an authorized red-team harness for **local OpenAI-compatible LLMs** (Ollama, vLLM, LM Studio).

It runs tagged prompt-injection / jailbreak payloads, scores responses with **objective evidence** and a **1–5 compliance rubric**, reports **Wilson 95% confidence intervals**, and gives your team **plain-language remediation** in a dark pentest GUI.

> This is a **triage suite**, not a claim of full MITRE ATLAS or OWASP LLM Top 10 coverage. Tags map findings — they don’t invent completeness.

```text
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Process    │────▶│   Measure    │────▶│   Remediate     │
│  CLI / GUI  │     │  CI · rubric │     │  What / Why / Do│
└─────────────┘     └──────────────┘     └─────────────────┘
```

---

## Why teams use it

| | |
| --- | --- |
| **Simple** | Non-engineers see *Needs fix now* / *Worth reviewing* / *Looks good* — not jargon walls. |
| **Clear** | Every finding: **What happened** · **Why it matters** · **What to do**. |
| **Honest** | Rates + confidence intervals beat fake binary “secure / insecure”. |
| **Operable** | SOP, audit log, CSV/JSON evidence, cooperative stop. |
| **Lean** | Assessment engine is **stdlib-only**; GUI is optional CustomTkinter. |

---

## Quick start

**Requirements:** Python **3.14.4** company baseline (verified on 3.14.3+) · local chat-completions endpoint.

```bash
git clone https://github.com/Elpi97/RedPrompt.git
cd RedPrompt
pip install -r requirements.txt   # GUI only
```

Create `.env` (git-ignored):

```text
VLLM_BASE_URL=http://127.0.0.1:11434/v1
MODEL_NAME=qwen2.5:14b
API_KEY=ollama
COMPANY_NAME=Your Organization
CLASSIFICATION=INTERNAL-USE-ONLY
TESTER_IDENTITY=your.name
```

```bash
python ai_pentest_suite.py --self-test          # offline classifier checks
python ai_pentest_suite.py --runs 5             # live assessment
python -m redprompt_gui                         # Process + Report UI
```

**Authorized testing only.** Read the [Standard Operating Procedure](STANDARD_OPERATING_PROCEDURE.md) before you run against any system.

### Ollama

```bash
# Windows example path if ollama is not on PATH:
"%LOCALAPPDATA%\Programs\Ollama\ollama.exe" pull qwen2.5:14b
python ai_pentest_suite.py --runs 1
```

---

## GUI

```bash
python -m redprompt_gui
```

| Tab | Purpose |
| --- | --- |
| **Process** | Endpoint, Ollama model picker, runs, rate limit, live log, Stop |
| **Report** | Severity cards, finding matrix, reasoning & remediation playbook, evidence |

---

## How results work

**Per run:** `ERROR` · `SAFE` · `VULNERABLE` · `INDETERMINATE` (+ compliance 1–5)

**Per payload:**  
`Vulnerability Rate: X/N (Rate% +/- margin, 95% CI [low%, high%])`

| Triage label | Plain language |
| --- | --- |
| `CRITICAL` | **Needs fix now** |
| `WARNING` | **Worth reviewing** |
| `COVERAGE_GAP` | **Couldn't fully test** |
| `PASSED` | **Looks good** |

`--rate-limit` = seconds between requests (client throttle).  
`--judge` = optional same-model aid for indeterminate only — **not** an independent control.  
`--self-test` = offline heuristic checks — **does not** call your model.

---

## Repository map

| Path | Role |
| --- | --- |
| `ai_pentest_suite.py` | Stdlib assessment engine |
| `redprompt_gui/` | CustomTkinter Process + Report + remediations |
| `docs/` | GitHub Pages site |
| `STANDARD_OPERATING_PROCEDURE.md` | Authorized execution |
| `ROADMAP.md` | Phase 2+ |
| `requirements.txt` | `customtkinter>=5.2.0` |

---

## Standards posture

Payloads carry **OWASP LLM Top 10 (2025)** and **MITRE ATLAS** technique tags for mapping and reporting. Treat coverage as **partial by design**. Expand via the roadmap before using RedPrompt as a compliance artifact.

---

## License

[MIT](LICENSE) © 2026 Elpi97

<p align="center">
  <sub>RedPrompt — measure what matters, fix what fails.</sub>
</p>
