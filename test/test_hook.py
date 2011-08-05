import pimp.core.common

import unittest
import data
import time


class HookException(Exception):pass
""" Just to make some basic test. Because handler return nothing, we
emit an exception instead.
"""

def emit1():raise HookException("emit1")
def emit2():raise HookException("emit2")

class TestHook1(object):
    __metaclass__=pimp.core.common.Hook
    print "Entering in Test definition"
    def __init__(self):self.a=1
    
    @pimp.core.common.Hook.HookMethod
    def get(self):pass

    
class TestHook2(object):
    __metaclass__=pimp.core.common.Hook
    @pimp.core.common.Hook.HookMethod
    def get(self):pass

class NeestedHook(object):
    __metaclass__=pimp.core.common.Hook
    @pimp.core.common.Hook.HookMethod
    def get(self):
        return TestHook1().get()
    

def handle1(): print "Callback function handle1() call"
def handle2(): print "Callback function handle2() call"


class TestHook(unittest.TestCase):
    def test_one(self):
        """Try to hook a class method and add a handler"""
        TestHook1.AddHandler(TestHook1.get,emit1)
        try :
            TestHook1().get()
        except HookException as e :
            self.assertEqual(str(e),"emit1")
        else: return False

    def test_many(self):
        """Try to hook two methods of different class, add different handlers to them"""
        TestHook1.AddHandler(TestHook1.get,emit1)
        TestHook2.AddHandler(TestHook2.get,emit2)
        try :
            TestHook1().get()
        except HookException as e :
            self.assertEqual(str(e),"emit1")
        else : return False
        try :
            TestHook2().get()
        except HookException as e :
            self.assertEqual(str(e),"emit2")
        else: return False

    def test_neested(self):
        """\nTry to hook neested hook method"""
        TestHook1.AddHandler(TestHook1.get,emit1)
        NeestedHook.AddHandler(NeestedHook.get,handle2)
        try :
            NeestedHook().get()
        except : self.fail()



if __name__ == '__main__':
    unittest.main()

