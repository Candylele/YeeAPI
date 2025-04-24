# 读取Excel中的数据存为[{},{},...{}]格式
import xlrd3
import os

class ExcelUtils:
    def __init__(self,excel_file_path,sheet_name):
        self.excel_file_path = excel_file_path
        self.sheet_name = sheet_name
        self.sheet = self.get_sheet()

    def get_sheet(self):  #打开表格
        work_book = xlrd3.open_workbook(self.excel_file_path)
        sheet = work_book.sheet_by_name(self.sheet_name)
        return sheet

    def get_row_count(self):  #获取行数
        row_count = self.sheet.nrows
        return row_count

    def get_column_count(self):  #获取列数
        column_count = self.sheet.ncols
        return column_count

    def get_merged_cell_value(self,row_index,col_index): #获取Excel单元格中的值
        for (min_row,max_row,min_col,max_col) in self.sheet.merged_cells:
            if min_row<=row_index<max_row and min_col<=col_index<max_col: #判断是否有合并单元格
                return self.sheet.cell_value(min_row,min_col)
        return self.sheet.cell_value(row_index,col_index)

    def get_excel_data_by_list(self):  #将Excel中的数据转为[{},{},...{}]格式
        excel_data = []
        first_row_data = self.sheet.row_values(0)
        for row_index in range(1,self.get_row_count()):  # 去掉表头
            row_dict = {}
            for col_index in range(self.get_column_count()):
                row_dict[first_row_data[col_index]] = self.get_merged_cell_value(row_index,col_index)
            excel_data.append(row_dict)
        return excel_data

if __name__ == "__main__":
    excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'test_data', 'testcase_infos.xlsx')
    list_value = ExcelUtils(excel_path,"Sheet1").get_excel_data_by_list()
    for value in list_value:
        print(value)

    # row1 = ExcelUtils(excel_path,"Sheet1").get_row_count()
    # print(row1)
    # col1 = ExcelUtils(excel_path,"Sheet1").get_column_count()
    # print(col1)

    # sheet1 = ExcelUtils(excel_path,"Sheet1").get_sheet()
    # for row in range(sheet1.nrows):
    #     for col in range(sheet1.ncols):
    #         value = sheet1.cell_value(row, col)
    #         print(value)

