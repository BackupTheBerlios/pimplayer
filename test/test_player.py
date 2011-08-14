import pimp.core.common
import pimp.core.player
import unittest
import data
import time

class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.instance = pimp.core.player.Player()
        
    def tearDown(self):
        self.instance.quit()
        
    def test_load_random_data(self):
        self.assertFalse(self.instance.load(data.file_random))

    def test_load_not_exist(self):
        self.assertFalse(self.instance.load(data.file_not_exist))

    def test_load_valid(self):
        self.assertTrue(self.instance.load(data.file_valid))

    def test_duration(self):
        self.instance.load(data.file_valid)
        self.assertEqual(self.instance.information()['duration'],365)
        
    def test_stress_load(self):
        """ To test a lot of load calls """
        print "This test can take some times ... please wait!"
        for k in range(1,10000):
            self.assertTrue(self.instance.load(data.file_valid))
            self.assertFalse(self.instance.load(data.file_not_exist))

    def test_state(self):
        self.instance.stop()
        self.instance.load(data.file_valids[0])
        self.instance.waitReady()
        self.instance.seek(40)
        s1=self.instance.__getstate__()

        self.instance.stop()
        self.instance.load(data.file_valids[1])
        self.instance.waitReady()
        s2=self.instance.__getstate__()
        self.instance.stop()
        print "STOP Done"
        self.assertTrue(self.instance.__setstate__(s1))
        self.instance.waitReady()
        s3=self.instance.__getstate__()
        self.assertEqual(s3,s1)
        

if __name__ == '__main__':
    unittest.main()
