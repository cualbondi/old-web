from pymongo import MongoClient
from django.conf import settings
import datetime

def limpiar(dic):
    if type(dic) in (str, int, float, unicode):
        return dic
    if type(dic) in (dict,):
        d = {}
        for k, v in dic.iteritems():
            d[k.replace(".", "_")] = limpiar(dic[k])
        return d
    if type(dic) in (list,):
        l = []
        for v in dic:
            l.append(limpiar(v))
        return l
    try:
        return limpiar(dic.asDict())
    except:
        return ""

class MongoLog():

    col = False

    def __init__(self, dic):
        if not self.__class__.col:
            try:
                conn = MongoClient(settings.PYMONGOLOG_URI, 27017)
                conn.write_concern['w'] = 0
                self.__class__.col = conn.cualbondi.log
            except:
                pass
        if self.__class__.col:
            try:
                self.__class__.col.insert(dict(limpiar(dic).items()+{"timestamp": datetime.datetime.now()}.items()), w=0)
            except:
                pass
                
