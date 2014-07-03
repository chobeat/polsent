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
    mapping={"Pierferdinando":"c","LegaNord2_0":'d',"angealfa":"d","SenatoreMonti":"c","udctw":"d","matteorenzi":"s","forzasilvioit":"d","scelta_civica":"c","matteosalvinimi":"d","NichiVendola":"s","pdnetwork":"s","sinistraelib":"s","NCD_tweet":"d","forza_italia":"d","Mov5Stelle":"p","beppe_grillo":"p","Oscar Giannino":"d"}
    return mapping[timeline]

def tweet2words(coll):
    t=coll.find({},["data","id","in_reply_to_screen_name",   "in_reply_to_user_id","timeline","user.id"])

   #rimuove @ e hashtags

    def sanitize(s):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",s).split())

    features=[({st.stem(w):1 for w in nltk.word_tokenize(sanitize(tweet['data']))},sentiment(tweet['timeline'])) for tweet in t]

    return features

def appendToTS(ts):
    trainingSetDB=MongoClient()["polsent"].ts

    for w,s in ts:
        d={"words":w,"sentiment":s}
        trainingSetDB.insert(d)
def readTS():
    trainingSetDB=MongoClient()["polsent"].ts

    return [(i['words'],i['sentiment']) for i in trainingSetDB.find()]

def group_read_ts(dim):
    trainingSetDB=MongoClient()["polsent"].ts

    datas=trainingSetDB.aggregate([{"$group":{"_id":"$sentiment", "words":{"$push":"$words"}}}])

    for i in data:







import random
if __name__=="__main__":
    texts=MongoClient()["polsent"].giannino
    #train_set=appendToTS(tweet2words(texts))
    pp.pprint(group_read_ts(20))
"""
    train_set=readTS()
    random.shuffle(train_set)
    test_set=train_set[:2500]
    train_set=train_set[2501:]
    #classifier=nltk.NaiveBayesClassifier.train(train_set)
    classifier = SklearnClassifier(LinearSVC())
    classifier.train(train_set)
    accuracy=nltk.classify.accuracy(classifier, test_set)
    #res=classifier.classify({w:1 for w in [st.stem(w) for w in nltk.word_tokenize("")]})

    print len(test_set),len(train_set),accuracy"""
