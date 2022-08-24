# -*- coding: utf-8 -*-
import geatpy as ea
import warnings
import numpy as np
from MCLP_Macro.Draft5 import MyProblem  # 导入自定义问题接口: MCLP_Macro.MyProblem

# warnings.filterwarnings("ignore", category=Warning)


if __name__ == '__main__':
    problem = MyProblem()

    Encoding = 'RI'  # 编码方式
    NIND = 300  # 种群规模
    Field = ea.crtfld(Encoding, problem.varTypes, problem.ranges, problem.borders)  # 创建区域描述器
    population = ea.Population(Encoding, Field, NIND)  # 实例化种群对象（此时种群还没被初始化，仅仅是完成种群对象的实例化）
    """===============================算法参数设置============================="""
    myAlgorithm = ea.soea_SEGA_templet(problem, population)  # 实例化一个算法模板对象
    myAlgorithm.mutOper.Pm = 0.1  # 修改变异算子的变异概率
    myAlgorithm.recOper.XOVR = 0.9  # 修改交叉算子的交叉概率
    myAlgorithm.MAXGEN = 500  # 最大进化代数
    myAlgorithm.logTras = 1  # 设置每隔多少代记录日志，若设置成0则表示不记录日志
    myAlgorithm.verbose = True  # 设置是否打印输出日志信息
    myAlgorithm.drawing = 1  # 设置绘图方式（0：不绘图；1：绘制结果图；2：绘制目标空间过程动画；3：绘制决策空间过程动画）
    """==========================调用算法模板进行种群进化========================"""
    [BestIndi, population] = myAlgorithm.run()  # 执行算法模板，得到最优个体以及最后一代种群
    BestIndi.save()  # 把最优个体的信息保存到文件中
    """=================================输出结果=============================="""
    print('评价次数：%s' % myAlgorithm.evalsNum)
    print('时间已过 %s 秒' % myAlgorithm.passTime)

    '''
    result = list(BestIndi.Phen[0,:])
    print(result)
    Index_in_result = []
    for index, value in enumerate(result):
        if value == 1:
            # index+=2
            Index_in_result.append(index)

    k_value = BestIndi.ObjV[0][0]
    exIdx_result = []
    sum_result = []
    a=trans()
    for i in range(len(Index_in_result)):
        sum_result = np.sum([sum_result, a[Index_in_result[i]]], axis=0)
        if k_value in sum_result:
            exIdx_result.append(i)

    if exIdx_result == []:
        print('所得个体可覆盖所有需求点')
    else:
        print('所得个体不可覆盖所有需求点')
    '''

    if BestIndi.sizes != 0:
        print('最优的目标函数值为：%s' % BestIndi.ObjV[0][0])
        print('最优的控制变量值为：')
        for i in range(BestIndi.Phen.shape[1]):
            print(BestIndi.Phen[0, i])
    else:
        print('没找到可行解。')
