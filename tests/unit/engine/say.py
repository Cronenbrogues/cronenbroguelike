import unittest
from unittest.mock import patch

from engine import say
from tests import common


def _to_generator(string):
    for character in string:
        yield character


def _sifted_edits(original, augmented):
    """Reconstructs original from augmented by removing characters.

    If original is a disjoint substring of augmented (i.e., if a series of
    addition edits/interpolations can get from original to augmented), this
    method returns the tuple (original, edits).

    Otherwise, this method will return the longest left substring that can be
    so reconstructed and all edits encountered up to that point. In either case,
    the returned values will be lists of characters.

    This is equivalent to assessing that the edit distance between the two
    strings consists only in a series of additions (not removals or
    substitutions).
    """
    reconstructed = []
    edits = []

    aug_gen = _to_generator(augmented)

    for oc in original:
        while True:
            try:
                next_aug = next(aug_gen)
            except StopIteration:
                break
            if oc == next_aug:
                reconstructed.append(next_aug)
                break
            else:
                edits.append(next_aug)

    # Captures any remaining characters.
    edits.extend(aug_gen)
    return reconstructed, edits


class InsayneTest(common.EngineTest):

    @patch("adventurelib.say")
    def test_add_newline(self, mock_say):
        say.insayne("nasty pervy voices", add_newline=True, insanity=0)
        mock_say.assert_called_with("")
        mock_say.assert_called_with("nasty pervy voices")

    def test_sift(self):
        a, b = _sifted_edits('hello', 'hasdfekldfdloz')
        self.assertEqual(list('hello'), a)
        self.assertEqual(list('asdfkdfdz'), b)

        c, d = _sifted_edits('hello', 'ghoodbyesdfsdf')
        self.assertEqual(list('he'), c)
        self.assertEqual(list('goodbysdfsdf'), d)
