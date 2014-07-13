from pymongo import *
import twitter
import nltk
from nltk.stem.snowball import ItalianStemmer
import pprint
import re
from sklearn.svm import LinearSVC,SVC,NuSVC
from nltk.classify.scikitlearn import SklearnClassifier
import tweetDownloader
import matplotlib.pyplot as pyplot
dbname_text="texts"
st=ItalianStemmer()
pp = pprint.PrettyPrinter(indent=4)
PURENESS_THRESHOLD=0.70

def sentmap(timeline):
    mapping={"Pierferdinando":"c","LegaNord2_0":'d',"angealfa":"d","SenatoreMonti":"c","udctw":"d","matteorenzi":"s","forzasilvioit":"d","scelta_civica":"c","matteosalvinimi":"d","NichiVendola":"s","pdnetwork":"s","sinistraelib":"s","NCD_tweet":"d","forza_italia":"d","Mov5Stelle":"p","beppe_grillo":"p","Oscar Giannino":"d","Alba Dorata ":"d","civati":"s","Paolo Ferrero":"s","AlessandroDiBattista":"s","Maurizio Gasparri":"d","Alessandra Mussolini":"d","Stato & Potenza":"s"}
    return mapping[timeline]

def words2sentiment(words,sentiment=None):
    if sentiment:
       return [(x,sentiment) for x,timeline in words]

    else:
        return [(x,sentmap()[timeline]) for x,timeline in words]



def coll2words(coll):
    tweets=MongoClient()['polsent'][coll].find({},["data","id","in_reply_to_screen_name",   "in_reply_to_user_id","timeline","user.id"])
    return tweetParser(tweet)
def tweet2words(tweets):
   #rimuove @ e hashtags

    def sanitize(s):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",s).split())

    features=[({st.stem(w):1 for w in nltk.word_tokenize(sanitize(tweet['data']))},tweet['timeline']) for tweet in tweets]

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

def insertPure(coll_name):
    p=MongoClient()["polsent"]["pures"]
    p.update({},{"$addToSet":{"colls":coll_name}})

def removePure(coll_name):

    p=MongoClient()["polsent"]["pures"]
    p.update({},{"$pull":{"colls":coll_name}})


def addPureFromScreenName(name):
    tweets=tweetDownloader.get_all_tweets(name)
    words=tweet2words(tweets)
    sentiment,p=pureSentiment([x for x,y in words])
    if p:
        coll_name=name[:4]+"_p"
        insertPure(coll_name)
    else:
        coll_name=name[:4]+"_u"

    coll=MongoClient()['polsent'][coll_name]
    coll.remove()
    coll.insert([{"words":x[0],"sentiment":sentiment} for x in words])



from collections import Counter
def pureSentiment(words):
    c=generateClassifier(group_read(15,"ts"))
    sentiments=Counter(c.batch_classify(words))
    label,sent=max(sentiments.iteritems(),key=lambda x:x[1])


    print "Il sentiment di questo account "+label
    return (label,sent>PURENESS_THRESHOLD)



def crossvalidation(training,num_folds):
    random.shuffle(training)
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
    classifier = SklearnClassifier(LinearSVC())

    classifier.train(train_set)

    return classifier
def populate_ts():

    cl= MongoClient()["polsent"]
    tscoll=cl.pures.find_one()['colls']



    cl['ts'].remove({})


    for c in tscoll:

        appendToTS(tweet2words(c),"ts")




import collections
import random
from multiprocessing.pool import ThreadPool
if __name__=="__main__":
    polsent=MongoClient()["polsent"]

      #print c.batch_classify(tweet2words("statoepotenza"))
    #print nltk.classify.accuracy(c,group_read(30,"stato"))
    #group_size_experiment(1,40,10)
    #train_set=group_read(20,"ts")
    #print c
    #populate_ts()
    #c=generateClassifier(group_read(20,"ts"))
    #print nltk.classify.accuracy(c,group_read(10,"ferre"))
    # appendToTS(tweet2words(polsent["civati"]),"ts")
    #c=generateClassifier(group_read(20,"ts"))
    #print nltk.classify.accuracy(c,group_read(10,"ferre"))

   #print crossvalidation(group_read(30,"ts"),10)
    #test_set=group_read(10,"gaspa")
    #print test_set
    #test_set=[i[0] for i in test_set]
    #train_set=train_set[301:]
    #classifier=nltk.NaiveBayesClassifier.train(train_set)
    #print "svc"
    #classifier=SklearnClassifier(SVC())
    #classifier.train(train_set)
   # print nltk.classify.accuracy(classifier,test_set)
