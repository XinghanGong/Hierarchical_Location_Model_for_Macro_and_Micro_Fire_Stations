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
from geopy.distance import geodesic
from MCLP_Macro.Read_Excel import excel_read
from MCLP_Macro.Read_txtfile import *
from MCLP_Macro.DistMatrix_3 import *


class MyProblem(ea.Problem):  
    def __init__(self, M=1):
        name = 'MyProblem'  # Initialize file's name (name for problem function)
        Dim = 239  # Initialize Dim (dimension of decision variables)
        maxormins = [-1] * M  # Initialize maxormins（signs for max or min of objectives, 1: minimize the objectives: -1：maximize the objectives）
        varTypes = [1] * Dim  # Initialize varTypes (Types for decision variables, 0: real number; 1: Integer)
        lb = [0] * Dim  # Lower bound of decision variables
        ub = [0] * Dim  # Upper bound of decision variables
        lbin = [1] * Dim  # Lower boundary of decision variables (0: do not inlude the lower boundary; 1: the otherwise)
        ubin = [1] * Dim  # Upper boundary of decision variables (0: do not include the upper boundary; 1: the otherwise)
        
        ea.Problem.__init__(self, name, M, maxormins, Dim, varTypes, lb, ub, lbin, ubin)

    def aimFunc(self, pop):  # Define objectives

        """=========================Parameter definition=========================="""
        R = 1.746  # Service radius of macro fire station, unit: kilometers
        Num_Build = 3  # The number of new macro fire stations to be sited
        d_l = 2 * R + 0.05  # Maximal distance between each pair of adjacent macro fire stations
        d_s = 2.043  # Minimal distance between each pair of macro fire stations

        """=========================Generate initial populations=========================="""
        Vars = pop.Phen  # Matrix of decision variables

        num_list = [x for x in range(239)]
        rand_num = []  
        for l in range(300):
            b = random.sample(num_list, 3)
            rand_num.append(b)

        for i in range(len(Vars)):
            for j in range(len(rand_num[i])):
                Vars[i][rand_num[i][j]] = 1
        Vars = np.array(Vars)

        """=======================Construct objective f1=========================="""
        excel_path_0 = r'/zengyp/Xinghan/Macro_Experience_Record/overlaprate30_p3_jianbiao/RiskValue_jainbiao.xls'
        risk = xlrd.open_workbook(excel_path_0)
        sheet = risk.sheet_by_index(0)
        RiskValue = sheet.col_values(0)
        del RiskValue[0]  # delete initial text heading
        
        ''' Compute distance matrix of potential location points, where elements in the matrix are distances from one potential location point 
            to all the rest potential location points'''
        dist_matrix_1 = dist_matrx_1()  
        
        ''' Compute distance matrix of potential location points and community points, where elements in the matrix are distances from one potential 
            location point to all the community points'''
        dist_matrix_3 = dist_matrx_3()  
        
        Index = rand_num  # 每个元素即是当前个体的建站方案

        overall_list_0 = []
        code_list_0 = []
        for i in range(len(dist_matrix_3)):
            index_0 = []
            code_idx = []
            for j in range(len(dist_matrix_3[0])):
                if dist_matrix_3[i][j] <= R:
                    index_0.append(j)
                    code_idx.append(1)  # 1: within the service area of potential location points, 0: the otherwise;
                else:
                    code_idx.append(0)
            overall_list_0.append(index_0)  # elements in overall_list_0 are indexes of communities within the service area of potential location points;
            code_list_0.append(code_idx)  # elements in code_list are 0-1 list constructed from indexes in overall_list;

        f1 = [0]*300
        for i in range(len(Vars)):  # elements in Index are the current location siting plan
            New_list_0 = []  # find all elements from overall_list based on Index[i]

            for j in range(len(Index[i])):
                New_list_0.append(overall_list_0[Index[i][j]])

            '''Merge indexes of community points from New_list_0 and delete repeating values'''
            New_list_1 = []
            for k in range(len(New_list_0)):
                New_list_1 += New_list_0[k]
            New_list_1 = np.unique(New_list_1).tolist()  # obtain indexes of potential location points within the service area of chosen communities

            '''Compute sum of risk value from elements in New_list_1 and RiskValue'''
            Sum_value = 0
            for k in range(len(New_list_1)):
                Sum_value = Sum_value + RiskValue[New_list_1[k]]
            f1[i] = Sum_value

        f1 = np.array(f1)

        """===============Main loop: find all indexes of infeasible individuals in populations============="""

        exIdx = []  # index list of infeasible individuals

        for i in range(len(Vars)):  # current individual: Vars[i]
            adj_list = []  # list containing distances among p potential location points and their adjacent potential location points
            for f in range(len(rand_num[i])):
                adj_build = []  # for certain potential location point, store the distances among the rest p-1 potential location points and the certain potential location point
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

        """============================Apply feasibility rule to handle constraints==================================="""
        pop.ObjV = np.vstack(f1)  # type of ObjV: np.array
        pop.CV = np.zeros((pop.sizes, 1))
        pop.CV[exIdx] = 1  

        # We do not use penalty function method becasue it is hard to set values for the relative parameeters;
