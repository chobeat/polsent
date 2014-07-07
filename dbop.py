from pymongo import *
import twitter
import nltk
from nltk.stem.snowball import ItalianStemmer
import pprint
import re
from sklearn.svm import LinearSVC
from nltk.classify.scikitlearn import SklearnClassifier

dbname_text="texts"
st=ItalianStemmer()
pp = pprint.PrettyPrinter(indent=4)
def sentiment(timeline):
    mapping={"Pierferdinando":"c","LegaNord2_0":'d',"angealfa":"d","SenatoreMonti":"c","udctw":"d","matteorenzi":"s","forzasilvioit":"d","scelta_civica":"c","matteosalvinimi":"d","NichiVendola":"s","pdnetwork":"s","sinistraelib":"s","NCD_tweet":"d","forza_italia":"d","Mov5Stelle":"p","beppe_grillo":"p","Oscar Giannino":"d","Alba Dorata ":"x","civati":"s","Paolo Ferrero":"s","AlessandroDiBattista":"s"}
    return mapping[timeline]

def tweet2words(coll):
    t=coll.find({},["data","id","in_reply_to_screen_name",   "in_reply_to_user_id","timeline","user.id"])

   #rimuove @ e hashtags

    def sanitize(s):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",s).split())

    features=[({st.stem(w):1 for w in nltk.word_tokenize(sanitize(tweet['data']))},sentiment(tweet['timeline'])) for tweet in t]

    return features

def appendToTS(ts,from_coll):
    trainingSetDB=MongoClient()["polsent"][from_coll]

    for w,s in ts:
        d={"words":w,"sentiment":s}
        trainingSetDB.insert(d)
def readTS(coll):
    trainingSetDB=MongoClient()["polsent"][coll]

    return [(i['words'],i['sentiment']) for i in trainingSetDB.find()]

from itertools import *
def grouper(n, iterable, fillvalue=""):
        "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
        args = [iter(iterable)] * n
        return izip_longest(fillvalue=fillvalue, *args)

def group_read(dim,coll):
    trainingSetDB=MongoClient()["polsent"][coll]

    datas=trainingSetDB.aggregate([{"$group":{"_id":"$sentiment", "words":{"$push":"$words"}}}])
    return group_tweets(datas,dim)

def group_tweets(datas,dim):
    result=[]
    for d in datas['result']:
        words=grouper(dim,d['words'])

        newWords=[]
        for group in words:
            w={}
            for tweet in group:
                if tweet:
                    for s in tweet.keys():
                        w[s]=1

            newWords.append((w,d['_id']))
        result.append(newWords)


    return [item for sublist in result for item in sublist]
def crossvalidation(training,num_folds):

    subset_size = len(training)/num_folds
    res=[]
    for i in range(num_folds):
            testing_this_round = training[i*subset_size:][:subset_size]
            training_this_round = training[:i*subset_size] + training[(i+1)*subset_size:]

            classifier=generateClassifier(training_this_round)
            accuracy=nltk.classify.accuracy(classifier, testing_this_round)
            res.append(accuracy)
    print res
    return sum(res)/len(res)

def generateClassifier(train_set):
    random.shuffle(train_set)

    classifier = SklearnClassifier(LinearSVC())

    classifier.train(train_set)

    return classifier
def populate_ts():
    tscoll=["texts","giannino","civati","ferrero_paolo"]
    MongoClient()["polsent"]['ts'].remove({})


    for c in tscoll:
        t=polsent[c]
        appendToTS(tweet2words(t),"ts")



import collections
import random
from multiprocessing.pool import ThreadPool
if __name__=="__main__":
    polsent=MongoClient()["polsent"]
    #train_set=appendToTS(tweet2words(texts))
    def cc(i):
        c= crossvalidation(group_read(i,"ts"),10)
        return (i,c)
    pool=ThreadPool(4)
    res=pool.map(cc,range(20,50,2))
    print res
    #print crossvalidation(group_read(5,"ts"),10)
    #train_set=readTS("ts")
    #print c

    test_set=group_read(10,"ferre")

    test_set=[i[0] for i in test_set]
    #train_set=train_set[301:]
    #classifier=nltk.NaiveBayesClassifier.train(train_set)

    import tsquality
    #batch1=classifier.batch_classify([{w:1 for w in tsquality.getAllWords(MongoClient()['polsent']["ferre"])}])
   # c1=collections.Counter(batch1)

    #b2=classifier.batch_classify(test_set)
    #c2=collections.Counter(b2)
    print c2
    #res=classifier.classify({w:1 for w in [st.stem(w) for w in nltk.word_tokenize("")]})


