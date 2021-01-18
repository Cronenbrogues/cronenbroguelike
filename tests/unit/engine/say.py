import io
import re
import unittest
from unittest.mock import call
from unittest.mock import patch

from engine.globals import G
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
    the returned values will be strings.

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
    return ''.join(reconstructed), ''.join(edits)


class InsayneTest(common.EngineTest):

    @patch("adventurelib.say")
    def test_add_newline(self, mock_say):
        say.insayne("nasty pervy voices", add_newline=True, insanity=0)
        mock_say.assert_has_calls([call.say(""), call.say("nasty pervy voices")], any_order=False)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_output_reconstructable(self, mock_stdout):
        original_text = (
            "When Gregor Samsa awoke one morning from unsettling dreams, "
            "he found himself changed in his bed into a monstrous vermin.")
        say.insayne(original_text, insanity=100)
        augmented = mock_stdout.getvalue()
        # adventurelib.say freely introduces newlines.
        augmented = re.sub(r'\n', r' ', augmented)
        reconstructed, _ = _sifted_edits(original_text, augmented)
        self.assertEqual(original_text, reconstructed)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_no_alteration_when_insanity_low(self, mock_stdout):
        original_text = "There is no death in all the world."
        say.insayne(original_text, insanity=0)
        augmented = mock_stdout.getvalue()
        # adventurelib.say freely introduces newlines.
        augmented = re.sub(r'\n', r' ', augmented)
        _, edits = _sifted_edits(original_text, augmented)
        edited_edits = re.sub(r'\s*', r'', edits)
        self.assertEqual('', edited_edits)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_sets_zalgochance_when_insanity_high(self, mock_stdout):
        # TODO: Refactor the zalgotext library to be more testable.
        original_text = "some text"
        say.insayne(original_text, insanity=100)
        augmented = mock_stdout.getvalue()
        # adventurelib.say freely introduces newlines.
        augmented = re.sub(r'\n', r' ', augmented)
        _, edits = _sifted_edits(original_text, augmented)
        edited_edits = re.sub(r'[A-Z]*', r'', edits)
        self.assertNotEqual('', edited_edits)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_sets_zalgochance_when_insanity_high(self, mock_stdout):
        # TODO: Refactor the zalgotext library to be more testable.
        original_text = "some text"
        say.insayne(original_text, insanity=100)
        augmented = mock_stdout.getvalue()
        # adventurelib.say freely introduces newlines.
        augmented = re.sub(r'\n', r' ', augmented)
        _, edits = _sifted_edits(original_text, augmented)
        edited_edits = re.sub(r'[A-Z]*', r'', edits)
        self.assertNotEqual(edits, '')

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_interpolates_voices_when_insanity_high(self, mock_stdout):
        # TODO: Refactor the zalgotext library to be more testable.
        original_text = "no, not a text, not a text at all"
        say.insayne(original_text, insanity=100)
        augmented = mock_stdout.getvalue()
        # adventurelib.say freely introduces newlines.
        augmented = re.sub(r'\n', r' ', augmented)
        _, edits = _sifted_edits(original_text, augmented)
        edited_edits = re.sub(r'[^A-Z]*', r'', edits)
        with open('/tmp/output.txt', 'w') as outp:
            outp.write(mock_stdout.getvalue())
        self.assertIsNotNone(re.search(
                r"^(HEEEHEHEHEHEHE|THEREISNOHOPE|DIDYOUHEARTHAT?"
                "|IPROMISEYOUKNOWLEDGE)+$", edited_edits))

    @patch("adventurelib.say")
    @patch("engine.say._hear_voices")
    def test_player_insanity_used_by_default(self, mock_hear_voices, _):
        G.player.insanity.modify(20)
        self.assertEqual(20, G.player.insanity.value)
        say.insayne("")
        mock_hear_voices.assert_called_once_with("", G.player.insanity.value)
