#!/usr/bin/env python

# Pimp is a highly interactive music player.
# Copyright (C) 2011 kedals0@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Some futur example
# $ pimpc search format:mp3 folder:zic filename:test
# $ pimpc enqueue format:mp3 folder:zic filename:test
# $ pimpc note 4 format:mp3 folder:zic filename:test
# $ pimpc comment un_comment format:mp3 folder:zic filename:test
import Pyro4
Pyro4.config.HMAC_KEY="pimp"

import pimp.core.common
import pimp.core.playlist
import pimp.core.song
import pimp.core.db

import argparse

import sys 
def pprint(a):
    if type(a) is list:
        if args.print0 == True:
            acc=""
            for i in a:
                acc+=i+'\0'
            sys.stdout.write(acc)
        else:
            for i in a : print i
    elif type(a) is dict or type(a) is pimp.core.common.Info:
        for k,e in a.items():
            print str(k) +'\t' + str(e)
    elif type(a) is pimp.core.song.Song:
        print a.getPath()

def cmd_player(args):
    player=Pyro4.Proxy("PYRO:player@localhost:%d"%args.port)          # get a Pyro proxy to the greeting object
    if args.enqueue != None:
        print "Enqueue " + str(args.enqueue)
        try:
            map(player.appendByPath,args.enqueue)
        except pimp.core.common.FileNotSupported as e : 
            print "FileNotSupported: "+ str(e)
            exit(1)
    elif args.play != None:
        print "Play [NOT IMPLEMENTED] " + str(args.play)
    elif args.next :
        print "Next [NOT IMPLEMENTED] "
    elif args.info :
        pprint(player.information())
    elif args.current :
        pprint(player.current())
    elif args.playlist :
        pprint(map(pimp.core.song.Song.getPath,player.__getslice__(1,player.__len__())))

def cmd_note(args):
    Note=Pyro4.Proxy("PYRO:Note@localhost:%d"%args.port)          # get a Pyro proxy to the greeting object
    if args.files != None and args.files != []:
        pathfiles=args.files
        if args.add != None:
            print map(lambda f : Note.Add(f,args.add),pathfiles)
        else:
            notes=map(Note.GetNote,pathfiles)
            pprint(zip(notes,pathfiles))
    elif args.search != None:
        for i in Note.GreatherOrEqualThan(args.search):
            print i.xnote , i.file.path
    else:
        raise argparse.ArgumentTypeError("Note needs at least a filepath")

def cmd_file(args):
    File=Pyro4.Proxy("PYRO:File@localhost:%d"%args.port)          # get a Pyro proxy to the greeting object
    if args.files != None and args.files != []:
        if args.add == True:
            map(File.Get,map(pimp.core.db.Path,args.files))
        else: # Without option
            for fs in map(File.Find,args.files):
                pprint(map(lambda f : f.path , fs))
            
    else:
        raise argparse.ArgumentTypeError("File needs at least a filepath")
    


def cmd_comment(args):
    Comment=Pyro4.Proxy("PYRO:Comment@localhost:%d"%args.port)          # get a Pyro proxy to the gre   
    if args.files != None and args.files != []:
        if args.add != None:
            print map(lambda f : Comment.Add(f,args.add),args.files)
        else:
            comments=map(Comment.FindBySong,args.files)
            pprint(zip(comments,args.files))
    elif args.search != None:
        for i in Comment.Find(args.search):
            print i.text , i.file.path
    else:
        raise argparse.ArgumentTypeError("Note needs at least a filepath")

# create the top-level parser
parser = argparse.ArgumentParser(prog='Pimp')

parser.add_argument('--port','-p', type=int, default=9998,help='Pimp Pyro4 server port')
parser.add_argument('--version',"-v", action='version', version='%(prog)s ' + pimp.core.common.version)
parser.add_argument('--print0',"-0", action='store_true',default=False, help='Like find print0 arguments')
parser.add_argument('--printz',"-z", action='store_true',default=False, help='Print zicApt instead path')

subparsers = parser.add_subparsers(help='sub-command help')

parser_player = subparsers.add_parser('player', help='player commands')
parser_player.add_argument('--info', '-i'  , action='store_true',help='get player informations')
parser_player.add_argument('--enqueue', '-e', type=str ,  nargs='+' , action='store',metavar='file', help='Enqueue files')
parser_player.add_argument('--play', '-p' ,type=str ,  nargs='*' , action='store',metavar='file', help='play files')
parser_player.add_argument('--next', '-n'  , action='store_true',help='play next file')
parser_player.add_argument('--playlist', '-l'  , action='store_true',help='show current playlist')
parser_player.add_argument('--current', '-c'  , action='store_true',help='show current song')
parser_player.set_defaults(func=cmd_player)

parser_note = subparsers.add_parser('note', help='Note commands (get all notes without arguments)')
parser_note.add_argument('--add', '-a', type=int ,   action='store',metavar='note', help='Add note to files')
parser_note.add_argument('--search', '-s', type=int ,   action='store',metavar='note', help="Search file notes greather than 'note'")
parser_note.add_argument('files', metavar='file', type=str, nargs='*', help='a song file')
parser_note.set_defaults(func=cmd_note)

parser_note = subparsers.add_parser('file', help='Files commands (get files without arguments)')
parser_note.add_argument('--add', '-a', action='store_true', help='Add files to database')
parser_note.add_argument('files', metavar='file', type=str, nargs='*', help='a song file')
parser_note.set_defaults(func=cmd_file)


parser_comment = subparsers.add_parser('comment', help='comment commands')
parser_comment.add_argument('--add', '-c', type=str ,  nargs='*' , action='store',metavar='file', help='Get comment of files')
parser_comment.add_argument('--search', '-s', type=str ,   action='store',metavar='comment', help="Search comments")
parser_comment.add_argument('files', metavar='file', type=str, nargs='*', help='a song file')
parser_comment.set_defaults(func=cmd_comment)

args = parser.parse_args()
args.func(args)
exit(0)
