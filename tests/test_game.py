import tempfile
import unittest
from pathlib import Path

from game import Game, RuleError


class GameTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.clock = [1000.0]
        self.path = Path(self.tmp.name) / 'world.sqlite3'
        self.game = Game(self.path, clock=lambda: self.clock[0])
        self.token = self.game.join('Maple', 'dog')

    def state(self):
        return self.game.state(self.token)

    def move(self, x, y):
        self.clock[0] += 10
        return self.game.action(self.token, 'move', {'x': x, 'y': y})

    def test_join_and_session_validation(self):
        state = self.state()
        self.assertEqual(state['player']['name'], 'Maple')
        self.assertEqual(state['player']['coins'], 30)
        self.assertEqual(state['player']['inventory']['wood'], 2)
        with self.assertRaises(RuleError):
            self.game.state('not-a-session')

    def test_movement_cannot_teleport_or_use_nan(self):
        with self.assertRaises(RuleError):
            self.game.action(self.token, 'move', {'x': 1100, 'y': 600})
        with self.assertRaises(RuleError):
            self.game.action(self.token, 'move', {'x': float('nan'), 'y': 300})

    def test_gather_requires_proximity_and_cooldown(self):
        with self.assertRaises(RuleError):
            self.game.action(self.token, 'gather', {'node': 'sun-wood'})
        self.move(240, 300)
        self.game.action(self.token, 'gather', {'node': 'sun-wood'})
        self.assertEqual(self.state()['player']['inventory'].get('wood'), 4)
        with self.assertRaises(RuleError):
            self.game.action(self.token, 'gather', {'node': 'sun-wood'})

    def test_travel_requires_portal_and_changes_world(self):
        with self.assertRaises(RuleError):
            self.game.action(self.token, 'travel', {})
        self.move(1050, 385)
        self.game.action(self.token, 'travel', {})
        self.assertEqual(self.state()['player']['world'], 'penguin')
        self.assertEqual(self.state()['player']['stats']['visits_penguin'], 1)

    def test_craft_is_atomic_and_checks_materials(self):
        self.move(540, 250)
        before = self.state()['player']['inventory']
        with self.assertRaises(RuleError):
            self.game.action(self.token, 'craft', {'recipe': 'lantern'})
        self.assertEqual(self.state()['player']['inventory'], before)
        self.game.action(self.token, 'craft', {'recipe': 'stool'})
        self.assertEqual(self.state()['player']['inventory']['stool'], 1)
        self.assertEqual(self.state()['player']['inventory']['wood'], 0)

    def test_quest_claim_cannot_repeat_or_claim_early(self):
        with self.assertRaises(RuleError):
            self.game.action(self.token, 'claim', {'quest': 'berry-trail'})
        self.move(760, 300)
        self.game.action(self.token, 'gather', {'node': 'sun-berries'})
        self.game.action(self.token, 'claim', {'quest': 'berry-trail'})
        self.assertEqual(self.state()['player']['coins'], 45)
        with self.assertRaises(RuleError):
            self.game.action(self.token, 'claim', {'quest': 'berry-trail'})

    def test_fishing_is_timed_and_replay_safe(self):
        self.move(320, 540)
        challenge = self.game.action(self.token, 'fish-start', {})['challenge']
        self.clock[0] = challenge['target_at']
        result = self.game.action(self.token, 'fish-catch', {'challenge': challenge['id']})
        self.assertTrue(result['caught'])
        self.assertEqual(self.state()['player']['inventory']['fish'], 2)
        with self.assertRaises(RuleError):
            self.game.action(self.token, 'fish-catch', {'challenge': challenge['id']})

    def test_fishing_miss_awards_nothing(self):
        self.move(320, 540)
        challenge = self.game.action(self.token, 'fish-start', {})['challenge']
        result = self.game.action(self.token, 'fish-catch', {'challenge': challenge['id']})
        self.assertFalse(result['caught'])
        self.assertEqual(self.state()['player']['inventory'].get('fish', 0), 0)

    def test_gift_rejects_negative_and_self_transfer(self):
        other = self.game.join('Pebble', 'penguin')
        target = self.game.state(other)['player']['id']
        for qty in (-1, 0, 999, True):
            with self.assertRaises(RuleError):
                self.game.action(self.token, 'gift', {'target': target, 'item': 'wood', 'qty': qty})
        self.game.action(self.token, 'gift', {'target': target, 'item': 'wood', 'qty': 1})
        self.assertEqual(self.game.state(other)['player']['inventory'].get('wood'), 3)
        self.assertEqual(self.state()['player']['inventory']['wood'], 1)
        with self.assertRaises(RuleError):
            self.game.action(self.token, 'gift', {'target': self.state()['player']['id'], 'item': 'wood', 'qty': 1})

    def test_home_and_session_persist_across_restart(self):
        self.move(540, 250)
        self.game.action(self.token, 'craft', {'recipe': 'stool'})
        self.game.action(self.token, 'decorate', {'slot': 0, 'item': 'stool'})
        restarted = Game(self.path, clock=lambda: self.clock[0])
        self.assertEqual(restarted.state(self.token)['player']['home'][0], 'stool')
        self.game.action(self.token, 'decorate', {'slot': 0, 'item': ''})
        self.assertEqual(self.state()['player']['inventory']['stool'], 1)

    def test_unknown_actions_and_slots_are_rejected(self):
        for action, args in [('fly', {}), ('decorate', {'slot': -1, 'item': 'stool'}),
                             ('decorate', {'slot': True, 'item': ''})]:
            with self.assertRaises(RuleError):
                self.game.action(self.token, action, args)


if __name__ == '__main__':
    unittest.main()
