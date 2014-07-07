from pymongo import *
import pprint
import dbop
client=MongoClient()['polsent']
ts=client.ts
pp=pprint.PrettyPrinter()
def getAllWords(coll):
    words=coll.find({})

    return set([x for i in words for x in i['words']])

def count_matchings(tscoll,test_coll):
    tswords=getAllWords(tscoll)

    test_sample=getAllWords(test_coll)
    matchings=[i for i in test_sample if i in tswords]
    return len(matchings)


if __name__=="__main__":
    pass
