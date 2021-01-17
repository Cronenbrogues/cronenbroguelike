import unittest
from unittest.mock import patch

from engine import event
from engine.globals import G
from tests import common


class EventTest(common.EngineTest):
    
    def test_will_execute(self):
        occurrence = event.Event()
        self.assertTrue(occurrence.will_execute)
        occurrence.kill()
        self.assertFalse(occurrence.will_execute)
