"""Unit tests for typingtest.textbank and the bundled data file."""
import json
import tempfile
import unittest
from pathlib import Path

from typingtest import config
from typingtest.textbank import (CUSTOM_CATEGORY, TextBank,
                                 VALID_DIFFICULTIES)


class TestBundledData(unittest.TestCase):
    """The shipped texts.json must be valid and well-formed."""

    @classmethod
    def setUpClass(cls) -> None:
        with open(config.BUNDLED_TEXTS, encoding="utf-8") as fh:
            cls.payload = json.load(fh)

    def test_has_texts(self) -> None:
        self.assertGreaterEqual(len(self.payload["texts"]), 49)

    def test_schema_fields(self) -> None:
        for entry in self.payload["texts"]:
            self.assertIn("id", entry)
            self.assertIn("category", entry)
            self.assertIn(entry["difficulty"], VALID_DIFFICULTIES)
            self.assertGreater(len(entry["text"]), 100)

    def test_unique_ids(self) -> None:
        ids = [t["id"] for t in self.payload["texts"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_all_difficulties_present(self) -> None:
        diffs = {t["difficulty"] for t in self.payload["texts"]}
        self.assertEqual(diffs, set(VALID_DIFFICULTIES))

    def test_code_category_exists(self) -> None:
        self.assertTrue(any(t["category"] == "Code"
                            for t in self.payload["texts"]))


class BankMixin:
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        tmp = Path(self._tmp.name)
        self.data = tmp / "texts.json"
        self.custom = tmp / "custom.json"
        entries = [
            {"id": "a", "category": "Code", "difficulty": "easy",
             "text": "print('hello world') and some more words here"},
            {"id": "b", "category": "Code", "difficulty": "hard",
             "text": "x = [y for y in range(100) if y % 3 == 0] # foo bar"},
            {"id": "c", "category": "Nature", "difficulty": "easy",
             "text": "the quick brown fox jumps over the lazy dog today"},
            {"id": "d", "category": "Tech", "difficulty": "medium",
             "text": "computers process information in binary form daily"},
        ]
        self.data.write_text(
            json.dumps({"version": 2, "texts": entries}), encoding="utf-8")
        self.bank = TextBank(data_path=self.data, custom_path=self.custom)

    def tearDown(self) -> None:
        self._tmp.cleanup()


class TestTextBank(BankMixin, unittest.TestCase):
    def test_loads_all_entries(self) -> None:
        self.assertEqual(len(self.bank.all), 4)
        self.assertEqual(self.bank.total_texts, 4)

    def test_categories(self) -> None:
        self.assertEqual(set(self.bank.categories),
                         {"Code", "Nature", "Tech"})

    def test_filter_by_difficulty(self) -> None:
        easy = self.bank.filter(difficulty="easy")
        self.assertEqual(len(easy), 2)
        self.assertTrue(all(e.difficulty == "easy" for e in easy))

    def test_filter_by_category(self) -> None:
        code = self.bank.filter(category="Code")
        self.assertEqual(len(code), 2)

    def test_filter_all_is_unfiltered(self) -> None:
        self.assertEqual(len(self.bank.filter("All", "All")), 4)

    def test_pick_never_repeats_immediately(self) -> None:
        picks = [self.bank.pick().id for _ in range(8)]
        for first, second in zip(picks, picks[1:]):
            self.assertNotEqual(first, second)

    def test_pick_with_filters(self) -> None:
        entry = self.bank.pick(difficulty="easy", category="Code")
        self.assertEqual(entry.id, "a")

    def test_pick_relaxes_impossible_filters(self) -> None:
        # difficulty hard + category Tech matches nothing -> graceful pool
        entry = self.bank.pick(difficulty="hard", category="Tech")
        self.assertIn(entry.id, {"a", "b", "c", "d"})

    def test_missing_data_file_raises(self) -> None:
        from typingtest.textbank import TextBankError
        with self.assertRaises(TextBankError):
            TextBank(data_path=self.data.parent / "missing.json",
                     custom_path=self.custom)


class TestCustomTexts(BankMixin, unittest.TestCase):
    LONG = "word " * 40

    def test_add_and_persist(self) -> None:
        entry = self.bank.add_custom(self.LONG)
        self.assertEqual(entry.category, CUSTOM_CATEGORY)
        reloaded = TextBank(data_path=self.data, custom_path=self.custom)
        self.assertEqual(len(reloaded.custom_entries), 1)
        self.assertIn(CUSTOM_CATEGORY, reloaded.categories)

    def test_rejects_short_text(self) -> None:
        with self.assertRaises(ValueError):
            self.bank.add_custom("too short")

    def test_rejects_long_text(self) -> None:
        with self.assertRaises(ValueError):
            self.bank.add_custom("x" * 5000)

    def test_remove_custom(self) -> None:
        entry = self.bank.add_custom(self.LONG)
        self.assertTrue(self.bank.remove_custom(entry.id))
        self.assertFalse(self.bank.remove_custom(entry.id))
        reloaded = TextBank(data_path=self.data, custom_path=self.custom)
        self.assertEqual(reloaded.custom_entries, [])

    def test_custom_included_in_pool(self) -> None:
        self.bank.add_custom(self.LONG)
        entry = self.bank.pick(category=CUSTOM_CATEGORY)
        self.assertEqual(entry.category, CUSTOM_CATEGORY)


if __name__ == "__main__":
    unittest.main()
