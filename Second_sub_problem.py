
from itertools import product
from gurobipy import *
import numpy as np


def SecondSubProblem(Data, Xp ,Yp):
    M = Data['M']  # j
    # N=Data['N'] #k
    NS = Data['NS']  # s
    Cap = Data.get('cap')
    ScProb = Data['p']
    budget = Data['budget']
    pop = Data['pop']
    cec = Data['cec']
    C = Data['cost']
    B = np.array(Data['demand'])

    C = C * np.array(Xp)
    popsum = sum(pop)
    BigM = sum(C[j] + cec[j] * (popsum - Cap[j]) for j in range(M))
    Sub2 = Model("secondsubproblem")

    t = Sub2.addVars(M, NS, obj=1, name="t")
    z = Sub2.addVars(NS, vtype=GRB.BINARY, obj=0, name="z")
    Sub2.update()
    Sub2.addConstrs(sum(Yp[:, j] * B[s, :]) - t[j, s] <= Cap[j] for j, s in product(range(M), range(NS)))
    Sub2.addConstrs((quicksum(cec * t.select('*', s) + C) + BigM * z[s] <= budget + BigM for s in range(NS)), "indb")
    Sub2.addConstr(quicksum(ScProb * z.select('*')) >= 0.95)

    Sub2.params.OutputFlag = 0
    Sub2.params.MIPGap = 0.01
    Sub2.params.MIPGapAbs = 0.01
    Sub2.params.SubMIPNodes = 50
    Sub2.update()

    return Sub2