# this is a test to run independently of the rest of the tests
# pytest couldn't test the keyboard inputs so it was better to remove them
import unittest
import os
from key_press import KeyboardInput
import time

class TestKeyboardInputIntegration(unittest.TestCase):
    def setUp(self):
        self.keyboard = KeyboardInput()

    def test_keyboard_input_timeout(self):
        """
        This test verifies that keyboard input properly times out.
        No actual keypress needed.
        """
        start_time = time.time()
        result = self.keyboard.check_for_key(timeout=0.1)
        end_time = time.time()
        
        self.assertIsNone(result)
        self.assertLess(end_time - start_time, 0.2)  # Ensure timeout works

    def test_keyboard_input_manual(self):
        """
        This test requires manual intervention.
        Run this separately from automated tests.
        """
        if not os.environ.get('MANUAL_TEST_MODE'):
            self.skipTest("Skipping manual keyboard test")

        print("\nPlease press any key within 2 seconds...")
        result = self.keyboard.check_for_key(timeout=2)
        self.assertIsNotNone(result)

if __name__ == '__main__':
    # To run manual tests:
    # MANUAL_TEST_MODE=1 python -m unittest keyboard_test.py
    unittest.main()
