import unittest

from gui2.scratch import STATUS_ACTIVE, STATUS_HIDDEN, STATUS_OUT_OF_SCREEN, Object, ObjectGroup


class TestScratchObjects(unittest.TestCase):
    def test_metadata_change_triggers_gui_sync(self):
        obj = Object()
        events = []
        obj.bind_gui_sync(lambda changed: events.append(changed.metadata["x"]))
        obj.set_position(12, 3)
        self.assertEqual(events[-1], 12)

    def test_out_of_screen_and_active_switching(self):
        obj = Object()
        obj.set_viewport(0, 0, 100, 100).set_position(200, 10)
        self.assertEqual(obj.status, STATUS_OUT_OF_SCREEN)
        obj.set_position(20, 10)
        self.assertEqual(obj.status, STATUS_ACTIVE)

    def test_hide_show_preserves_metadata_and_restores_state(self):
        obj = Object().set_viewport(0, 0, 100, 100).set_position(20, 20)
        obj.hide()
        obj.set_meta("x", 220)
        self.assertEqual(obj.status, STATUS_HIDDEN)
        obj.show()
        self.assertEqual(obj.status, STATUS_OUT_OF_SCREEN)

    def test_set_meta_clamps_negative_size_values(self):
        obj = Object().set_meta("width", -10).set_meta("height", -20)
        self.assertEqual(obj.get_meta("width"), 0.0)
        self.assertEqual(obj.get_meta("height"), 0.0)

    def test_object_group_inherits_object_and_propagates_viewport(self):
        group = ObjectGroup()
        child = Object().set_position(999, 10)
        group.add(child).set_viewport(0, 0, 100, 100)
        self.assertIsInstance(group, Object)
        self.assertEqual(child.status, STATUS_OUT_OF_SCREEN)

    def test_callbacks_can_be_set_from_plain_python_functions(self):
        obj = Object()

        def click_handler(value):
            return value + 1

        returned = obj.on_click(click_handler)
        self.assertIs(returned, click_handler)
        self.assertEqual(obj.trigger_click(41), 42)

    def test_callbacks_can_also_use_decorator_style(self):
        obj = Object()

        @obj.on_click()
        def click_handler():
            return "ok"

        self.assertEqual(click_handler(), "ok")
        self.assertEqual(obj.trigger_click(), "ok")

    def test_callbacks_can_use_decorator_without_parentheses(self):
        obj = Object()

        @obj.on_click
        def click_handler():
            return "plain"

        self.assertEqual(click_handler(), "plain")
        self.assertEqual(obj.trigger_click(), "plain")


if __name__ == "__main__":
    unittest.main()
