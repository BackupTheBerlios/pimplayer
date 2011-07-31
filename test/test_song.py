import pimp.core.common
import pimp.core.song
import unittest
import data
import time

class TestSong(unittest.TestCase):

    def test_create(self):
        self.assertEqual(pimp.core.song.Song(data.file_valid).path,data.file_valid)

    def test_create_random(self):
        self.assertRaises(pimp.core.common.FileNotSupported,pimp.core.song.Song,data.file_random)

    def test_create_not_exist(self):
        self.assertRaises(pimp.core.common.FileNotSupported,pimp.core.song.Song,data.file_not_exist)

if __name__ == '__main__':
    unittest.main()
