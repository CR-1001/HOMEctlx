# This file is part of HomeCtl. Copyright (C) 2024 Christian Rauch.
# Distributed under terms of the GPL3 license.

import unittest
import services.ambinterpreter as ami
from services.lightstates import State


# TODO: more tests


class Test_ambinterpreter(unittest.TestCase):
    """ Tests the ambscript interpreter."""

    states_changed = []
    states = [
        State("1 on   0     20   50  a"),
        State("2 off  30    21  100  b"),
        State("3 on   120  100   52  c"),
        State("4 off  360   22   52  d"),
        State("5 on   -      -   52  e"),
    ]


    def test_asterisk(self):
        """ Test the asterisk (all devices)."""
        changed_ids = set()
        ami._interpret_tokens(["* on"], self.states, changed_ids)
        self.assertIs(changed_ids, set([1, 2, 3, 4, 5]))


if __name__ == '__main__':
    unittest.main()