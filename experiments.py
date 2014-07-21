from dbop import *
import matplotlib.pyplot as pyplot
resultColl=MongoClient()['polsent']['results']

def cross_ts(i):
        i,fold=i
        c= crossvalidation(group_read(i,"ts"),fold)
        return (i,c)
def acc_wrapper(test_set):
        def inner(i):
            i,fold=i
            c=generateClassifier(group_read(20,"ts"))
            res=nltk.classify.accuracy(c,group_read(i,test_set))
            return (i,res)
        return inner

def group_size_experiment(bgn,end,fold,func=None):
    pool=ThreadPool(4)
    interval=range(bgn,end)
    if func:
        cc=func

    res=pool.map(cc,zip(interval,[fold]*len(interval)))
    resColl=MongoClient()["polsent"]['results']
    resColl.remove()
    resColl.insert({"type":"group_size","params":{"bgn":bgn,"end":end,"fold":fold},"results":res})

def plotGroupSizeGraph(filename):
    datas=resultColl.find_one({"type":"group_size"})
    xdata=[]
    ydata=[]
    for i,j in datas['results']:
        xdata.append(i)
        ydata.append(j)

    pyplot.xlabel("Grouping size")
    pyplot.ylabel("Accuracy")
    pyplot.title("Accuracy su test set esterno (Luigi Di Maio)")
    pyplot.plot(xdata,ydata)

    pyplot.savefig(filename)

if __name__=="__main__":
    plotGroupSizeGraph("maio.png")
