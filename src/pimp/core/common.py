import logging

class Log:
    """ Logging configuration """
    _stdoutLogEnable=False
    _logfile='.pimp.log'
    _format='%(levelname)6s %(asctime)s  %(filename)s %(funcName)s() > %(message)s'
    _stdout=logging.StreamHandler()

    logging.basicConfig(filename=_logfile,level=logging.INFO,format=_format)

    @staticmethod
    def To_stdout(state=True):
        """To see or not log messages in the console"""
        if Log._stdoutLogEnable and state == False:
            logging.getLogger().removeHandler(Log._stdout)
            Log._stdoutLogEnable=False
        elif state==True:
            logging.getLogger().addHandler(Log._stdout)
            Log._stdoutLogEnable=True

version="1.2"

class FileNotSupported(Exception):pass
""" Raise it when a file is not supported by Pimp """


# For information from player to avoid an exception when an information is not available.
class Info(dict):
    def __missing__(self,key):
        return None



# To avoid neested log event calls
class Guard(object):
    lock = 0
    @classmethod
    def guard (cls,fct):
        if cls.lock <= 1:
            cls.lock=cls.lock+1
#            print "** Entry block : %d" % cls.lock
            try :
                fct()
            except:
                raise
            finally:
                cls.lock=cls.lock-1
#            print "** Exit block : %d" % cls.lock
        else : pass #None print "** Predicated"

    # Used as a decorator to lock some method. If a method is locked,
    # then all guarded instructions in it are evaluated if and only if
    # this method has not been called by a locked method
    @classmethod
    def locked(cls,fct):
        def wrapper(*args):
            cls.lock=cls.lock+1
#            print "** Locked : %d" % cls.lock
            try :
                fct(*args)
            except:
                raise
            finally:
                cls.lock=cls.lock-1
#                print "** Unlocked : %d" % cls.lock
        return wrapper






# class Remote(object):
#     commands={}

#     @staticmethod
#     def addCommand(method):
#         Remote.commands.update({method.__name__ : method })
#         print Remote.commands

#     @staticmethod
#     def execCommand():
#         Remote.command[0]()
                       
#     @staticmethod
#     def showCommands():
#         for c in commands.items:
#             print c
                                   

# class Foo():
#     @staticmethod
#     @Remote.addCommand
#     def test():
#         print "foo is called!"

# class Foo():
#     @staticmethod
#     @Remote.addCommand
#     def test():
#         print "foo is called!"




        
