""" To get information about system files """
#import subprocess #commands
import commands
from os.path import isfile,getmtime
import time
import datetime
import player

import common
import logging


def get_status_output(cmd, input=None, cwd=None, env=None):
    pipe = Popen(cmd, shell=True, cwd=cwd, env=env, stdout=PIPE, stderr=STDOUT)

    (output, errout) = pipe.communicate(input=input)
    assert not errout

    status = pipe.returncode

    return (status, output)


def type(path):
    """ Just 3 formats are supported : mp3 , flac , ogg
    TODO : Really shity ... """

    if not isfile(path) : 
        logging.info("'%s' is not a file" % path)
        return None
#    t = subprocess.check_output('gst-typefind-0.10 "%s"' % path)
#    t = commands.getstatusoutput('gst-typefind-0.10 "%s"' % path)
    t = get_status_output('gst-typefind-0.10 "%s"' % path)
    mimetype = t[1]
    if mimetype.find(" - FAILED:") != -1:
        logging.warning("File NOT supported by gst-typefind : %s" % path)
        return None
    else :
        logging.debug("mimetype of '%s' is %s" % (path,mimetype))

    if mimetype.find("audio/mpeg") != -1 or mimetype.find("application/x-id3") != -1:
        format='mp3'
    elif mimetype.find("application/ogg") != -1:
        format="ogg"
    elif mimetype.find("audio/x-flac") != -1:
        format="flac"
    else:
        logging.info("Format NOT supported by Pimp : %s ; %s" % (mimetype,path))
        format=None
    return format


def supported(path):
    """ To know if a file is supported by Pimp """
    return type(path) != None
        


from subprocess import *
import subprocess
def format_md5(path):
    format=type(path)
    if format == None : return None
    p1 = Popen(['sox -t %s "%s" -t wav -' % (format,path)], stdout=PIPE,stderr=PIPE,shell=True)
    p2 = Popen(["dd bs=1 count=%dkB |md5sum"% 500], stdin=p1.stdout , stdout=PIPE,stderr=PIPE, shell=True)
    p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
    output = p2.communicate()
    p1.wait()
    retcode=p1.returncode
#    p2.terminate() #useless ?
#    p1.terminate() #useless ?
    if retcode != 0 :
        logging.warning("Sox return a bad return code on file '%s'" % path)
        return None
    md5=output[0].split(" ")[0]
    logging.debug("format='%s' ; md5='%s' ; filepath='%s'" % (format,md5,path))
    return (format,md5)


def modification_date(path):
    if not isfile(path) : 
        logging.warning("Is not a file : %s " % path)
        return None
    return datetime.datetime.utcfromtimestamp(getmtime(path))
    
def duration(path):
    """ To get the duration of a file. """
    p=player.Player(path)
    dur=p.information()['duration']
    p.quit()
    return dur



import test    
if False : 
    test = ["~/tmp.a","/home/eiche/tmp.a","/home/eiche/20 - pourquoi_drunk.ogg","/home/eiche/destroyer.flac","/home/eiche/impd.log"]

    for t in test :
        print "\n--------------------------------------------------------------------------------"
        print "path : %s "%t
        print "(format,md5): " , format_md5(t)
        print "modification_date: " , modification_date(t)
        print "duration: " , duration(t)
    

