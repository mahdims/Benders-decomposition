from numpy import where
import numpy as np
import time
import os
from gurobipy import *
from itertools import product

from Get_Data import getdata
from Master import MasterProblem
from First_sub_problem import FirstSubProblem
from Second_sub_problem import SecondSubProblem

dir_path = os.path.dirname(os.path.realpath(__file__))
start_time_total = time.time()

N = 50
M = 16
NS = 50
percentage = 0.95
LAMBDA = 0.5

Data = getdata(N, M, NS, percentage, LAMBDA)

EstCost = Data['cost']
Budget = Data['budget']
MaxOpen = where(np.cumsum(EstCost) >= Budget)[0][0]
MinOpen = 5
############ Main Algothim ##########
(Master, x) = MasterProblem(Data, MaxOpen, MinOpen)
(Sub1, y) = FirstSubProblem(Data)
Masterstatus = 2
Sub1status = 2
Sub2status = 1
BestObj = 999999999999999999999

while Masterstatus == 2:
    start_time = time.time()
    Master.optimize()
    print("Solving the Master problem took %s sec" % round(time.time() - start_time,4))
    Masterstatus = Master.status
    if Masterstatus != 2: break
    Xp=[a.x for a in Master.getVars()]
    for j,k in product(range(M), range(N) ):
            Sub1.remove(Sub1.getConstrByName("XP[%d,%d]" %(j,k)))
    Sub1.addConstrs((y[k,j]<=Xp[j] for j in range(M) for k in range(N)),name="XP")
    Sub1status = 2
    while Sub1status == 2:

        start_time = time.time()
        Sub1.optimize()
        print("Solving the First Sub problem took %s sec" % round(time.time() - start_time,4))
        
        Sub1status=Sub1.status
        if Sub1status!=2:
            oneindex=[i for i ,j in enumerate(Xp) if j==1]
            zerosindex=[i for i ,j in enumerate(Xp) if j==0]
            Master.addConstr(quicksum(1-x[i] for i in oneindex) +quicksum(x[i] for i in zerosindex)>=1)
            break
            
        Yp = np.array([a.x for a in Sub1.getVars()[0:M*N]])
        Yp = Yp.reshape( (N,M) )
        
        Sub2 = SecondSubProblem(Data, Xp, Yp)
        start_time = time.time()
        Sub2.optimize()
        print("Solving the Second Sub problem took %s sec" % round(time.time() - start_time,4))
        
        Sub2status=Sub2.status
        if Sub2.status==2:
            oneindex=[i for i ,j in enumerate(Xp) if j==1]
            zerosindex=[i for i ,j in enumerate(Xp) if j==0]
            Master.addConstr(quicksum(1-x[i] for i in oneindex) +quicksum(x[i] for i in zerosindex)>=1)
            if Sub1.ObjVal < BestObj:
                BestObj=Sub1.ObjVal
                bestSol=[Sub1.ObjVal,Xp,Yp]
            break
        else:
            oneindex=[(i,k) for (i,k) ,j in np.ndenumerate(Yp) if j==1]
            zerosindex=[(i,k) for (i,k) ,j in np.ndenumerate(Yp) if j==0]
            Sub1.addConstr(quicksum(1-y[i,k] for (i,k) in oneindex) +quicksum(y[i,k] for (i,k) in zerosindex)>=1,name="SBC")
        
Runtime= time.time()- start_time
Master.write("Master.lp")
Sub1.write("Sub1.lp")
Sub2.write("Sub2.lp")