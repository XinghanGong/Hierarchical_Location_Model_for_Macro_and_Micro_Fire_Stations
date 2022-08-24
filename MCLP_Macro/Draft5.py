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


class MyProblem(ea.Problem):  # 继承Problem父类
    def __init__(self, M=1):
        name = 'MyProblem'  # 初始化name（函数名称，可以随意设置）
        Dim = 239  # 初始化Dim（决策变量维数）
        maxormins = [-1] * M  # 初始化maxormins（目标最小最大化标记列表，1：最小化该目标；-1：最大化该目标）
        varTypes = [1] * Dim  # 初始化varTypes（决策变量的类型，0：实数；1：整数）
        lb = [0] * Dim  # 决策变量下界
        ub = [0] * Dim  # 决策变量上界
        lbin = [1] * Dim  # 决策变量下边界（0表示不包含该变量的下边界，1表示包含）
        ubin = [1] * Dim  # 决策变量上边界（0表示不包含该变量的上边界，1表示包含）
        # 调用父类构造方法完成实例化
        ea.Problem.__init__(self, name, M, maxormins, Dim, varTypes, lb, ub, lbin, ubin)

    def aimFunc(self, pop):  # 目标函数

        """=========================相关参数设定=========================="""
        # AveSpeed = 26  # 19年工作日高峰时段平均时速, 单位km/h
        R = 1.746  # 28km/h:1.867  # 26km/h:1.733  # (AveSpeed*4)/60  # 服务半径: 大型站要求4min到达现场，单位km

        Num_Build = 3  # 建站数量
        d_l = 2 * R + 0.05  # 消防站间最远距离
        d_s = 2.043  # 消防站间最近距离
        # r = 0.295

        """=========================生成初始种群=========================="""
        Vars = pop.Phen  # 得到决策变量矩阵

        num_list = [x for x in range(239)]
        rand_num = []  # rand_num里的每个元素即是当前个体的建站方案
        for l in range(300):
            b = random.sample(num_list, 3)
            rand_num.append(b)

        for i in range(len(Vars)):
            for j in range(len(rand_num[i])):
                Vars[i][rand_num[i][j]] = 1
        Vars = np.array(Vars)

        """=======================构造目标函数f1=========================="""
        excel_path_0 = r'/zengyp/Xinghan/Macro_Experience_Record/overlaprate30_p3_jianbiao/RiskValue_jainbiao.xls'
        risk = xlrd.open_workbook(excel_path_0)
        sheet = risk.sheet_by_index(0)
        RiskValue = sheet.col_values(0)
        del RiskValue[0]  # 去掉开头的字符
        # s = np.sum(RiskValue, axis=0)

        dist_matrix_1 = dist_matrx_1()  # 计算候选点间距离矩阵，其中元素为某候选点到其余所有候选点间距离构成的列表
        dist_matrix_3 = dist_matrx_3()  # 计算候选点与社区间距离矩阵，其中元素为某候选点到所有社区点的距离构成的列表
        Index = rand_num  # 每个元素即是当前个体的建站方案


        overall_list_0 = []
        code_list_0 = []
        for i in range(len(dist_matrix_3)):
            index_0 = []
            code_idx = []
            for j in range(len(dist_matrix_3[0])):
                if dist_matrix_3[i][j] <= R:
                    index_0.append(j)
                    code_idx.append(1)  # 1: 在候选点的R范围之内; 0: 反之
                else:
                    code_idx.append(0)
            overall_list_0.append(index_0)  # overall_list_0中的元素为某候选点R范围内的社区点索引值
            code_list_0.append(code_idx)  # code_list中的元素为由overall_list中索引值对应构成的0-1列表

        f1 = [0]*300
        for i in range(len(Vars)):  # Index中每个元素即是当前个体的建站方案
            New_list_0 = []  # 找出Index[i]对应于overall_list中的元素

            for j in range(len(Index[i])):
                New_list_0.append(overall_list_0[Index[i][j]])

            '''将New_list_0中社区点索引值合并去掉重复值'''
            New_list_1 = []
            for k in range(len(New_list_0)):
                New_list_1 += New_list_0[k]
            New_list_1 = np.unique(New_list_1).tolist()  # 得到所有在被选中社区R范围的候选点索引值

            '''New_list_1中元素与RiskValue中值对应然后求和'''
            Sum_value = 0
            for k in range(len(New_list_1)):
                Sum_value = Sum_value + RiskValue[New_list_1[k]]
            f1[i] = Sum_value

        f1 = np.array(f1)

        """===============主循环: 找出所有不可行个体在种群中的索引值============="""

        exIdx = []  # 不可行个体索引值列表
        # code_list_0 = list(map(list, zip(*code_list_0))), 将code_list_0转置

        for i in range(len(Vars)):  # 当前个体: Vars[i]
            adj_list = []  # 存储p个站点距离近邻站点的距离的列表
            for f in range(len(rand_num[i])):
                adj_build = []  # 对于某一个站点，存储剩余p-1个站点到该站点的距离
                for g in range(len(rand_num[i])):
                    if g == f:
                        continue
                    else:
                        adj_build.append(dist_matrix_1[rand_num[i][f]][rand_num[i][g]])
                adj_list.append(min(adj_build))

            max_dist = max(adj_list)  # 与每一个站点相邻的站点的距离，p者取最大
            min_dist = min(adj_list)  # 与每一个站点相邻的站点的距离，p者取最小

            if max_dist <= d_l and min_dist >= d_s:
                # print(rand_num[i])
                continue
            else:
                exIdx.append(i)

        print(len(exIdx))  # 循环到最后若len(exIdx)==200, 则说明种群没有可行个体

        """============================应用可行性法则处理约束条件==================================="""
        pop.ObjV = np.vstack(f1)  # ObjV是类型为np.array的列向量
        pop.CV = np.zeros((pop.sizes, 1))
        pop.CV[exIdx] = 1  # 把求得的违反约束程度矩阵赋值给种群pop的CV

        # 罚函数方法: 不推荐，因为难以确定相关参量数值；
        # alpha =0.2  # 惩罚缩放因子
        # beta = 0.1  # 惩罚最小偏移量
        # f1[exIdx] = f1[exIdx] + self.maxormins[0] * alpha * (np.max(f1) - np.min(f1) + beta)

        # 自定义惩罚方法:
        # f1[exIdx] = f1[exIdx]-0.05  #- np.min(f1)














