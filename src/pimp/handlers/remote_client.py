
import sys,os
sys.path.insert(0,os.path.abspath("./src/"))

import Pyro4
Pyro4.config.HMAC_KEY="pimp"

import pimp.core.common
import pimp.core.playlist


import argparse

def cmd_player(args):
    player=Pyro4.Proxy("PYRO:player@localhost:9998")          # get a Pyro proxy to the greeting object
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
        print player.information()
    elif args.playlist :
        print player.show()

def cmd_tag(args):
    import pimp.core.db
    if args.note != None:
        Note=Pyro4.Proxy("PYRO:Note@localhost:9998")          # get a Pyro proxy to the greeting object
        pathfiles=map(pimp.core.db.Path,args.note)
        notes=map(Note.GetNote,pathfiles)
        for (n,p) in zip(notes,pathfiles):
            print str(n) + " " + p
    if args.comment != None:
        Note=Pyro4.Proxy("PYRO:Comment@localhost:9998")          # get a Pyro proxy to the greeting object
        pathfiles=map(pimp.core.db.Path,args.comment)
        notes=map(Note.GetComments,pathfiles)
        for (n,p) in zip(notes,pathfiles):
            print str(n) + " " + p

# create the top-level parser
parser = argparse.ArgumentParser(prog='Pimp')

parser.add_argument('--port', type=int, default=9998,help='Pimp Pyro4 server port')
subparsers = parser.add_subparsers(help='sub-command help')

parser_player = subparsers.add_parser('player', help='player commands')
parser_player.add_argument('--info', '-i'  , action='store_true',help='get player informations')
parser_player.add_argument('--enqueue', '-e', type=str ,  nargs='+' , action='store',metavar='file', help='Enqueue files')
parser_player.add_argument('--play', '-p' ,type=str ,  nargs='*' , action='store',metavar='file', help='play files')
parser_player.add_argument('--next', '-n'  , action='store_true',help='play next file')
parser_player.add_argument('--playlist', '-l'  , action='store_true',help='show current playlist')
parser_player.set_defaults(func=cmd_player)

parser_tag = subparsers.add_parser('tag', help='tagging commands')
parser_tag.add_argument('--add', '-a', type=str ,  nargs='*' , action='store',metavar='file', help='Get notes of files')
parser_tag.add_argument('--note', '-n', type=str ,  nargs='*' , action='store',metavar='file', help='Get notes of files')
parser_tag.add_argument('--comment', '-c', type=str ,  nargs='*' , action='store',metavar='file', help='Get comment of files')
parser_tag.set_defaults(func=cmd_tag)

args = parser.parse_args()
args.func(args)
exit(0)
