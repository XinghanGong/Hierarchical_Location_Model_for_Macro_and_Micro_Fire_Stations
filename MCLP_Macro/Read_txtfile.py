import numpy as np

def Read_list(filename):
    file1 = open(filename + ".txt", "r")
    list_row = file1.readlines()
    list_source = []
    for i in range(len(list_row)):
        column_list = list_row[i].strip().split("\t")
        list_source.append(column_list)
    for i in range(len(list_source)):
        for j in range(len(list_source[i])):
            list_source[i][j] = float(list_source[i][j])
    file1.close()
    return list_source