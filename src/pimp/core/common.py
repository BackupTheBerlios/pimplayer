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

class PimpException(Exception):pass


# For information from player to avoid an exception when an information is not available.
class Info(dict):
    def __missing__(self,key):
        return None


class Guard(object):
    """Permit to guard execution of an expression in a neested context.
    A function context can be declared with decorator Guard.locked. In a
    locked context, expression executed in Guard.guard() are not executed
    in inner context.
    
    For example,
    def echo(a):print a
    @Guard.locked
    def test1():
    echo('not guarded')
    Guard.guard(echo('guarded'))
    
    @Guard.locked
    def test2()
    test1()
    
    >>> test1()
    not guarded
    guarded
    >>> test2()
    not guarded
    >>>
    """
    lock = 0
    @classmethod
    def guard (cls,fct):
        if cls.lock <= 1:
            cls.lock=cls.lock+1
            try :
                return fct()
            except:
                raise
            finally:
                cls.lock=cls.lock-1
        else : pass #None print "** Predicated"

    @classmethod
    def locked(cls,fct):
        """Used as a decorator to lock some method. If a method is locked,
        then all guarded instructions in it are evaluated if and only if
        this method has not been called by a locked method"""
        def wrapper(*args):
            cls.lock=cls.lock+1
            try :
                return fct(*args)
            except:
                raise
            finally:
                cls.lock=cls.lock-1
        return wrapper


import types
class Hook(type):
    """ This metaclass permit to hook a class method by several handlers. The
    handlers are called when a hooked method is called. A method is
    'hooked' if it is preceded by the decorator 'Hook.Hook'.

    Each 'hooked' method has a __hooks__ attribute which is a list
    of handler methods.

    I don't know what appends if a subclass obect is copied (fct
    addresses change) !

    The hooked method is called first. And after it, handler methods
    are called. If hooked method return None, handler methods are not
    called, otherwise, they take in arguments the return value of
    hooked method.

    
    Note that you can raise exception in hooked method to bypass
    handler methods : they are then not called.
    """

    __methods_hooked__=[]
    """ Used to enable 'hooked' method by metaclass """
    def __new__(metacls, name, bases, dct):
        def _wrapper(name, method):
            print name  ,  method
            # Redefining a function
            @Guard.locked
            def _handle(self, *args, **kwargs):
                res=method(self, *args, **kwargs)
                if res == None : return res
                handlers=self.__getattribute__(name).__handlers__
                for f in handlers:
                    Guard.guard(lambda : f(res))
                return res
            # Renaming
            _handle.__name__ = method.__name__
            _handle.__doc__  = method.__doc__
            _handle.__handlers__=[]
            _handle.__dict__.update(method.__dict__)
            return _handle

        # Class method decorated with HookMethod are replaced by _handle methods.
        newDct = {'__methods_hooked__' : list(Hook.__methods_hooked__)}
        for iname, islot in dct.iteritems():
            if type(islot) is types.FunctionType and islot in Hook.__methods_hooked__:
                print "Hook on method %s.%s" % (name , iname)
                newDct[iname] = _wrapper(iname, islot)
            else:
                newDct[iname] = islot
        # Preparation for next class ...
        Hook.__methods_hooked__=[]
        return type.__new__(metacls, name, bases, newDct)

    @staticmethod
    def AddHandler(method,callback):
        """ Attach a handler to a class method """
        print "Handler %s on method %s" % (callback,method)
        method.__handlers__.append(callback)

        
    @staticmethod
    def HookMethod(method):
        """ Used as a Decorator to handle a class method """
        Hook.__methods_hooked__.append(method)
        return method





        
