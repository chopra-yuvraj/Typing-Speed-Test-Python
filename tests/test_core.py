"""Unit tests for typingtest.core (pure logic — no GUI)."""
import unittest

from typingtest.core import (CharStatus, Grade, TestResult, TypingEngine,
                             accuracy, evaluate_achievements, grade_for,
                             gross_wpm, net_wpm)


class FakeClock:
    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        return self.t

    def advance(self, seconds: float) -> None:
        self.t += seconds


class TestMetrics(unittest.TestCase):
    def test_gross_wpm_standard(self) -> None:
        # 300 chars in 60s -> 60 WPM
        self.assertAlmostEqual(gross_wpm(300, 60), 60.0)

    def test_gross_wpm_zero_elapsed(self) -> None:
        self.assertEqual(gross_wpm(100, 0), 0.0)

    def test_net_wpm_penalizes_errors(self) -> None:
        # 60 correct chars in 30s = 24 WPM gross; 1 error in 30s = -2
        self.assertAlmostEqual(net_wpm(60, 1, 30), 22.0)

    def test_net_wpm_never_negative(self) -> None:
        self.assertEqual(net_wpm(0, 500, 60), 0.0)

    def test_accuracy(self) -> None:
        self.assertAlmostEqual(accuracy(9, 10), 90.0)
        self.assertEqual(accuracy(0, 0), 100.0)

    def test_accuracy_floor_zero(self) -> None:
        self.assertEqual(accuracy(0, 0, floor=0.0), 0.0)

    def test_grade_boundaries(self) -> None:
        self.assertEqual(grade_for(95, 99), Grade.S)
        self.assertEqual(grade_for(75, 96), Grade.A)
        self.assertEqual(grade_for(55, 93), Grade.B)
        self.assertEqual(grade_for(35, 87), Grade.C)
        self.assertEqual(grade_for(10, 50), Grade.D)


class TestEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = FakeClock()
        self.engine = TypingEngine("hello world", clock=self.clock)

    def test_initial_state(self) -> None:
        self.assertFalse(self.engine.running)
        stats = self.engine.stats()
        self.assertEqual(stats.total_typed, 0)
        self.assertEqual(stats.progress, 0.0)
        self.assertEqual(stats.accuracy, 100.0)
        self.assertEqual(self.engine.statuses[0], CharStatus.CURRENT)

    def test_update_correct_prefix(self) -> None:
        self.engine.begin()
        self.clock.advance(30)
        self.engine.update("hello")
        stats = self.engine.stats()
        self.assertEqual(stats.correct, 5)
        self.assertEqual(stats.incorrect, 0)
        # 5 correct chars in 30s -> (5/5)/0.5min = 2 WPM
        self.assertAlmostEqual(stats.gross_wpm, 2.0)

    def test_update_with_errors(self) -> None:
        self.engine.begin()
        self.engine.update("hexlo")
        self.assertEqual(self.engine.statuses[2], CharStatus.INCORRECT)
        stats = self.engine.stats()
        self.assertEqual(stats.correct, 4)
        self.assertEqual(stats.incorrect, 1)
        self.assertAlmostEqual(stats.accuracy, 80.0)

    def test_update_clamps_overflow(self) -> None:
        self.engine.begin()
        self.engine.update("hello world extra")
        self.assertEqual(self.engine.typed, "hello world")
        self.assertEqual(self.engine.stats().progress, 100.0)

    def test_is_finished_complete_mode(self) -> None:
        self.engine.begin()
        self.assertFalse(self.engine.is_finished())
        self.engine.update("hello world")
        self.assertTrue(self.engine.is_finished())

    def test_not_finished_with_errors(self) -> None:
        self.engine.begin()
        self.engine.update("hello worlx")  # one char wrong at the end
        self.assertFalse(self.engine.is_finished())

    def test_timed_mode_expires(self) -> None:
        clock = FakeClock()
        engine = TypingEngine("hello world", time_limit=10, clock=clock)
        engine.begin()
        clock.advance(11)
        self.assertTrue(engine.is_finished())
        self.assertEqual(engine.stats().remaining, 0.0)

    def test_remaining_before_start(self) -> None:
        engine = TypingEngine("abc", time_limit=60)
        self.assertEqual(engine.remaining(), 60)

    def test_reset_clears_state(self) -> None:
        self.engine.begin()
        self.engine.update("hello")
        self.engine.record_mistake("o", "p")
        self.engine.reset()
        self.assertFalse(self.engine.running)
        self.assertEqual(self.engine.typed, "")
        self.assertEqual(sum(self.engine.mistakes.values()), 0)

    def test_mistake_tracking(self) -> None:
        self.engine.record_mistake("e", "w")
        self.engine.record_mistake("e", "q")
        self.assertEqual(self.engine.mistakes["e"], 2)

    def test_validation(self) -> None:
        with self.assertRaises(ValueError):
            TypingEngine("")
        with self.assertRaises(ValueError):
            TypingEngine("text", time_limit=0)

    def test_finish_produces_result_dict(self) -> None:
        self.engine.begin()
        self.clock.advance(60)
        self.engine.update("hello world")
        result = self.engine.finish(
            text_id="t1", category="Technology", difficulty="medium",
            mode="Complete Text", timestamp="2026-01-01 10:00:00")
        data = result.to_dict()
        self.assertEqual(data["text_id"], "t1")
        self.assertEqual(data["completion"], 100.0)
        self.assertEqual(data["wpm"], round((11 / 5), 1))
        self.assertIn(data["grade"], ("S", "A", "B", "C", "D"))

    def test_finish_requires_begin_but_safe(self) -> None:
        # finishing without starting should not crash
        result = self.engine.finish(
            text_id="t", category="c", difficulty="medium",
            mode="m", timestamp="now")
        self.assertEqual(result.total_chars_typed, 0)


class TestResultRoundTrip(unittest.TestCase):
    def test_from_dict_round_trip(self) -> None:
        original = {
            "date": "2026-01-01 10:00:00", "text_id": "tech-01",
            "category": "Technology", "difficulty": "medium",
            "test_mode": "Complete Text", "elapsed_time": 90.0,
            "wpm": 55.5, "net_wpm": 50.1, "accuracy": 96.2, "errors": 12,
            "correct_chars": 500, "total_chars": 512, "text_length": 1403,
            "completion": 36.5, "grade": "B",
        }
        restored = TestResult.from_dict(original).to_dict()
        self.assertEqual(restored["grade"], "B")
        self.assertEqual(restored["wpm"], 55.5)
        self.assertEqual(restored["category"], "Technology")

    def test_from_legacy_dict(self) -> None:
        legacy = {
            "date": "2025-01-01 00:00:00", "text_number": 3,
            "test_mode": "60 seconds", "elapsed_time": 60.0, "wpm": 72.0,
            "net_wpm": 70.0, "accuracy": 97.0, "errors": 4,
            "total_chars": 400, "text_length": 1403, "completion": 28.5,
        }
        result = TestResult.from_dict(legacy)
        self.assertEqual(result.text_id, "3")
        self.assertEqual(result.grade, "A")  # recomputed from wpm/accuracy
        self.assertEqual(result.correct_chars, 400)


class TestAchievements(unittest.TestCase):
    def test_first_test_unlocks(self) -> None:
        result = {"wpm": 42.0, "accuracy": 96.0, "completion": 100.0,
                  "total_chars": 300}
        unlocked = {a.key: a for a in evaluate_achievements([result], 300, {})
                    if a.unlocked}
        self.assertIn("first_test", unlocked)
        self.assertIn("wpm_40", unlocked)
        self.assertNotIn("wpm_60", unlocked)

    def test_marathon_needs_chars(self) -> None:
        achievements = evaluate_achievements([], 49_999, {})
        self.assertFalse(achievements[10].unlocked)  # marathon
        achievements = evaluate_achievements([], 50_000, {})
        self.assertTrue(achievements[10].unlocked)

    def test_streak_achievement(self) -> None:
        tests = [{"wpm": 30, "accuracy": 96.0, "completion": 50.0}
                 for _ in range(5)]
        unlocked = {a.key for a in evaluate_achievements(tests, 1500, {})
                    if a.unlocked}
        self.assertIn("consistent", unlocked)

    def test_previously_unlocked_stay_unlocked(self) -> None:
        achievements = evaluate_achievements([], 0, {"wpm_100": "ts"})
        by_key = {a.key: a for a in achievements}
        self.assertTrue(by_key["wpm_100"].unlocked)

    def test_perfect_test(self) -> None:
        tests = [{"wpm": 101.0, "accuracy": 100.0, "completion": 100.0,
                  "total_chars": 1500}]
        unlocked = {a.key for a in evaluate_achievements(tests, 1500, {})
                    if a.unlocked}
        self.assertIn("flawless", unlocked)
        self.assertIn("wpm_100", unlocked)


if __name__ == "__main__":
    unittest.main()
