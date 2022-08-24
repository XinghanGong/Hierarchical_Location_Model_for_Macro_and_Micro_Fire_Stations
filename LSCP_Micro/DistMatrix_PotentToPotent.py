from Read_Excel import excel_read
from geopy.distance import geodesic


def dist_matrix_PTP():
    excel_path_1 = r'/zengyp/Xinghan/Miro_Exp_Record/CommunPoint_Newest.xls'
    excel_path_2 = r'/zengyp/Xinghan/Miro_Exp_Record/PotentPoint_xishu.xls'
    ind = 0
    n = excel_read(excel_path_2, ind).get_data()

    dist_matrix_2 = []
    for i in range(len(n)):
        ac = []
        for j in range(len(n)):
            x = geodesic(n[i], n[j]).km
            ac.append(x)
        dist_matrix_2.append(ac)

    return dist_matrix_2


