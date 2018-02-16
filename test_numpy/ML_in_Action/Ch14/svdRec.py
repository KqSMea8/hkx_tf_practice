#coding:gbk
'''
Created on Mar 8, 2011

@author: Peter
'''
from numpy import *
from numpy import linalg as la

def loadExData():
    return[[0, 0, 0, 2, 2],
           [0, 0, 0, 3, 3],
           [0, 0, 0, 1, 1],
           [1, 1, 1, 0, 0],
           [2, 2, 2, 0, 0],
           [5, 5, 5, 0, 0],
           [1, 1, 1, 0, 0]]  #7*5
    
def loadExData2():
    return[[2, 0, 0, 4, 4, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5],
           [0, 0, 0, 0, 0, 0, 0, 1, 0, 4, 0],
           [3, 3, 4, 0, 3, 0, 0, 2, 2, 0, 0],
           [5, 5, 5, 0, 0, 0, 0, 5, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 5, 0, 0, 5, 0],
           [4, 0, 4, 0, 0, 0, 0, 0, 0, 0, 5],
           [0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 4],
           [0, 0, 0, 0, 0, 0, 5, 0, 0, 5, 0],
           [0, 0, 0, 3, 0, 0, 0, 0, 4, 5, 0],
           [1, 1, 2, 1, 1, 2, 1, 0, 4, 5, 0]]
    
def ecludSim(inA,inB): #ŷ�����ƶ�
    return 1.0/(1.0 + la.norm(inA - inB))

def pearsSim(inA,inB):#Ƥ��ѷ����������ƶ�
    if len(inA) < 3 : return 1.0
    return 0.5+0.5*corrcoef(inA, inB, rowvar = 0)[0][1]

def cosSim(inA,inB):#�������ƶ�
    num = float(inA.T*inB)
    denom = la.norm(inA)*la.norm(inB)
    return 0.5+0.5*(num/denom)

def standEst(dataMat, user, simMeas, item):#�ڸ������ƶȼ��㷽���������£��û�����Ʒ�Ĺ�������ֵ(�����û�Ŀǰδ�Ը���Ʒ�����)
    n = shape(dataMat)[1]  #��Ʒ����
    simTotal = 0.0; ratSimTotal = 0.0
    for j in range(n):
        userRating = dataMat[user,j]
        if userRating == 0: continue #���ҵ���ǰ�û���ĳ����Ʒ�Ĵ�ֲ�Ϊ�㣬itemΪ��Ҫ���ֵ�����,ʹ�õ��ǻ�����Ʒ�����ƶ�
        overLap = nonzero(logical_and(dataMat[:,item].A>0, \
                                      dataMat[:,j].A>0))[0]
        if len(overLap) == 0: similarity = 0 #���������û�й�ͬ����Ʒ��֣������ƶ�Ϊ0
        else: similarity = simMeas(dataMat[overLap,item], \
                                   dataMat[overLap,j])#����������ǵ����ƶ�
        #print 'the %d and %d similarity is: %f' % (item, j, similarity)
        simTotal += similarity #
        ratSimTotal += similarity * userRating
    if simTotal == 0: return 0
    else: return ratSimTotal/simTotal  #�����ǻ������ƶȵļ�Ȩƽ������
    
def svdEst(dataMat, user, simMeas, item):#����SVD�����ֹ���,itemΪ��Ҫ���ֵ�����,ʹ�õ��ǻ�����Ʒ�����ƶ�
    n = shape(dataMat)[1]#��Ʒ����
    simTotal = 0.0; ratSimTotal = 0.0
    U,Sigma,VT = la.svd(dataMat) #m*n
    Sig4 = mat(eye(4)*Sigma[:4]) #arrange Sig4 into a diagonal matrix�����������תΪ�ԽǾ���
    xformedItems = dataMat.T * U[:,:4] * Sig4.I  #create transformed items
    for j in range(n):#�е���PCA�׻�����˼
        userRating = dataMat[user,j]
        if userRating == 0 or j==item: continue
        similarity = simMeas(xformedItems[item,:].T,\
                             xformedItems[j,:].T)
        print 'the %d and %d similarity is: %f' % (item, j, similarity)
        simTotal += similarity
        ratSimTotal += similarity * userRating
    if simTotal == 0: return 0
    else: return ratSimTotal/simTotal

def recommend(dataMat, user, N=3, simMeas=cosSim, estMethod=standEst):
    unratedItems = nonzero(dataMat[user,:].A==0)[1]#find unrated items ��Ѱ��δ��������Ʒ
    if len(unratedItems) == 0: return 'you rated everything'
    itemScores = []
    for item in unratedItems:
        estimatedScore = estMethod(dataMat, user, simMeas, item)#�û��Ը���δ���ֵ���Ʒ���з�ֵ����
        itemScores.append((item, estimatedScore))
    return sorted(itemScores, key=lambda jj: jj[1], reverse=True)[:N]  #Ѱ��ǰN��δ��������Ʒ

def printMat(inMat, thresh=0.8):
    for i in range(32):
        for k in range(32):
            if float(inMat[i,k]) > thresh:
                print 1,
            else: print 0,
        print ''

def imgCompress(numSV=3, thresh=0.8):
    myl = []
    for line in open('0_5.txt').readlines():
        newRow = []
        for i in range(32):
            newRow.append(int(line[i]))
        myl.append(newRow)
    myMat = mat(myl)
    print "****original matrix******"
    printMat(myMat, thresh)
    U,Sigma,VT = la.svd(myMat)
    SigRecon = mat(zeros((numSV, numSV)))
    for k in range(numSV):#construct diagonal matrix from vector
        SigRecon[k,k] = Sigma[k] #�Խ���
    reconMat = U[:,:numSV]*SigRecon*VT[:numSV,:] #ȡUǰnumSV�У�VTǰnumSV��
    print "****reconstructed matrix using %d singular values******" % numSV
    printMat(reconMat, thresh)
    
    print "***����֮��***"
    printMat(reconMat-myMat)
    print "���֮�ͣ�"+str(sum(abs(reconMat-myMat)>thresh))
    
if __name__=='__main__':
    print "����SVD:\n"
    Data=loadExData()
    U,Sigma,VT=linalg.svd(Data)
    print "\nSigma:\n"
    print Sigma
    
    sig3=mat([[Sigma[0],0,0],#ֻȡǰ����sigma
              [0,Sigma[1],0],
              [0,0,Sigma[2]]]) 
    reconData=U[:,:3]*sig3*VT[:3,:]
    print reconData
    
    myMat=mat(loadExData()) #7*5
    print "����ŷ�����ƶȣ�\n"
    print ecludSim(myMat[:,0], myMat[:,4])
    
    print "�����������ƶȣ�\n"
    print cosSim(myMat[:,0], myMat[:,4])
    
    print "����Ƥ��ѷ�������ƶȣ�\n"
    print pearsSim(myMat[:,0], myMat[:,4])
    
    
    print "�����Ƽ���\n"
    myMat=mat(loadExData()) #7*5
    myMat[0,1]=myMat[0,0]=myMat[1,0]=myMat[2,0]=4
    myMat[3,3]=2
    print myMat
    
    print "cosSim:"+str(recommend(myMat, 2)) #�Եڶ����û������Ƽ�,�����������
    print "ecludSim:"+str(recommend(myMat, 2,simMeas=ecludSim)) #�Եڶ����û������Ƽ�,�����������
    print "pearSim:"+str(recommend(myMat, 2,simMeas=pearsSim)) #�Եڶ����û������Ƽ�,�����������
    
    print "������svd�Ƽ�"
    myMat=mat(loadExData2());
    U,Sigma,VT=la.svd(myMat)
    print "Sigma:\n"+str(Sigma)
    print sum(Sigma**2),sum(Sigma**2)*0.9
    print recommend(myMat, 1, estMethod=svdEst)
    
    print "ͼ��ѹ��\n"
    imgCompress(2)
    
   