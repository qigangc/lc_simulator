import unittest

from lc.problems import solution_filename


class SolutionFilenameTests(unittest.TestCase):
    def test_pads_single_digit_id_to_three_digits(self):
        problem = {"id": 1, "slug": "two-sum"}
        self.assertEqual(solution_filename(problem), "001_two_sum.py")

    def test_keeps_three_digit_id_without_extra_padding(self):
        problem = {"id": 100, "slug": "word-ladder"}
        self.assertEqual(solution_filename(problem), "100_word_ladder.py")

    def test_replaces_all_dashes_in_slug(self):
        problem = {"id": 8, "slug": "letter-combinations-of-a-phone-number"}
        self.assertEqual(solution_filename(problem), "008_letter_combinations_of_a_phone_number.py")

    def test_slug_without_dashes_stays_unchanged(self):
        problem = {"id": 28, "slug": "climbing"}
        self.assertEqual(solution_filename(problem), "028_climbing.py")


if __name__ == "__main__":
    unittest.main()
