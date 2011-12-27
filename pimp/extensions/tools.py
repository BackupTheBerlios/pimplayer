import db
import playlist

def LastPlayed(number=None,til=None):
    ret=db.Play.Last()
    
    p=playlist.Playlist()
    for e in ret:
        p.append(e.file.path)
    return p

    
