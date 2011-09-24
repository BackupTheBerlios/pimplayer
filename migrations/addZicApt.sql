UPDATE evt_play, file SET evt_play.zicApt=file.zicApt WHERE evt_play.fileId=file.id ;
UPDATE evt_stop, file SET evt_stop.zicApt=file.zicApt WHERE evt_stop.fileId=file.id ;
UPDATE evt_seek, file SET evt_seek.zicApt=file.zicApt WHERE evt_seek.fileId=file.id ;
UPDATE evt_pause, file SET evt_pause.zicApt=file.zicApt WHERE evt_pause.fileId=file.id ;
UPDATE note, file SET note.zicApt=file.zicApt WHERE note.fileId=file.id ;
UPDATE comment, file SET comment.zicApt=file.zicApt WHERE comment.fileId=file.id ;


