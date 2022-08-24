# -*- coding: utf-8 -*-
import numpy as np
import geatpy as ea
import xlrd
import copy
import itertools
import random
from haversine import haversine_vector, Unit
from geopy.distance import geodesic
from LSCP_Micro.Read_Excel import excel_read
from DistMatrix_PotentToPotent import *
from DistMatrix_PotentToCommun import *


class MyProblem(ea.Problem):
    def __init__(self, M=3):
        name = 'MyProblem'
        Dim = 165
        maxormins = [1] * M
        varTypes = [1] * Dim
        lb = [0] * Dim  # lower bound
        ub = [1] * Dim  # upper bound
        lbin = [1] * Dim
        ubin = [1] * Dim

        ea.Problem.__init__(self, name, M, maxormins, Dim, varTypes, lb, ub, lbin, ubin)

    def aimFunc(self, pop):  # define objective functions
        """==================================Parameter Setting==================================="""
        Vars = pop.Phen  # Matrix of decision variables
        R = 1  # Rescue radius
        s = 19.374828778990626  # Upper limit of workload for each micro fire station

        """===================================Construct Obj1:f1===================================="""
        Obj1 = np.sum(Vars, axis=1, keepdims=True)
        f1 = []
        for i in range(len(Obj1)):
            f1.append(Obj1[i][0])
        f1 = np.array(f1)
        f1 = f1.T

        """===================================Construct Obj2:f2===================================="""
        """Obtain the indexes of each individual's chosen construction points"""
        Index = []
        for i in range(len(Vars)):
            Index_0 = []
            for j in range(len(Vars[0])):
                if Vars[i][j] == 1:
                    Index_0.append(j)
            Index.append(Index_0)  # Index list

        """Compute distance matrix of each candidate to every community points"""
        dist_matrix = dist_matrix_PTC()

        """Trans dist_matrix into 0-1 matrix: code_list_0"""
        overall_list_0 = []
        code_list_0 = []
        for i in range(len(dist_matrix)):
            index_0 = []
            code_idx = []
            for j in range(len(dist_matrix[0])):
                if dist_matrix[i][j] <= R:
                    index_0.append(j)
                    code_idx.append(1)  # 1: within R dist of the candidate point; 0: otherwise
                else:
                    code_idx.append(0)
            overall_list_0.append(index_0)  # each element: list of indexes of communities points which locate in the R dist of the candidate point
            code_list_0.append(code_idx)  # 0-1 form of overall_list

        """Compute distance matrix of each construction point to its serviced community points 
        based on overall_list_0 and dist_matrix"""
        dist_matrix_1 = []
        for i in range(len(overall_list_0)):
            dist = []
            for j in range(len(overall_list_0[i])):
                dist.append(dist_matrix[i][overall_list_0[i][j]])
            dist_matrix_1.append(dist)

        """Create list 'A' based on overall_list_1 and RiskValue"""
        excel_path_0 = r'/zengyp/Xinghan/Miro_Exp_Record/RiskValue.xls'
        risk = xlrd.open_workbook(excel_path_0)
        sheet = risk.sheet_by_index(0)
        RiskValue = sheet.col_values(0)
        del RiskValue[0]

        risk_matrix = []
        for i in range(len(overall_list_0)):
            risk = []
            for j in range(len(overall_list_0[i])):
                risk.append(RiskValue[overall_list_0[i][j]])
            risk_matrix.append(risk)

        """Main loop: obtain f2[i]"""
        f2 = [0] * 300
        for i in range(len(Index)):
            dist_matrix_11 = copy.deepcopy(dist_matrix_1)
            Index_0 = []
            New_list = []
            for j in range(len(Index[i])):
                Index_0.append(Index[i][j])
                New_list.append(overall_list_0[Index[i][j]])

            '''Differentiate the existence of repeated elements in New_list; '''
            look_up = dict()  # Initialize an empty dictionary (if neccesary: global LOOK_UP = dict()
            for k in range(len(New_list)):
                for l in range(len(New_list[k])):
                    my_number = New_list[k][l]
                    if my_number not in look_up:
                        look_up[my_number] = [[Index_0[k], l]]
                    else:
                        look_up[my_number].append([Index_0[k], l])

            New_list_1 = []  # Each element: indexes of repeatedly covered communities
            for value in look_up.values():
                if len(value) != 1:
                    New_list_1.append(value)

            if New_list_1 == []:  # If no repeatedly covered communities, compute f2[i] in the standard way
                count_value = []
                for p in range(len(dist_matrix_1)):
                    cont = np.dot(dist_matrix_1[i], overall_list_0[i])
                    count_value.append(cont)
                f2[i] = np.dot(Vars[i], count_value)
            else:  # If there exists repeatedly covered communities, compute as follows
                for q in range(len(New_list_1)):
                    num_list = []
                    for ex in range(len(New_list_1[q])):
                        num_list.append(dist_matrix_11[New_list_1[q][ex][0]][New_list_1[q][ex][1]])

                    min_value = min(num_list)

                    for r in range(len(New_list_1[q])):
                        if dist_matrix_11[New_list_1[q][r][0]][New_list_1[q][r][1]] > min_value:
                            dist_matrix_11[New_list_1[q][r][0]][New_list_1[q][r][1]] = 0

                count_value = []  # dist_matrix_1与risk_matrix中对应元素相乘
                for p in range(len(dist_matrix_11)):
                    cont = np.dot(dist_matrix_11[p], risk_matrix[p])
                    count_value.append(cont)
                count_value = np.array(count_value).T
                f2[i] = np.dot(Vars[i], count_value)

        f2 = np.array(f2)
        f2 = f2.T

        """===================================Construct Obj3:f3===================================="""
        '''Compute dist matrix of each pair of construction points'''
        dist_matrix_2 = dist_matrix_PTP()

        dist_min_all = []  # Find distance of every neighbouring stations of each individual
        for i in range(len(Index)):
            adj_list = []
            for f in range(len(Index[i])):
                adj_build = []
                for g in range(len(Index[i])):
                    if g == f:
                        continue
                    else:
                        adj_build.append(dist_matrix_2[Index[i][f]][Index[i][g]])
                adj_list.append(min(adj_build))
            dist_min_all.append(adj_list)

        mean_value = []
        for i in range(len(dist_min_all)):
            b = np.sum(dist_min_all[i], axis=0)
            c = -b / len(dist_min_all[i])
            mean_value.append(c)

        f3 = np.array(mean_value)

        """=============================Find indexes of infeasible individuals in the population=============================="""

        '''First constraint: fully-covered communities'''
        Commun_indexlist = [x for x in range(95)]
        exIdx_0 = []
        for i in range(len(Index)):
            code_index_8 = []  # list of indexes of communities which can be covered by the chosen construction points in current Vars[i]
            for l5 in range(len(Index[i])):
                code_index_8.append(overall_list_0[Index[i][l5]])

            comb_7 = []  # del repeated values in code_index_8
            for l6 in range(len(code_index_8)):
                comb_7 += code_index_8[l6]
            comb_7 = np.unique(comb_7).tolist()

            if set(comb_7) < set(Commun_indexlist):
                exIdx_0.append(i)

        '''Second constraint: workload upper limit for each micro station'''
        exIdx_1 = []
        for i in range(len(Index)):
            A_selected = []
            for j in range(len(Index[i])):
                A_selected.append(risk_matrix[Index[i][j]])

            A_value = []
            for sb in range(len(A_selected)):
                d = np.sum(A_selected[sb])
                A_value.append(d)

            deter_value = 0
            for va in range(len(A_value)):
                deter_value = deter_value + A_value[va]
            deter_value = deter_value / len(A_value)
            # print(deter_value)
            if deter_value > s:
                exIdx_1.append(i)
                continue

        '''Obtain the list of indexes of infeasible individuals in the population'''
        exIdx_all = list(np.unique(exIdx_0))

        # SUMT:
        # alpha =0.2
        # beta = 0.1
        # f1[exIdx] = f1[exIdx] + self.maxormins[0] * alpha * (np.max(f1) - np.min(f1) + beta)

        # Self-defined function:
        # f1[exIdx] = f1[exIdx]-0.05  #- np.min(f1)

        """============================Feasibility rule==================================="""
        pop.ObjV = np.vstack([f1, f2, f3]).T
        pop.CV = np.zeros((pop.sizes, 1))
        pop.CV[exIdx_all] = 1
