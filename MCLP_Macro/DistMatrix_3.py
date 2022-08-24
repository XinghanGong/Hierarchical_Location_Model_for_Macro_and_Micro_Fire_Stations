# -*- coding: utf-8 -*-
from geopy.distance import geodesic
from MCLP_Macro.Read_Excel import excel_read


def dist_matrx_3():
    excel_path_1 = r'/zengyp/Xinghan/Macro_Experience_Record/overlaprate30_p3_jianbiao/CommunPoint_overlap30_jianbiao.xls'
    excel_path_2 = r'/zengyp/Xinghan/Macro_Experience_Record/overlaprate30_p3_jianbiao/PotentialPoint_overlap30_jianbiao.xls'
    index = 0
    m = excel_read(excel_path_1, index).get_data()
    n = excel_read(excel_path_2, index).get_data()


    dist_matrix_7 = []
    for l1 in range(len(n)):
        L = []
        for l2 in range(len(m)):
            x = geodesic(n[l1], m[l2]).km
            L.append(x)
        dist_matrix_7.append(L)

    return dist_matrix_7