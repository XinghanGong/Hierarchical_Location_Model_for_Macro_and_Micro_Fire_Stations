# -*- coding: utf-8 -*-
import xlrd
from haversine import haversine_vector, Unit


class excel_read:
    def __init__(self, excel_path, index):
        self.data = xlrd.open_workbook(excel_path)
        self.table = self.data.sheets()[index]
        self.rows = self.table.nrows

    def get_data(self):
        result = []
        for i in range(self.rows):
            col = self.table.row_values(i)  
            result.append(col)
        del result[0]
        return result










