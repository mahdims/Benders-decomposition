

import numpy as np
from gurobipy import *
from itertools import combinations, product


def FirstSubProblem(Data):
    M = Data['M']  # j
    N = Data['N']  # k
    NS = Data['NS']  # s
    Range_M = range(M)
    LAMBDA = Data['lambda']
    B = np.array(Data['demand'])
    BS = np.sum(B, 1)
    pop = Data['pop']
    D = np.array(Data['distance'])
    ScProb = Data['p']
    # budget=Data['budget']
    popsum = sum(pop)
    # BigM=sum(C[j]+cec[j]*(popsum-Cap[j]) for j in Range_M)
    BD = np.array([[sum(ScProb * B[:, k] * D[k, j, :]) for j in Range_M] for k in range(N)]) / popsum
    BDS = np.array([[sum(ScProb * B[:, k] * D[k, j, :] / BS) for j in Range_M] for k in range(N)])
    NN = tuplelist([(i, j) for i, j in combinations(range(N), 2)])
    yco = {}
    for i, j in product(range(N), range(M)):
        yco[i, j] = 0.5 * BD[i, j] + 0.5 * BDS[i, j]

    # BB1=np.array([ScProb*B[:,k]*B[:,i]/BS**2  for i,j  in combinations(range(N),2)])
    uppco = {}
    for (i, k), s in product(NN, range(NS)):
        uppco[i, k, s] = LAMBDA * ScProb[s] * B[s, k] * B[s, i] / BS[s] ** 2

    Sub1 = Model("firstsubproblem")
    # construct variables
    y = Sub1.addVars(N, M, obj=yco, name="y", vtype=GRB.BINARY)  # obj=D[k,j]*sum(B[:,k])/popsum,name='Y%s.%s' % (k

    up = Sub1.addVars(NN, obj=LAMBDA / popsum ** 2, name="up")
    un = Sub1.addVars(NN, obj=LAMBDA / popsum ** 2, name="un")

    upp = Sub1.addVars(NN, NS, obj=uppco, name="upp")
    unp = Sub1.addVars(NN, NS, obj=uppco, name='unp')

    Sub1.update()

    Sub1.addConstrs((y[k, j] <= 1 for j in range(M) for k in range(N)), name="XP")
    Sub1.addConstrs(y.sum(k, '*') == 1 for k in range(N))
    PBD = [[sum(ScProb * B[:, k] * D[k, j, :]) for j in range(M)] for k in range(N)]
    Sub1.addConstrs(float(pop[i]) * quicksum(PBD[k][j] * y[k, j] for j in range(M))
                    - float(pop[k]) * quicksum(PBD[i][j] * y[i, j] for j in range(M))
                    == up[k, i] - un[k, i] for k, i in NN)

    Sub1.addConstrs(LinExpr(D[k, :, s], y.select(k, '*'))
                    - LinExpr(D[i, :, s], y.select(i, '*')) == upp[k, i, s] - unp[k, i, s]
                    for k, i, s in upp.keys())

    Sub1.update()

    Sub1.params.OutputFlag = 0
    Sub1.params.MIPGap = 0.01
    Sub1.params.MIPGapAbs = 0.01
    Sub1.params.SubMIPNodes = 50

    return Sub1, y