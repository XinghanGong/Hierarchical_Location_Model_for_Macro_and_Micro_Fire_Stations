# -*- coding: utf-8 -*-
import geatpy as ea
from Trans_result import *
from MyProblem_micro import *  # Import self-defined model

if __name__ == '__main__':
    problem = MyProblem()

    Encoding = 'BG'  # Encoding method
    NIND = 300  # Population size
    Field = ea.crtfld(Encoding, problem.varTypes, problem.ranges, problem.borders)
    population = ea.Population(Encoding, Field, NIND)

    """===============================Set Parameters============================="""
    myAlgorithm = ea.moea_NSGA2_templet(problem, population)  # Algorithm template
    myAlgorithm.mutOper.Pm = 0.005  # Mutation probability
    myAlgorithm.recOper.XOVR = 0.9  # Crossover probability
    myAlgorithm.MAXGEN = 300  # Maximum number of generation
    myAlgorithm.logTras = 1  # Logging option
    myAlgorithm.verbose = True  # Set whether or not print log
    myAlgorithm.drawing = 1  # Drawing method

    """==========================Invoke Algorithm Template========================="""
    [NDSet, population] = myAlgorithm.run()
    NDSet.save()

    """==================================Results Output=============================="""
    print('time：%f s' % myAlgorithm.passTime)
    print('evaluation freq：%d' % myAlgorithm.evalsNum)
    print('The number of nondominated individuals：%d' % NDSet.sizes) if NDSet.sizes != 0 else print('No feasible solutions！')

    if myAlgorithm.log is not None:
        print(myAlgorithm.log)
    if myAlgorithm.log is not None and NDSet.sizes != 0:
        print('HV', myAlgorithm.log['hv'][-1])
        print('Spacing', myAlgorithm.log['spacing'][-1])
        """=========================Evaluation of Indicators========================="""
        metricName = [['spacing'], ['hv']]
        Metrics = np.array([myAlgorithm.log[metricName[i][0]] for i in range(len(metricName))]).T
        ea.trcplot(Metrics, labels=metricName, titles=[['Spacing'], ['HV']])
