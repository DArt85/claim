
class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None

    def __call__(cls,*args,**kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance

class Util():

    @staticmethod
    def safe_call(func, *args):
        try:
            res = func(*args)
        except Exception as e:
            res = e
        return res
