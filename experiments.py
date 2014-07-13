from dbop import *
import matplotlib.pyplot as pyplot
resultColl=MongoClient()['polsent']['results']

def group_size_experiment(bgn,end,fold):
    def cc(i):
        i,fold=i
        c= crossvalidation(group_read(i,"ts"),fold)
        return (i,c)
    pool=ThreadPool(4)
    interval=range(bgn,end)
    res=pool.map(cc,zip(interval,[fold]*len(interval)))
    resColl=MongoClient()["polsent"]['results']
    resColl.insert({"type":"group_size","params":{"bgn":bgn,"end":end,"fold":fold},"results":res})

def plotGroupSizeGraph():
    datas=resultColl.find_one({"type":"group_size"})
    xdata=[]
    ydata=[]
    for i,j in datas['results']:
        xdata.append(i)
        ydata.append(j)

    pyplot.xlabel("Grouping size")
    pyplot.ylabel("Cross Validation Accuracy")
    pyplot.title("Accuracy del classificatore al variare della taglia del raggruppamento")
    pyplot.plot(xdata,ydata)

    pyplot.savefig("group_size_test.png")

if __name__=="__main__":
    plotGroupSizeGraph()
