import unittest

from gui2.scratch import Stage


class TestScratchLayer(unittest.TestCase):
    def test_when_flag_clicked_script_uses_block_api(self):
        stage = Stage()
        script = stage.when_flag_clicked().move_steps(10).turn_right_degrees(15).say("Hello")

        self.assertIn("event_whenflagclicked", stage.scripts_by_event)
        self.assertEqual(
            [(b.opcode, b.args) for b in script.blocks],
            [
                ("motion_move_steps", (10,)),
                ("motion_turn_right", (15,)),
                ("looks_say", ("Hello",)),
            ],
        )


if __name__ == "__main__":
    unittest.main()
