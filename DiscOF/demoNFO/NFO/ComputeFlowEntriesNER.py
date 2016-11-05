'''
Created on Apr 26, 2014

@author: Luiza Nacshon
'''
#made for the result
import routePlan
import os
import json
import datetime
import csv
from collections import OrderedDict
list_of_values=[]
list_of_values.append(28)
list_of_values.append(28)
list_of_values.append(24)

def gini(list_of_values):
  sorted_list = sorted(list_of_values)
  height, area = 0, 0
  for value in sorted_list:
    height += value
    area += height - value / 2.
  fair_area = height * len(list_of_values) / 2
  return (fair_area - area) / fair_area

print gini(list_of_values)

