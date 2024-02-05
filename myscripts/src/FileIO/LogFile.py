import numpy as np

class LogFile():
    '''
    '''

    def __init__(self, path):
        '''
        Path: Absolute file path to the log-file, contains filename and extension.
        e.g. C:/Users/ejmei/Desktop/log.lammps
        '''
        self.path = path


    def parse_thermo_table(self):
        with open(self.path,'r') as f:
            start_line = -1
            end_line = -1
            lines = f.readlines()
            for i,line in enumerate(lines):
                if line.strip().startswith("Per MPI rank"):
                    start_line = i + 1
                if line.strip().startswith("Loop time"):
                    end_line = i - 1
            data = lines[start_line : end_line + 1]

        #Parse out column headings
        data = np.array(data)
        column_headings = data[0].strip().split()
        data = data[1:] 
        #Parse data
        data = [[float(val) for val in line.strip().split()] for line in data]

        #Build output dictionary
        data = np.array(data)
        data_dict = {column_headings[i]:data[:,i] for i in range(len(column_headings))}
        return data_dict
