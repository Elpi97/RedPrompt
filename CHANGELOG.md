# Changelog

## [1.1.0] — 2026-09-13

First public product release of RedPrompt.

### Assessment engine
- Configurable `--runs` (default 5) with Wilson 95% confidence intervals
- Triage labels: CRITICAL / WARNING / COVERAGE_GAP / PASSED
- 1–5 compliance rubric and safer bypass heuristics
- Multi-turn, context-exhaustion, and HTML-entity payloads (LLM-11–13)
- OWASP LLM Top 10 (2025) + MITRE ATLAS + CWE tags on every payload
- `audit.log`, `--rate-limit`, cooperative stop

### GUI
- CustomTkinter Process + Report tabs (pentest theme)
- Ollama model picker and live process log
- Plain-language **What happened / Why it matters / What to do** remediations

### Docs & site
- Branded README and `docs/` GitHub Pages landing
- SOP and roadmap updates
