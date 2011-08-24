from pimp.core.playlist import *
import unittest
import data
import pimp.core.song

pimp.core.common.Log.toggle_stdout()

class TestSong():
    def __init__(self,path):self.path=path
    def __repr__(self):return self.path


class TestPlaylist(unittest.TestCase):
    def setUp(self):pass
    
    def test_first(self):
        self.assertEqual(Playlist(TestSong,data.playlist)[0].path, data.playlist[0])

    def test_next(self):
        p=Playlist(TestSong,data.playlist)
        self.assertEqual(p.getNext(True).path,data.playlist[1])
        self.assertEqual(p.getNext(False).path,data.playlist[2])
        self.assertEqual(p.getNext(False).path,data.playlist[2])
        del p

    def test_prev(self):
        p=Playlist(TestSong,data.playlist)
        self.assertEqual(p.getPrev(True).path,data.playlist[len(data.playlist)-1])
        self.assertEqual(p.getPrev(False).path,data.playlist[len(data.playlist)-2])
        self.assertEqual(p.getPrev(False).path,data.playlist[len(data.playlist)-2])


    def test_random_file(self):
        p=Playlist(pimp.core.song.Song,[data.file_random])
        self.assertEqual(len(p),0)

    def test_current(self):
        p=Playlist(TestSong,data.playlist)
        p.getNext(True)
        self.assertEqual(p.current().path,data.playlist[1])


    def test_methods(self):
        p=Playlist(TestSong,data.playlist)
        p.information()
        p.show()
        p.getNext(True)
        p.getNext(True)
        p.show(3)


if __name__ == '__main__':
    unittest.main()
