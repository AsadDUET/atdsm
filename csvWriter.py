# -*- coding: utf-8 -*-
"""
Created on Wed May 27 23:13:43 2020

@author: Asad
"""
import csv
def write():
    with open('employee_file.csv', mode='a') as employee_file:
        employee_writer = csv.writer(employee_file,lineterminator = '\n')
        employee_writer.writerow(['John Smith', 'Accounting', 'November'])
    