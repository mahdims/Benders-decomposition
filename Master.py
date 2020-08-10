
from gurobipy import Model, GRB, quicksum



def MasterProblem(Data, MaxOpen, MinOpen):
    M = Data['M']  # j
    Master = Model("masterproblem")
    x = Master.addVars(M, vtype=GRB.BINARY, obj=0, name="x")
    Master.update()
    Master.addConstr(quicksum(x.select('*')) <= MaxOpen)
    Master.addConstr(quicksum(x.select('*')) >= MinOpen)

    Master.params.OutputFlag = 0
    Master.params.MIPGap = 0.01
    Master.params.MIPGapAbs = 0.01
    Master.params.SubMIPNodes = 50
    Master.update()
    return (Master, x)