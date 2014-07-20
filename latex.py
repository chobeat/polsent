from pymongo import *

core=MongoClient()['polsent']['texts']
def coreTSNames():
    return core.distinct("user.name")

def coreSize():
    return core.count()

for i in coreTSNames():
    print "\\item "+i
