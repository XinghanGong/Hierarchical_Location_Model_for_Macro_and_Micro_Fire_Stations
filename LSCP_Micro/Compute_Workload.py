# -*- coding: utf-8 -*-
from geopy.distance import geodesic
import xlrd
import numpy as np
from DistMatrix_PotentToPotent import *
from DistMatrix_PotentToCommun import *

"""Read column data and store in a list"""
class excel_read_1:
    def __init__(self, excel_path, index):
        self.data = xlrd.open_workbook(excel_path)
        self.table = self.data.sheets()[index]
        self.rows = self.table.nrows

    def get_data(self):
        result = []
        for i in range(self.rows):
            col = self.table.row_values(i)
            result.append(col)
        return result

"""Read row data and store in a list"""
class excel_read_2:
    def __init__(self, excel_path, index):
        self.data = xlrd.open_workbook(excel_path)
        self.table = self.data.sheets()[index]
        self.cols = self.table.ncols

    def get_data(self):
        result = []
        for i in range(self.cols):
            row = self.table.col_values(i)
            result.append(row)
        return result

if __name__ == '__main__':
    excel_path_1 = r'/zengyp/Xinghan/ModPaper_Exp/ComputeWorkload/Nind_300/Exp10/Result/Phen.xls'
    index = 0
    m = excel_read_1(excel_path_1, index).get_data()

    excel_path_2 = r'/zengyp/Xinghan/ModPaper_Exp/ComputeWorkload/Nind_300/Exp10/Result/ObjV.xls'
    ob = excel_read_2(excel_path_2, index).get_data()

    R = 1
    d_s = 1.170

    """Find indexes of each individual's construction points"""
    Index = []
    for i in range(len(m)):
        Index_0 = []
        for j in range(len(m[0])):
            if m[i][j] == 1:
                Index_0.append(j)
        Index.append(Index_0)

    """Total number of constuction points of each individual"""
    Build_Total = []
    for i in range(len(Index)):
        Build_Total.append(len(Index[i]))

    """Import dist matrix of each pair of construction points"""
    dist_matrix_2 = dist_matrix_PTP()

    """differentiate the existence of feasible individuals"""
    Unfeas_Num = []  # Record the number of infeasible construction points in Index[i]
    dist_min_all = []  # Compute the dist of each pair of neighboring construction points in eacch individual
    exIdx_2 = []

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

        max_dist = max(adj_list)
        min_dist = min(adj_list)

        Unfeas_0 = []
        for k in range(len(adj_list)):
            if adj_list[k] < d_s:
                Unfeas_0.append(k)
        Unfeas_Num.append(len(Unfeas_0))

        if d_s <= min_dist:
            continue
        else:
            exIdx_2.append(i)
    print('The number of infeasible individuals: ', len(exIdx_2))

    """If no feasible solutions, find approximately optimal individuals"""

    '''Definition of approx optimal 1: individual which has the lowest value of 
    'the number of infeasible construction points/total number of construction points'''
    Ratio_Unfeas = np.divide(np.array(Unfeas_Num),np.array(Build_Total))

    index_value_0 = min(Ratio_Unfeas)

    OptSolution_0 = []  # [14, 107, 176]
    for i in range(len(Ratio_Unfeas)):
        if Ratio_Unfeas[i] == index_value_0:
            OptSolution_0.append(i)
    print('Approx opt individuals 1: ', OptSolution_0)

    '''Definition of approx optimal 2: individual which has the biggest value of 
    average distance of neighbouring construction points'''
    mean_value = []
    for i in range(len(dist_min_all)):
        b = np.sum(dist_min_all[i], axis=0)
        c = b / len(dist_min_all[i])
        mean_value.append(c)

    index_value_1 = max(mean_value)

    OptSolution_1 = []  # [114, 197]
    for i in range(len(mean_value)):
        if mean_value[i] == index_value_1:
            OptSolution_1.append(i)
    print('Approx opt individuals 2: ', OptSolution_1)


    """Compute the number of workload upper limit value under the two approx definitions"""
    OptSolution_Total = OptSolution_0 + OptSolution_1
    print('Individuals obtained by the initial ideal method: ', OptSolution_Total)

    '''dist matrix of each candidate point to every community points'''
    dist_matrix = dist_matrix_PTC()

    '''Trans into 0-1 form: code_list_0'''
    overall_list_0 = []
    code_list_0 = []
    for i in range(len(dist_matrix)):
        index_0 = []
        code_idx = []
        for j in range(len(dist_matrix[0])):
            if dist_matrix[i][j] <= R:
                index_0.append(j)
                code_idx.append(1)
            else:
                code_idx.append(0)
        overall_list_0.append(index_0)
        code_list_0.append(code_idx)

    '''Create matrix A'''
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
        risk = np.sum(risk, axis=0)
        risk_matrix.append(risk)

    Index_feas = []
    for i in range(len(OptSolution_Total)):
        Index_feas.append(Index[OptSolution_Total[i]])

    workload_s = []
    for i in range(len(Index_feas)):
        risk_cal = [0]
        for j in range(len(Index_feas[i])):
            risk_cal = np.sum([risk_cal,risk_matrix[Index_feas[i][j]]], axis=0)
        risk_total_num = np.divide(np.array(risk_cal),np.array(Build_Total[OptSolution_Total[i]]))
        workload_s.append(risk_total_num[0])

    print('Workload value using initial ideal method: ', workload_s)

    """Workload using modified approx method"""
    min_obj2 = min(ob[1])
    ind = []
    for i in range(len(ob[1])):
        if ob[1][i]==min_obj2:
            ind.append(i)
    print('index values with modified method: ', ind)

    Index_feas_new = []
    for i in range(len(ind)):
        Index_feas_new.append(Index[ind[i]])

    workload_s_new = []
    for i in range(len(Index_feas_new)):
        risk_cal = [0]
        for j in range(len(Index_feas_new[i])):
            risk_cal = np.sum([risk_cal, risk_matrix[Index_feas_new[i][j]]], axis=0)
        risk_total_num = np.divide(np.array(risk_cal), np.array(Build_Total[ind[i]]))
        workload_s_new.append(risk_total_num[0])

    print('Workload value obtained by the modified method: ', workload_s_new)