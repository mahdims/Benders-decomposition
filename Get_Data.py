import csv
import os
import numpy as np



def getdata(N, M, NS, percentage, LAMBDA):

    dir_path = os.path.dirname(os.path.realpath(__file__))
    firstData = []
    ifile = open(dir_path + '/data/cap41_%d_%d_%d.csv' % (N, M, NS), "r", encoding="ascii")
    read = csv.reader(ifile)
    for row in read: firstData.append(row)
    ifile.close()

    Dis = np.array([np.array(x).astype(np.float) for i, x in enumerate(firstData) if i <= N - 1])
    B = [list(np.array(x).astype(np.float)) for i, x in enumerate(firstData) if i >= N and i <= NS + N - 1]
    pop = list([np.array(x).astype(np.float) for i, x in enumerate(firstData) if i == NS + N][0])
    Cost = [np.array(x).astype(np.float) for i, x in enumerate(firstData) if i == NS + N + 1][0]
    cap = [np.array(x).astype(np.float) for i, x in enumerate(firstData) if i == NS + N + 2][0]
    Cec = [np.array(x).astype(np.float) for i, x in enumerate(firstData) if i == NS + N + 3][0]
    p = [np.array(x).astype(np.float) for i, x in enumerate(firstData) if i == NS + N + 4][0]
    budget = [np.array(x).astype(np.float) for i, x in enumerate(firstData) if i == NS + N + 5][0][0]

    M = len(cap)
    Dis = np.reshape(Dis, (N, M, NS), 'F')

    Data = {
        'M': M,
        'N': N,
        'NS': NS,
        'budget': budget,
        'percentage': percentage,
        'pop': pop,
        'cap': cap,
        'cec': Cec,
        'cost': Cost,
        'distance': Dis,
        'demand': B,
        'p': p,
        'lambda': LAMBDA,
    }

    return Data