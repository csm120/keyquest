import unittest

from modules import input_utils


class TestInputUtils(unittest.TestCase):
    def test_mod_ctrl_detects_mask(self):
        self.assertTrue(input_utils.mod_ctrl(input_utils.CTRL_MASK))
        self.assertFalse(input_utils.mod_ctrl(0))


if __name__ == "__main__":
    unittest.main()

