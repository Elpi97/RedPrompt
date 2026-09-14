"""Background worker that runs the assessment suite."""

from __future__ import annotations

import os
import queue
import sys
import threading
from datetime import datetime
from pathlib import Path

import ai_pentest_suite as suite

from .log_bridge import QueueWriter


def fetch_ollama_models(base_host: str = 'http://127.0.0.1:11434') -> list[str]:
    """Return local Ollama model names via /api/tags (stdlib)."""
    from urllib.request import urlopen
    import json

    url = base_host.rstrip('/') + '/api/tags'
    try:
        with urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        return [m.get('name', '') for m in data.get('models', []) if m.get('name')]
    except Exception:
        return []


def worker_run(
    q: queue.Queue,
    config: dict,
    runs: int,
    rate_limit: float,
    judge: bool,
    stop_event: threading.Event,
    project_root: Path,
) -> None:
    """Execute suite in a worker thread; emit queue events."""
    old_stdout = sys.stdout
    writer = QueueWriter(q, fallback=old_stdout)
    sys.stdout = writer
    try:
        os.chdir(project_root)
        q.put(('status', 'Running'))
        q.put(('log', f'Working directory: {project_root}'))
        results = suite.run_automated_suite(
            config,
            judge=judge,
            runs=runs,
            rate_limit=rate_limit,
            stop_event=stop_event,
        )
        if stop_event.is_set() and not results:
            q.put(('error', 'Stopped before any payload completed.'))
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_path = suite.export_to_csv(results, config, timestamp, runs=runs)
        json_path = suite.export_full_results(results, config, timestamp, runs)
        summary = {
            'CRITICAL': sum(1 for r in results if r['consolidated_finding'] == 'CRITICAL'),
            'WARNING': sum(1 for r in results if r['consolidated_finding'] == 'WARNING'),
            'COVERAGE_GAP': sum(1 for r in results if r['consolidated_finding'] == 'COVERAGE_GAP'),
            'PASSED': sum(1 for r in results if r['consolidated_finding'] == 'PASSED'),
        }
        suite.append_audit_log(config, runs, rate_limit, judge, summary)
        q.put(('done', {
            'results': results,
            'summary': summary,
            'csv_path': str(Path(csv_path).resolve()),
            'json_path': str(Path(json_path).resolve()),
            'timestamp': timestamp,
        }))
    except Exception as exc:
        q.put(('error', f'{type(exc).__name__}: {exc}'))
    finally:
        try:
            writer.flush()
        except Exception:
            pass
        sys.stdout = old_stdout
        q.put(('status', 'Idle'))


def worker_self_test(q: queue.Queue) -> None:
    """Run offline self-test and report pass/fail."""
    old_stdout = sys.stdout
    writer = QueueWriter(q, fallback=old_stdout)
    sys.stdout = writer
    try:
        q.put(('status', 'Self-test'))
        ok = suite.run_self_test()
        q.put(('self_test', ok))
    except Exception as exc:
        q.put(('error', f'{type(exc).__name__}: {exc}'))
    finally:
        try:
            writer.flush()
        except Exception:
            pass
        sys.stdout = old_stdout
        q.put(('status', 'Idle'))
