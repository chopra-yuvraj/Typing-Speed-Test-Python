"""Unit tests for typingtest.storage (file-backed, using tmp dirs)."""
import json
import tempfile
import unittest
from pathlib import Path

from typingtest.storage import (HistoryManager, SettingsManager, load_json,
                                save_json)


class TempsMixin:
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()


class TestJsonIO(TempsMixin, unittest.TestCase):
    def test_round_trip(self) -> None:
        path = self.dir / "data.json"
        save_json(path, {"a": [1, 2, 3]})
        self.assertEqual(load_json(path, {}), {"a": [1, 2, 3]})

    def test_missing_file_returns_default(self) -> None:
        sentinel = object()
        self.assertIs(load_json(self.dir / "nope.json", sentinel), sentinel)

    def test_corrupt_file_is_set_aside(self) -> None:
        path = self.dir / "broken.json"
        path.write_text("{ not json", encoding="utf-8")
        self.assertEqual(load_json(path, {"ok": True}), {"ok": True})
        self.assertTrue(
            (self.dir / "broken.json.corrupt").exists())
        self.assertFalse(path.exists())

    def test_atomic_write_cleans_temp(self) -> None:
        path = self.dir / "clean.json"
        save_json(path, {"x": 1})
        leftovers = list(self.dir.glob(".tmp-*"))
        self.assertEqual(leftovers, [])


class TestSettings(TempsMixin, unittest.TestCase):
    def test_defaults_when_empty(self) -> None:
        mgr = SettingsManager(self.dir / "settings.json")
        self.assertEqual(mgr.get("theme"), "dark")
        self.assertTrue(mgr.get("sound"))

    def test_persistence(self) -> None:
        path = self.dir / "settings.json"
        SettingsManager(path).set("theme", "light")
        self.assertEqual(SettingsManager(path).get("theme"), "light")

    def test_unknown_keys_ignored_from_disk(self) -> None:
        path = self.dir / "settings.json"
        path.write_text(json.dumps({"theme": "light", "evil": True}),
                        encoding="utf-8")
        mgr = SettingsManager(path)
        self.assertEqual(mgr.get("theme"), "light")
        self.assertIsNone(mgr.get("evil"))


class TestHistory(TempsMixin, unittest.TestCase):
    def _sample(self, wpm: float = 50.0, acc: float = 95.0,
                category: str = "Technology",
                date: str = "2026-01-01 10:00:00") -> dict:
        return {"date": date, "text_id": "t", "category": category,
                "difficulty": "medium", "test_mode": "Complete Text",
                "elapsed_time": 60.0, "wpm": wpm, "net_wpm": wpm - 2,
                "accuracy": acc, "errors": 3, "correct_chars": 400,
                "total_chars": 420, "text_length": 1400,
                "completion": 30.0, "grade": "B"}

    def test_add_and_reload(self) -> None:
        path = self.dir / "history.json"
        HistoryManager(path).add_result(self._sample())
        reloaded = HistoryManager(path)
        self.assertEqual(reloaded.count(), 1)
        self.assertEqual(reloaded.tests()[0]["wpm"], 50.0)

    def test_best_wpm_and_averages(self) -> None:
        mgr = HistoryManager(self.dir / "h.json")
        mgr.add_result(self._sample(wpm=40.0, acc=90.0,
                                    date="2026-01-01 10:00:00"))
        mgr.add_result(self._sample(wpm=60.0, acc=100.0,
                                    date="2026-01-01 10:01:00"))
        self.assertEqual(mgr.best_wpm(), 60.0)
        self.assertEqual(mgr.averages()["wpm"], 50.0)
        self.assertEqual(mgr.averages()["accuracy"], 95.0)

    def test_empty_averages(self) -> None:
        mgr = HistoryManager(self.dir / "h.json")
        self.assertEqual(mgr.best_wpm(), 0.0)
        self.assertEqual(mgr.averages()["wpm"], 0.0)

    def test_per_category(self) -> None:
        mgr = HistoryManager(self.dir / "h.json")
        mgr.add_result(self._sample(wpm=40.0, category="Code",
                                    date="2026-01-01 10:00:00"))
        mgr.add_result(self._sample(wpm=80.0, category="Code",
                                    date="2026-01-01 10:01:00"))
        mgr.add_result(self._sample(wpm=50.0, category="Science",
                                    date="2026-01-01 10:02:00"))
        cats = mgr.per_category()
        self.assertEqual(cats["Code"]["tests"], 2)
        self.assertEqual(cats["Code"]["wpm"], 60.0)
        self.assertEqual(cats["Science"]["tests"], 1)

    def test_mistakes_accumulate(self) -> None:
        from collections import Counter
        mgr = HistoryManager(self.dir / "h.json")
        mgr.add_result(self._sample(), mistakes=Counter({"e": 3, "t": 1}))
        mgr.add_result(self._sample(date="2026-01-01 10:05:00"),
                       mistakes=Counter({"e": 1}))
        self.assertEqual(mgr.mistakes()["e"], 4)
        self.assertEqual(mgr.mistakes()["t"], 1)

    def test_unlocks_recorded_once(self) -> None:
        mgr = HistoryManager(self.dir / "h.json")
        mgr.add_result(self._sample(), unlockable={"first_test"})
        first = mgr.unlocked_achievements()["first_test"]
        mgr.add_result(self._sample(date="2026-01-01 10:06:00"),
                       unlockable={"first_test"})
        self.assertEqual(mgr.unlocked_achievements()["first_test"], first)

    def test_on_change_listener(self) -> None:
        events = []
        mgr = HistoryManager(self.dir / "h.json")
        mgr.on_change(lambda: events.append(1))
        mgr.add_result(self._sample())
        mgr.clear()
        self.assertEqual(len(events), 2)
        self.assertEqual(mgr.count(), 0)

    def test_listener_failure_isolated(self) -> None:
        mgr = HistoryManager(self.dir / "h.json")

        def bad() -> None:
            raise RuntimeError("boom")

        mgr.on_change(bad)
        mgr.add_result(self._sample())  # must not raise
        self.assertEqual(mgr.count(), 1)

    def test_export_csv_and_json(self) -> None:
        mgr = HistoryManager(self.dir / "h.json")
        mgr.add_result(self._sample())
        json_path = self.dir / "out.json"
        csv_path = self.dir / "out.csv"
        mgr.export_json(json_path)
        mgr.export_csv(csv_path)
        exported = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(len(exported), 1)
        lines = csv_path.read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(lines), 2)  # header + row
        self.assertIn("wpm", lines[0])
        self.assertIn("50.0", lines[1])

    def test_corrupt_history_recovers_empty(self) -> None:
        path = self.dir / "history.json"
        path.write_text("not json at all", encoding="utf-8")
        mgr = HistoryManager(path)
        self.assertEqual(mgr.count(), 0)

    def test_import_legacy(self) -> None:
        legacy = self.dir / "advanced_typing_history.json"
        rows = [
            {"date": "2025-01-01 00:00:00", "text_number": 3,
             "test_mode": "60 seconds", "elapsed_time": 60.0, "wpm": 72.0,
             "net_wpm": 70.0, "accuracy": 97.0, "errors": 4,
             "total_chars": 400, "text_length": 1403, "completion": 28.5},
            "not a dict row",  # malformed rows are skipped
        ]
        legacy.write_text(json.dumps(rows), encoding="utf-8")
        mgr = HistoryManager(self.dir / "h.json")
        imported = mgr.import_legacy(legacy)
        self.assertEqual(imported, 1)
        self.assertEqual(mgr.count(), 1)
        self.assertEqual(mgr.tests()[0]["test_mode"], "60 seconds")
        self.assertEqual(mgr.tests()[0]["grade"], "A")
        # second import must not duplicate
        self.assertEqual(mgr.import_legacy(legacy), 0)
        self.assertTrue(legacy.exists())  # legacy file untouched


if __name__ == "__main__":
    unittest.main()
