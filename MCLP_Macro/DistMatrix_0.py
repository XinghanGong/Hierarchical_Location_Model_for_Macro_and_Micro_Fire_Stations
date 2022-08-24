# -*- coding: utf-8 -*-
from geopy.distance import geodesic
from MCLP_Macro.Read_Excel import excel_read
import numpy as np

def dist_matrx():
    excel_path_1 = r'/zengyp/Xinghan/Macro_Experience_Record/overlaprate30_p3_jianbiao/CommunPoint_overlap30_jianbiao.xls'
    excel_path_2 = r'/zengyp/Xinghan/Macro_Experience_Record/overlaprate30_p3_jianbiao/PotentialPoint_overlap30_jianbiao.xls'
    index = 0
    m = excel_read(excel_path_1, index).get_data()
    n = excel_read(excel_path_2, index).get_data()

    dist_matrix = []
    for i in range(len(m)):
        a = []
        for j in range(len(n)):
            x = geodesic(m[i], n[j]).km
            a.append(x)
        dist_matrix.append(a)
    return dist_matrix






