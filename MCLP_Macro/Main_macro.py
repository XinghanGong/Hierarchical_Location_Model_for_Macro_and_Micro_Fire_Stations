# -*- coding: utf-8 -*-
import geatpy as ea
import warnings
import numpy as np
from MCLP_Macro.MyProblem_macro import MyProblem  # 导入自定义问题接口: MCLP_Macro.MyProblem

# warnings.filterwarnings("ignore", category=Warning)

if __name__ == '__main__':
    problem = MyProblem()

    Encoding = 'RI'  # Encoding method
    NIND = 300  # Population size
    Field = ea.crtfld(Encoding, problem.varTypes, problem.ranges, problem.borders)
    population = ea.Population(Encoding, Field, NIND)

    """===============================Parameter Setting============================="""
    myAlgorithm = ea.soea_SEGA_templet(problem, population)  # Algorithm template
    myAlgorithm.mutOper.Pm = 0.1  # Mutation probability
    myAlgorithm.recOper.XOVR = 0.9  # Crossover probability
    myAlgorithm.MAXGEN = 500  # Maximum number of generation
    myAlgorithm.logTras = 1  # Logging option
    myAlgorithm.verbose = True  # Set whether or not print log
    myAlgorithm.drawing = 1  # Drawing method

    """==========================Invoke Algorithm Template========================"""
    [BestIndi, population] = myAlgorithm.run()
    BestIndi.save()

    """=================================输出结果=============================="""
    print('evaluation freq：%s' % myAlgorithm.evalsNum)
    print('time: %s s' % myAlgorithm.passTime)

    if BestIndi.sizes != 0:
        print('Optimal obj value：%s' % BestIndi.ObjV[0][0])
        print('Optimal decision variable：')
        for i in range(BestIndi.Phen.shape[1]):
            print(BestIndi.Phen[0, i])
    else:
        print('No feasible solutions')
