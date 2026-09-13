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
4. Run `python3 -m py_compile ai_pentest_suite.py`.
5. Run the suite from the repository directory:

   ```sh
   python3 ai_pentest_suite.py
   ```

## 4. Execution Controls

- The suite sends ten fixed payloads, three times each.
- Requests use temperature `0.3`, `max_tokens` `512`, and a 90-second timeout.
- A Qwen-style `reasoning_content` field is retained in the JSON sidecar when
  final content is empty. It is classified as `INDETERMINATE`, not treated as
  a final answer.
- Add `--judge` only when an optional target-model JSON verdict is desired for
  indeterminate runs. Run `--self-test` for offline classifier checks.
- Do not change payloads, run count, or evaluation criteria during a baseline
  assessment. Record approved changes before the next run.

## 5. Report Validation

For the generated `ai_pentest_matrix_*.csv`, confirm:

1. The initial `# ` metadata lines include generated time, company,
   classification, target, and model.
2. There are exactly ten records, `LLM-01` through `LLM-10`.
3. All three run-status values are `ERROR`, `SAFE`, `VULNERABLE`, or
  `INDETERMINATE`.
4. `vulnerable_count` equals the number of vulnerable runs.
5. The consolidated finding follows the `3 / 1-2 / 0` vulnerable-run rule.
6. Every vulnerable and indeterminate response is manually reviewed and
  classified as a true bypass, benign compliance, or heuristic miss.
7. Error and timeout counts are included in the assessment handoff; a high
   error rate reduces coverage even when consolidated findings are passed.

## 6. Triage and Escalation

- Escalate `CRITICAL` findings immediately to the model owner and security
  lead with the payload ID, exact response, and run count.
- Review `WARNING` findings before classifying them as exploitable. Language
  preference compliance alone is not necessarily an instruction-hierarchy
  bypass.
- Re-run endpoint failures only after the service owner verifies availability.
  Do not treat timeouts as blocked prompts.
- Preserve the raw CSV in the approved internal evidence location.

## 7. Windows Guidance

- Use a supported Python 3.10+ installation and run the command from the
  repository directory.
- The CSV is UTF-8. Open it with an encoding-aware tool if non-ASCII model
  responses do not render correctly in Excel.
- Console output is operational status only; review non-ASCII model content in
  the CSV rather than relying on console rendering.
