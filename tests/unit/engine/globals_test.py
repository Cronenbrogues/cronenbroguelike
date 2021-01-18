import unittest
from unittest.mock import Mock
from unittest.mock import patch

from engine import event
from engine import globals as _globals
from tests import common


class _FakeQueue:

    def __init__(self):
        self.pre = Mock()
        self.post = Mock()

    def __call__(self, which):
        if which == "pre":
            yield self.pre
        else:
            assert which == "post"
            yield self.post


class MoribundEvent(event.Event):

    def __init__(self, to_live):
        super().__init__()
        self._to_live = to_live

    def execute(self):
        self._to_live -= 1
        if self._to_live <= 0:
            self.kill()


class PollEventsTest(unittest.TestCase):
    
    @patch("engine.globals.G.events", new_callable=_FakeQueue)
    def test_poll_events(self, fake_queue):
        fake_queue.pre.execute.assert_not_called()
        with _globals.poll_events():
            fake_queue.post.execute.assert_not_called()
            fake_queue.pre.execute.assert_called()
        fake_queue.post.execute.assert_called()
            
    @patch("engine.globals.G.events", new_callable=_FakeQueue)
    def test_poll_events_select_polls(self, fake_queue):
        with _globals.poll_events(poll_before=False, poll_after=False):
            fake_queue.pre.execute.assert_not_called()
        fake_queue.post.execute.assert_not_called()


class GTest(unittest.TestCase):

    def setUp(self):
        _globals.G.reset()

    def test_add_event_pre(self):
        event = MoribundEvent(1)
        _globals.G.add_event(event, 'pre')
        self.assertEqual([event], list(_globals.G.events('pre')))

    def test_add_event_post(self):
        event = MoribundEvent(1)
        _globals.G.add_event(event, 'post')
        self.assertEqual([event], list(_globals.G.events('post')))

    def test_post_event_lives_a_full_life(self):
        event = MoribundEvent(2)
        _globals.G.add_event(event, 'post')
        self.assertEqual([event], list(_globals.G.events('post')))
        event.execute()
        self.assertEqual([event], list(_globals.G.events('post')))
        event.execute()

        # Event is now dead and should not be yielded by the event queue.
        self.assertEqual([], list(_globals.G.events('post')))

    def test_pre_event_lives_a_full_life(self):
        event = MoribundEvent(2)
        _globals.G.add_event(event, 'pre')
        self.assertEqual([event], list(_globals.G.events('pre')))
        event.execute()
        self.assertEqual([event], list(_globals.G.events('pre')))
        event.execute()

        # Event is now dead and should not be yielded by the event queue.
        self.assertEqual([], list(_globals.G.events('pre')))

    def test_reset(self):
        # Adds some state to the global G.
        _globals.G.current_room = Mock()
        _globals.G.player = Mock()
        _globals.G.cause_of_death = Mock()
        _globals.G.just_died = True
        _globals.G.add_event(MoribundEvent(2), "pre")
        _globals.G.add_event(MoribundEvent(2), "post")

        # Asserts that state is there.
        self.assertIsNotNone(_globals.G.current_room)
        self.assertIsNotNone(_globals.G.player)
        self.assertIsNotNone(_globals.G.cause_of_death)
        self.assertNotEqual(False, _globals.G.just_died)
        self.assertNotEqual([], list(_globals.G.events("pre")))
        self.assertNotEqual([], list(_globals.G.events("post")))

        # Resets and asserts that state is restored.
        _globals.G.reset()
        self.assertIsNone(_globals.G.current_room)
        self.assertIsNone(_globals.G.player)
        self.assertIsNone(_globals.G.cause_of_death)
        self.assertEqual(False, _globals.G.just_died)
        self.assertEqual([], list(_globals.G.events("pre")))
        self.assertEqual([], list(_globals.G.events("post")))
