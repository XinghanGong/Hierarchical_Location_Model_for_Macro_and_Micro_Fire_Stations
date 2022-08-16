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


class MyProblem(ea.Problem):  # 继承Problem父类
    def __init__(self, M=3):
        name = 'MyProblem'  # 初始化name（函数名称，可以随意设置）
        Dim = 165  # 165  # 初始化Dim（决策变量维数）
        maxormins = [1] * M  # 初始化maxormins（目标最小最大化标记列表，1：最小化该目标；-1：最大化该目标）
        varTypes = [1] * Dim  # 初始化varTypes（决策变量的类型，0：实数；1：整数）
        lb = [0] * Dim  # 决策变量下界
        ub = [1] * Dim  # 决策变量上界
        lbin = [1] * Dim  # 决策变量下边界（0表示不包含该变量的下边界，1表示包含）
        ubin = [1] * Dim  # 决策变量上边界（0表示不包含该变量的上边界，1表示包含）
        # 调用父类构造方法完成实例化
        ea.Problem.__init__(self, name, M, maxormins, Dim, varTypes, lb, ub, lbin, ubin)

    def aimFunc(self, pop):  # 目标函数
        """==================================优化问题参数设定==================================="""
        Vars = pop.Phen  # 得到决策变量矩阵
        R = 1  # (AveSpeed * 3) / 60  # 服务半径: 大型站要求4min到达现场，单位km
        s = 19.374828778990626

        Obj1 = np.sum(Vars, axis=1, keepdims=True)
        f1 = []
        for i in range(len(Obj1)):
            f1.append(Obj1[i][0])
        f1 = np.array(f1)
        f1 = f1.T

        """===================================构造目标函数f2===================================="""
        """得到每个个体所选建站点索引值"""
        Index = []
        for i in range(len(Vars)):
            Index_0 = []
            for j in range(len(Vars[0])):
                if Vars[i][j] == 1:
                    Index_0.append(j)
            Index.append(Index_0)  # 最后得到形如[[...],...,[...]]的Index列表，每个元素对应Vars中每个个体的所选建站点的索引值

        """计算元素为某候选点到所有社区的距离矩阵"""
        dist_matrix = dist_matrix_PTC()  # 计算元素为某候选点到所有社区的距离矩阵

        """将候选点与社区点间矩阵转换成0-1矩阵: code_list_0"""
        overall_list_0 = []
        code_list_0 = []
        for i in range(len(dist_matrix)):
            index_0 = []
            code_idx = []
            for j in range(len(dist_matrix[0])):
                if dist_matrix[i][j] <= R:
                    index_0.append(j)
                    code_idx.append(1)  # 1: 在候选点的R范围之内; 0: 反之
                else:
                    code_idx.append(0)
            overall_list_0.append(index_0)  # overall_list_0中的元素为某候选点R范围内的社区点索引值
            code_list_0.append(code_idx)  # code_list中的元素为由overall_list中索引值对应构成的0-1列表

        """基于overall_list_0与dist_matrix得到建站点到其服务区内社区的距离矩阵"""
        dist_matrix_1 = []  # 对应笔记中的"D"
        for i in range(len(overall_list_0)):
            dist = []
            for j in range(len(overall_list_0[i])):
                dist.append(dist_matrix[i][overall_list_0[i][j]])
            dist_matrix_1.append(dist)

        """基于overall_list_1与RiskValue构造"A"列表"""
        excel_path_0 = r'/zengyp/Xinghan/Miro_Exp_Record/RiskValue.xls'
        risk = xlrd.open_workbook(excel_path_0)
        sheet = risk.sheet_by_index(0)
        RiskValue = sheet.col_values(0)
        del RiskValue[0]  # 去掉开头的字符
        # s = np.sum(RiskValue, axis=0)

        risk_matrix = []  # 对应笔记中的"A"
        for i in range(len(overall_list_0)):
            risk = []
            for j in range(len(overall_list_0[i])):
                risk.append(RiskValue[overall_list_0[i][j]])
            risk_matrix.append(risk)

        """主循环得到每一个f2[i]值"""
        f2 = [0] * 300
        for i in range(len(Index)):  # 把下面这两个部分放到这个大循环之中计算f2列表中的值
            dist_matrix_11 = copy.deepcopy(dist_matrix_1)
            Index_0 = []
            New_list = []
            for j in range(len(Index[i])):
                Index_0.append(Index[i][j])
                New_list.append(overall_list_0[Index[i][j]])
            '''判别New_list中元素是否存在重复元素: 若不存在，标准流程; 若存在，创建一个放入索引值的新list'''
            look_up = dict()  # 初始化一个空词典(如有必要，可以对其进行全局化声明: global LOOK_UP = dict()
            for k in range(len(New_list)):
                for l in range(len(New_list[k])):
                    my_number = New_list[k][l]
                    if my_number not in look_up:
                        look_up[my_number] = [[Index_0[k], l]]
                    else:
                        look_up[my_number].append([Index_0[k], l])
            # 至此，已经建立好了一个词典，只需要查询就可以得到相应的结果

            New_list_1 = []  # 每个元素为某被重复cover社区的索引值，形如[[[.,.],[.,.],...,[.,.]],[...],...,[...]]
            for value in look_up.values():
                if len(value) != 1:
                    New_list_1.append(value)

            if New_list_1 == []:  # 没有被重复cover的社区，按原定方案计算f2[i]即可
                count_value = []  # dist_matrix_1与risk_matrix中对应元素相乘
                for p in range(len(dist_matrix_1)):
                    cont = np.dot(dist_matrix_1[i], overall_list_0[i])
                    count_value.append(cont)
                f2[i] = np.dot(Vars[i], count_value)  # 种群Vars中个体Vars[i]与count_value相乘
            else:  # 出现了被重复覆盖社区的情况
                for q in range(len(New_list_1)):  # 当前重复出现社区在D中的索引值list: New_list_1[q]
                    num_list = []
                    for ex in range(len(New_list_1[q])):
                        num_list.append(dist_matrix_11[New_list_1[q][ex][0]][New_list_1[q][ex][1]])

                    min_value = min(num_list)

                    for r in range(len(New_list_1[q])):
                        if dist_matrix_11[New_list_1[q][r][0]][New_list_1[q][r][1]] > min_value:
                            dist_matrix_11[New_list_1[q][r][0]][New_list_1[q][r][1]] = 0
                            # else:  # 如果最小值个体有多个如何处理?
                            '''应该是让当前可覆盖社区数量最少的建站点负责这个'''
                            '''如果这里面同时有多个建站点可覆盖社区数量相同: 那就随机分配?'''

                count_value = []  # dist_matrix_1与risk_matrix中对应元素相乘
                for p in range(len(dist_matrix_11)):
                    cont = np.dot(dist_matrix_11[p], risk_matrix[p])
                    count_value.append(cont)
                count_value = np.array(count_value).T
                f2[i] = np.dot(Vars[i], count_value)  # 种群Vars中个体Vars[i]与count_value相乘

        f2 = np.array(f2)
        f2 = f2.T

        '''构造候选点间距离矩阵'''
        dist_matrix_2 = dist_matrix_PTP()

        dist_min_all = []  # 找出每个个体中的所有相邻站间的距离
        for i in range(len(Index)):  # 当前个体Index[i]
            adj_list = []  # 存储p个站点距离近邻站点的距离的列表
            for f in range(len(Index[i])):
                adj_build = []  # 对于某一个站点，存储剩余p-1个站点到该站点的距离
                for g in range(len(Index[i])):
                    if g == f:
                        continue
                    else:
                        adj_build.append(dist_matrix_2[Index[i][f]][Index[i][g]])
                adj_list.append(min(adj_build))
            dist_min_all.append(adj_list)  # 找出每个个体中的所有相邻站间的距离

        mean_value = []
        for i in range(len(dist_min_all)):
            b = np.sum(dist_min_all[i], axis=0)
            c = -b / len(dist_min_all[i])
            mean_value.append(c)

        f3 = np.array(mean_value)
        """=============================找出不可行个体在种群中的索引值=============================="""

        '''第一个约束: 社区全覆盖约束的判别'''
        Commun_indexlist = [x for x in range(95)]
        exIdx_0 = []
        for i in range(len(Index)):
            code_index_8 = []  # 当前个体Vars[i]中所选建站点可以cover的社区索引值列表
            for l5 in range(len(Index[i])):
                code_index_8.append(overall_list_0[Index[i][l5]])

            comb_7 = []  # 当前个体Vars[i]中所选建站点可以cover的社区索引值去除重复值后的列表
            for l6 in range(len(code_index_8)):
                comb_7 += code_index_8[l6]
            comb_7 = np.unique(comb_7).tolist()  # 得到当前个体建站方案可以cover的所有社区索引值

            if set(comb_7) < set(Commun_indexlist):  # 若list4[i]为comb_7的子集，则说明当前建站方案可以覆盖当前个体所选的所有社区点
                exIdx_0.append(i)

        '''第二个约束: 个体对应建站方案的每个小型站有workload上限'''
        exIdx_1 = []
        for i in range(len(Index)):  # 当前个体索引值为i
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
        
        '''汇总不可行个体的索引值'''
        exIdx_all = list(np.unique(exIdx_0))  #  + exIdx_2+ exIdx_1
        
        """============================应用可行性法则处理约束条件==================================="""
        pop.ObjV = np.vstack([f1, f2, f3]).T  # ObjV是类型为np.array的列向量
        pop.CV = np.zeros((pop.sizes, 1))
        pop.CV[exIdx_all] = 1  # 把求得的违反约束程度矩阵赋值给种群pop的CV
