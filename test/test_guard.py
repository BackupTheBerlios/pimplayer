import pimp.core.common

import unittest
import data
import time


def guarded():return "guarded"
def notguarded():return "not guarded"

@pimp.core.common.Guard.locked
def test1 ():
    ret=notguarded()
    t=pimp.core.common.Guard.guard(guarded)
    if t:
        ret+=t
    return ret

@pimp.core.common.Guard.locked
def test2 ():
    return test1()


class TestGuard(unittest.TestCase):
    def test_guard(self):
        """ Try to call a nested guard """
        self.assertEqual(test1(),notguarded()+guarded())
        self.assertEqual(test2(),notguarded())

if __name__ == '__main__':
    unittest.main()

