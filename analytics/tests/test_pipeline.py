from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

ANALYTICS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ANALYTICS_ROOT / "src"))

from mwg_dmx_analytics.pipeline import build_analytics


class PipelineTests(unittest.TestCase):
    def test_build_creates_reproducible_artifacts_and_database(self) -> None:
        sample = ANALYTICS_ROOT / "data" / "sample"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "curated"
            result = build_analytics(
                facts_path=sample / "financial_facts_sample.csv",
                sources_path=sample / "source_documents_sample.csv",
                scenarios_path=sample / "sotp_scenarios_sample.json",
                output_dir=output,
            )
            self.assertTrue(result.validation_summary["is_valid"])
            self.assertEqual(result.ratios_count, 2)
            self.assertEqual(result.scenarios_count, 3)
            expected_files = {
                "analytics.sqlite",
                "validation_results.csv",
                "ratios.json",
                "sotp_results.json",
                "run_manifest.json",
            }
            self.assertEqual({path.name for path in output.iterdir()}, expected_files)

            manifest = json.loads((output / "run_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["run_id"], result.run_id)
            self.assertEqual(len(manifest["outputs"]["analytics.sqlite"]["sha256"]), 64)

            with closing(sqlite3.connect(output / "analytics.sqlite")) as connection:
                fact_count = connection.execute("SELECT COUNT(*) FROM financial_facts").fetchone()[0]
                run_status = connection.execute(
                    "SELECT status FROM analytics_runs WHERE run_id = ?", (result.run_id,)
                ).fetchone()[0]
            self.assertEqual(fact_count, 52)
            self.assertEqual(run_status, "completed")


if __name__ == "__main__":
    unittest.main()
