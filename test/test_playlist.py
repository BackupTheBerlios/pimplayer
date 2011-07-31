import pimp.core.playlist
import unittest
import data
import pimp.core.song

class TestSong():
    def __init__(self,path):self.path=path
    def __repr__(self):return self.path


class TestPlaylist(unittest.TestCase):
    def setUp(self):pass
    
    def test_first(self):
        self.assertEqual(pimp.core.playlist.Playlist(TestSong,data.playlist)[0].path, data.playlist[0])

    def test_next(self):
        p=pimp.core.playlist.Playlist(TestSong,data.playlist)
        self.assertEqual(p.getNext(True).path,data.playlist[1])
        self.assertEqual(p.getNext(False).path,data.playlist[2])
        self.assertEqual(p.getNext(False).path,data.playlist[2])
        del p

    def test_prev(self):
        p=pimp.core.playlist.Playlist(TestSong,data.playlist)
        self.assertEqual(p.getPrev(True).path,data.playlist[len(data.playlist)-1])
        self.assertEqual(p.getPrev(False).path,data.playlist[len(data.playlist)-2])
        self.assertEqual(p.getPrev(False).path,data.playlist[len(data.playlist)-2])


    def test_random_file(self):
        p=pimp.core.playlist.Playlist(pimp.core.song.Song,[data.file_random])
        self.assertEqual(p.length(),0)






if __name__ == '__main__':
    unittest.main()
