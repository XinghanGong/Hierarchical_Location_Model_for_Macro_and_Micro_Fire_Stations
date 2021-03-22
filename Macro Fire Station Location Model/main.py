# -*- coding: utf-8 -*-
import geatpy as ea
import warnings
import numpy as np
from MCLP_Macro.Draft5 import MyProblem  # import self-defines optimization problem: MCLP_Macro.MyProblem
import matplotlib
matplotlib.rcParams['font.sans-serif']=['SimHei']
matplotlib.rcParams['axes.unicode_minus']=False
import matplotlib.pyplot as plt
# warnings.filterwarnings("ignore", category=Warning)


if __name__ == '__main__':
    problem = MyProblem()

    Encoding = 'RI'  # encoding methos
    NIND = 300  # population size
    Field = ea.crtfld(Encoding, problem.varTypes, problem.ranges, problem.borders)  
    population = ea.Population(Encoding, Field, NIND)  
    """===============================Parameter definiton of the algorithm============================="""
    myAlgorithm = ea.soea_SEGA_templet(problem, population)  
    myAlgorithm.mutOper.Pm = 0.1  # mutation rate
    myAlgorithm.recOper.XOVR = 0.9  # crossover rate
    myAlgorithm.MAXGEN = 500  
    myAlgorithm.logTras = 1  # record diary every logTras generation; 0: do not record information;
    myAlgorithm.verbose = True  # setting about wether output diary information
    myAlgorithm.drawing = 1  # set drawing method(0: do not draw anything, 1: draw final graphical graph, 2: dynamic graph of objective space, 3: dynamic graph of decision space)
    """==========================调用算法模板进行种群进化========================"""
    [BestIndi, population] = myAlgorithm.run()  # run the algorithm template
    BestIndi.save()  # store information of the best individual
    """=================================输出结果=============================="""
    print('Number of evaluation: %s' % myAlgorithm.evalsNum)
    print('Time %s s' % myAlgorithm.passTime)

    print(BestIndi)
    if BestIndi.sizes != 0:
        print('Best Obj value: %s' % BestIndi.ObjV[0][0])
        print('Best individual: ')
        for i in range(BestIndi.Phen.shape[1]):
            print(BestIndi.Phen[0, i])
    else:
        print('No feasible solution')

