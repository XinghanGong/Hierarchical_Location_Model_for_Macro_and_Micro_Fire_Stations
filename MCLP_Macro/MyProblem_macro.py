# -*- coding: utf-8 -*-
import numpy as np
import random
import geatpy as ea
import itertools
import xlrd
import copy
from MCLP_Macro.DistMatrix_0 import *
from MCLP_Macro.DistMatrix_1 import *
from MCLP_Macro.DistMatrix_2 import *
from MCLP_Macro.DistMatrix_3 import *
from geopy.distance import geodesic
from MCLP_Macro.Read_Excel import excel_read
from MCLP_Macro.Read_txtfile import *



class MyProblem(ea.Problem):
    def __init__(self, M=1):
        name = 'MyProblem'
        Dim = 239
        maxormins = [-1] * M
        varTypes = [1] * Dim
        lb = [0] * Dim
        ub = [0] * Dim
        lbin = [1] * Dim
        ubin = [1] * Dim

        ea.Problem.__init__(self, name, M, maxormins, Dim, varTypes, lb, ub, lbin, ubin)

    def aimFunc(self, pop):  # objective functions

        """=========================Parameter Setting=========================="""
        R = 1.746  # Rescue radius, km

        d_l = 2 * R + 0.05  # maximum distance between any two macro fire stations
        d_s = 2.043  # minimum distance between any two macro fire stations

        """=========================Generate Initial Population=========================="""
        Vars = pop.Phen

        num_list = [x for x in range(239)]
        rand_num = []
        for l in range(300):
            b = random.sample(num_list, 3)
            rand_num.append(b)

        for i in range(len(Vars)):
            for j in range(len(rand_num[i])):
                Vars[i][rand_num[i][j]] = 1
        Vars = np.array(Vars)

        """=======================Construct Obj1:f1=========================="""
        excel_path_0 = r'/zengyp/Xinghan/Macro_Experience_Record/overlaprate30_p3_jianbiao/RiskValue_jainbiao.xls'
        risk = xlrd.open_workbook(excel_path_0)
        sheet = risk.sheet_by_index(0)
        RiskValue = sheet.col_values(0)
        del RiskValue[0]

        dist_matrix_1 = dist_matrx_1()
        dist_matrix_3 = dist_matrx_3()
        Index = rand_num

        overall_list_0 = []
        code_list_0 = []
        for i in range(len(dist_matrix_3)):
            index_0 = []
            code_idx = []
            for j in range(len(dist_matrix_3[0])):
                if dist_matrix_3[i][j] <= R:
                    index_0.append(j)
                    code_idx.append(1)
                else:
                    code_idx.append(0)
            overall_list_0.append(index_0)
            code_list_0.append(code_idx)

        f1 = [0]*300
        for i in range(len(Vars)):
            New_list_0 = []

            for j in range(len(Index[i])):
                New_list_0.append(overall_list_0[Index[i][j]])

            '''Del repeated index values in New_list_0'''
            New_list_1 = []
            for k in range(len(New_list_0)):
                New_list_1 += New_list_0[k]
            New_list_1 = np.unique(New_list_1).tolist()  # indexes of candidate points within R dist of the chosen community point

            Sum_value = 0
            for k in range(len(New_list_1)):
                Sum_value = Sum_value + RiskValue[New_list_1[k]]
            f1[i] = Sum_value

        f1 = np.array(f1)

        """===============Main Loop: find indexes of all infeasible individuals in the population============="""

        exIdx = []

        for i in range(len(Vars)):
            adj_list = []
            for f in range(len(rand_num[i])):
                adj_build = []
                for g in range(len(rand_num[i])):
                    if g == f:
                        continue
                    else:
                        adj_build.append(dist_matrix_1[rand_num[i][f]][rand_num[i][g]])
                adj_list.append(min(adj_build))

            max_dist = max(adj_list)
            min_dist = min(adj_list)

            if max_dist <= d_l and min_dist >= d_s:
                continue
            else:
                exIdx.append(i)

        print(len(exIdx))  # If len(exIdx)==200, then no feasible individuals exist

        """============================Feasibility Rule==================================="""
        pop.ObjV = np.vstack(f1)
        pop.CV = np.zeros((pop.sizes, 1))
        pop.CV[exIdx] = 1

        # SUMT:
        # alpha =0.2
        # beta = 0.1
        # f1[exIdx] = f1[exIdx] + self.maxormins[0] * alpha * (np.max(f1) - np.min(f1) + beta)

        # Self-defined function:
        # f1[exIdx] = f1[exIdx]-0.05  #- np.min(f1)














