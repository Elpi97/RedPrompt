# RedPrompt Roadmap & Future Initiatives

Phase 1 (engine upgrades: dynamic runs, Wilson CI, multi-turn/context encoding schema, standards tags, 1–5 compliance rubric, audit.log, rate limiting) is implemented in `ai_pentest_suite.py` suite version **1.1.0**.

The items below are **deferred**. They intentionally stay out of the zero-dependency core until an isolated extension interface or packaging decision is made.

---

### 1. CI/CD Pipeline & Automated Regression Testing

**Target milestone:** v1.2

- Implement exit-code matrices and threshold triggers (e.g. fail pipeline if breach rate lower CI bound > 0%).
- Track baseline model drifts via historical delta reports (`run_prev.json` vs `run_current.json`).
- Provide official GitHub Actions and GitLab CI job templates for staging gate evaluation.
- Wire `--self-test` as a required pre-merge check.

---

### 2. Multimodal Adversarial Vectors

**Target milestone:** v1.3 (likely requires optional extras beyond stdlib)

- Expand coverage to multimodal models (vision, audio).
- Target typographic attacks, visual jailbreaks, and PGD-perturbed inputs.
- Audio injection testing (ultrasonic / steganographic adversarial patches).
- Map multimodal probes to AML.T0051 / AML.T0054 without overstating text-only coverage.

---

### 3. Model Supply Chain & Weight Integrity

**Target milestone:** v1.4

- Insecure deserialization checks (Pickle scanning, PyTorch `.pt` validation).
- Model artifact provenance (safetensors validation, SHA-256 verification against registries).
- Training / fine-tuning data poisoning detection hooks.
- Align findings with OWASP LLM03 / LLM05 (2025) and ATLAS supply-chain techniques.

---

### 4. Independent Judge & Semantic Scoring

**Target milestone:** v1.2–v1.3

- Separate `JUDGE_BASE_URL` / `JUDGE_MODEL` so adjudication is not same-model circular.
- Optional embedding-based semantic similarity (would require an extras package or remote API).
- Remediations and executive-summary generators for non-technical stakeholders.

---

### 5. Broader Standards Crosswalk

**Target milestone:** v1.3

- Explicit NIST AI RMF (Govern / Map / Measure / Manage) tagging per payload.
- ISO/IEC 42001 control mapping for management-system audits.
- Expanded multilingual payload packs (ES, ZH, AR, JA) under versioned suites.
