from LSCP_Micro.Read_Excel import excel_read
from geopy.distance import geodesic


def dist_matrix_PTC():
    excel_path_1 = r'/zengyp/Xinghan/Miro_Exp_Record/CommunPoint_Newest.xls'
    excel_path_2 = r'/zengyp/Xinghan/Miro_Exp_Record/PotentPoint_xishu.xls'
    ind = 0
    m = excel_read(excel_path_1, ind).get_data()
    n = excel_read(excel_path_2, ind).get_data()

    dist_matrix = []
    for i in range(len(n)):
        a = []
        for j in range(len(m)):
            x = geodesic(n[i], m[j]).km
            a.append(x)
        dist_matrix.append(a)

    return dist_matrix
