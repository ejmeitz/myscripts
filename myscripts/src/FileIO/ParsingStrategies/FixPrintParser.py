import numpy as np
from .AbstractParsingStrategy import AbstractParsingStrategy


class FixPrintParser(AbstractParsingStrategy):
    '''
    Implementation of AbstractParsingStrategy designed for data output as columns.
        This object should work to parse the output of commands like:
        "fix Uavg all ave/time 100 5 1000 c_2 v_pesq file Uavg.txt"
        
    Assumes the first non-commented line is the data and the commented line before
        that is the column headings. Also assumes all data is numeric and casts
        them to a float.
    '''

    def __init__(self):
        super().__init__()
    
    def parse(self, path : str, comment_str = "#", delimiter = None) -> dict:
        data = []
        with open(path,'r') as f:
            first_data_line = -1
            lines = f.readlines()
            for i in range(len(lines)):
                if not lines[i].strip().startswith(comment_str):
                    #Record first line to contain data
                    if first_data_line == -1:
                        first_data_line = i
                    #Parse data on line and convert to float
                    line_data = lines[i].strip().split(delimiter)
                    data.append([float(val) for val in line_data])
            column_heading_line = first_data_line - 1
            column_headings = lines[column_heading_line].replace(comment_str,'').strip().split()

        #Build output dictionary
        data = np.array(data)
        data_dict = {column_headings[i]:data[:,i] for i in range(len(column_headings))}

        return data_dict