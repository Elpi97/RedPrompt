# Standard Operating Procedure

## 1. Purpose

This procedure governs authorized internal execution of the RedPrompt LLM
red-teaming suite against local OpenAI-compatible deployments.

## 2. Authorization and Handling

1. Obtain approval from the system owner before testing.
2. Confirm the endpoint is local or otherwise explicitly in scope.
3. Treat the `.env` file, logs, and CSV outputs as internal assessment data.
4. Do not commit API keys, `.env` files, or raw CSV findings to source control.

## 3. Pre-Run Checks

1. Install Python 3.10 or later.
2. Start the target model server and confirm it exposes the chat-completions
   API at the configured URL.
3. In the repository directory, create or update `.env` with the endpoint,
   model name, API key, company name, and classification.
4. Run `python3 -m py_compile ai_pentest_suite.py` and `python3 ai_pentest_suite.py --self-test`.
5. Run the suite from the repository directory:

   ```sh
   python3 ai_pentest_suite.py --runs 5
   ```

   Optional: `--rate-limit 0.5`, `--tester your.name`, `--judge` (non-authoritative).

## 4. Execution Controls

- The suite sends thirteen tagged payloads (LLM-01–LLM-13). Default is **5**
  runs each (`--runs` 1–20). Record the chosen run count in the assessment notes.
- Requests use temperature `0.3`, `max_tokens` `512`, and a 90-second timeout.
- Multi-turn (LLM-11), context-exhaustion (LLM-12), and HTML-entity (LLM-13)
  payloads are in scope for Phase 1.
- A Qwen-style `reasoning_content` field is retained in the JSON sidecar when
  final content is empty. It is classified as `INDETERMINATE`, not treated as
  a final answer.
- Prefer the per-payload **Wilson 95% CI** summary over triage labels alone.
- Add `--judge` only as a same-model triage aid for indeterminate runs; it is
  not an independent control.
- Do not change payloads, run count, or evaluation criteria during a baseline
  assessment. Record approved changes before the next run.
- Confirm `audit.log` received a new JSON line after the run.

## 5. Report Validation

For the generated `ai_pentest_matrix_*.csv`, confirm:

1. The initial `# ` metadata lines include generated time, suite version,
   company, classification, target, model, and runs-per-payload.
2. There is one record per payload (`LLM-01` through `LLM-13`).
3. `run_statuses` values are only `ERROR`, `SAFE`, `VULNERABLE`, or
   `INDETERMINATE`.
4. `vulnerable_count` equals the number of vulnerable runs; `ci_summary`
   matches that count and `runs`.
5. Standards columns `mitre_atlas`, `owasp_llm`, and `cwe` are populated.
6. Triage labels are `CRITICAL`, `WARNING`, `COVERAGE_GAP`, or `PASSED` per
   the Wilson/CI consolidation rules in the README — not the legacy 3/1-2/0 rule.
7. Every vulnerable and indeterminate response is manually reviewed and
   classified as a true bypass, benign compliance, or heuristic miss.
8. Error and timeout counts are included in the assessment handoff; a high
   error rate yields `COVERAGE_GAP` even when no vulnerable runs appear.

## 6. Triage and Escalation

- Escalate `CRITICAL` findings immediately to the model owner and security
  lead with the payload ID, CI summary, exact response, and run count.
- Review `WARNING` findings before classifying them as exploitable. Language
  preference compliance alone is not necessarily an instruction-hierarchy
  bypass.
- Treat `COVERAGE_GAP` as incomplete evidence, not a pass.
- Re-run endpoint failures only after the service owner verifies availability.
  Do not treat timeouts as blocked prompts.
- Preserve the raw CSV, JSON sidecar, and relevant `audit.log` lines in the
  approved internal evidence location.

## 7. Windows Guidance

- Use a supported Python 3.10+ installation and run the command from the
  repository directory.
- The CSV is UTF-8. Open it with an encoding-aware tool if non-ASCII model
  responses do not render correctly in Excel.
- Console output is operational status only; review non-ASCII model content in
  the CSV rather than relying on console rendering.
