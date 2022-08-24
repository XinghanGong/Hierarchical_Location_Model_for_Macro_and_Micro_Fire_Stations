# -*- coding: utf-8 -*-
from geopy.distance import geodesic
import xlrd
import numpy as np
from DistMatrix_PotentToPotent import *
from DistMatrix_PotentToCommun import *

class excel_read_1:
    def __init__(self, excel_path, index):
        self.data = xlrd.open_workbook(excel_path)  # 获取文本对象
        self.table = self.data.sheets()[index]  # 根据index获取某个sheet
        self.rows = self.table.nrows  # 获取当前sheet页面的总行数,把每一行数据作为list放到 list

    def get_data(self):
        result = []
        for i in range(self.rows):
            col = self.table.row_values(i)  ##获取每一列数据
            result.append(col)
        return result


if __name__ == '__main__':
    excel_path_1 = r'/zengyp/Xinghan/ModPaper_Exp/ComputeWorkload/Nind_300/Exp2/Result/Phen.xls'  # r'/zengyp/Xinghan/Miro_Exp_Record/NSGA3_Obj3_Repeat.xls' # r'/zengyp/Xinghan/Miro_Exp_Record/NSGA2_Obj3_Repeat.xls' # r'/zengyp/Xinghan/Miro_Exp_Record/Three_Obj_0.xls' # r'/zengyp/Xinghan/Miro_Exp_Record/Exp3_Result/Chrom_Exp3_repeat.xls'  # r'/zengyp/Xinghan/Miro_Exp_Record/Exp3_Result/Chrom_Exp3.xls'
    index = 0  # 读取excel文档中的sheet0
    m = excel_read_1(excel_path_1, index).get_data()

    R = 1
    d_s = 1.170

    """找出每个个体的建站点索引值"""
    Index = []
    for i in range(len(m)):
        Index_0 = []
        for j in range(len(m[0])):
            if m[i][j] == 1:
                Index_0.append(j)
        Index.append(Index_0)  # 最后得到形如[[...],...,[...]]的Index列表，每个元素对应Vars中每个个体的所选建站点的索引值

    """找出每个个体的建站总数"""
    Build_Total = []
    for i in range(len(Index)):
        Build_Total.append(len(Index[i]))

    """引入站间距离矩阵"""
    dist_matrix_2 = dist_matrix_PTP()

    """判断Chrome_Result中是否存在满足距离约束条件的个体"""
    Unfeas_Num = []  # 记录每个个体Index[i]中不符合相邻站间距离约束建站点的个数
    dist_min_all = []  # 找出每个个体中的所有相邻站间的距离
    exIdx_2 = []
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

        max_dist = max(adj_list)
        min_dist = min(adj_list)

        Unfeas_0 = []  # 过渡用列表
        for k in range(len(adj_list)):
            if adj_list[k] < d_s:
                Unfeas_0.append(k)
        Unfeas_Num.append(len(Unfeas_0))  # 记录当前个体Index[i]中不符合相邻站间距离约束建站点的个数

        if d_s <= min_dist:
            continue
        else:
            exIdx_2.append(i)
    print('不可行方案数: ',len(exIdx_2))
    """若上一步中发现不存在满足距离约束条件的个体，则寻找近似最优个体"""

    '''近似最优定义1: 不满足相邻站建站点个数占当前个体总建站数的比值最小的个体'''
    Ratio_Unfeas = np.divide(np.array(Unfeas_Num),np.array(Build_Total))

    index_value_0 = min(Ratio_Unfeas)

    OptSolution_0 = []  # [14, 107, 176]
    for i in range(len(Ratio_Unfeas)):
        if Ratio_Unfeas[i] == index_value_0:
            OptSolution_0.append(i)
    print('不满足相邻距离约束站点比值最小的个体: ', OptSolution_0)
    '''for i in range(len(OptSolution_0)):
        print(Build_Total[OptSolution_0[i]])'''

    '''近似最优定义2: 相邻站间平均距离最大的个体'''
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
    print('相邻距离最大的个体: ', OptSolution_1)
    '''for i in range(len(OptSolution_1)):
        print(Build_Total[OptSolution_1[i]])'''

    """计算两种定义所得个体对应的workload值"""
    OptSolution_Total = OptSolution_0 + OptSolution_1  # 合并个体索引值列表
    print(OptSolution_Total)
    '''计算元素为某候选点到所有社区的距离矩阵'''
    dist_matrix = dist_matrix_PTC()  # 计算元素为某候选点到所有社区的距离矩阵

    '''将候选点与社区点间矩阵转换成0-1矩阵: code_list_0'''
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

    '''基于overall_list_1与RiskValue构造"A"列表'''
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
        risk = np.sum(risk, axis=0)
        risk_matrix.append(risk)

    Index_feas = []  # 得到近似最优个体所选建站点索引值
    for i in range(len(OptSolution_Total)):
        Index_feas.append(Index[OptSolution_Total[i]])

    workload_s = []
    for i in range(len(Index_feas)):
        risk_cal = [0]
        for j in range(len(Index_feas[i])):
            risk_cal = np.sum([risk_cal,risk_matrix[Index_feas[i][j]]], axis=0)
        risk_total_num = np.divide(np.array(risk_cal),np.array(Build_Total[OptSolution_Total[i]]))
        workload_s.append(risk_total_num[0])

    print(workload_s)  # [17.666666666666668, 17.666666666666668, 17.666666666666668, 17.884615384615383, 17.884615384615383]