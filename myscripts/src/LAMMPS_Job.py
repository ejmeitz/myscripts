import os
import numpy as np
import shutil
import time
from typing import Type

from ..FileIO.InFile import InFile

class LAMMPS_Job:

    def __init__(self, parent_project, name: str, n_seeds: int, seed_variables :list, variables : dict = None):
        '''
        Parent Project: Type of LAMMPS_Project, contains the information about where files will be saved etc.
        Name: Name to be used when file to store job is created
        n_seeds: Number of seeds to run.
        seed_variables: Name of variables in the in-file to change with each seed (e.g. velocity_seed). If more than
            one variable is passed they will be changed at the same time and not generate all combinations. The seed
            is generated randomly from 1000-1000000
        variables: Dictionary of variable name & value pairs. For example {"Temps": [10, 20, 30]}. The name in the
            keys should match a variable in the LAMMPS input file.
        '''
        self.parent_project = parent_project
        self.name = name
        self.variables = variables
        self.n_seeds = n_seeds
        self.seed_variables = seed_variables

        '''
        Outpath: Path to output for this job. Will be inside parent project folder.
        In-File Name: Name generated from parent_project in-file and ID
        In-File Path: Path to in-file for this job.
        In-File: An InFile object which parses and manipultes the in-file text.
        '''
        self.outpath = None
        self.in_file_name = None

        self.__create_output_file_structure()
        self.__create_in_files()



    def __create_output_file_structure(self) -> None:
        '''
        Creates a subfolder inside of the parent_project folder. All of the files
            associated with this job (e.g. in-file, dumps) are saved here.
        '''
        self.outpath = os.path.join(self.parent_project.outpath, self.name)
        #Create sub-folder if this is first time job is excuted
        if not os.path.exists(self.outpath):
            try:
                for i in range(self.n_seeds):
                    os.makedirs(os.path.join(self.outpath, f"seed{i}"))
            except PermissionError:
                raise PermissionError(f"Python does not have permission to create directory: {self.outpath}")
        else:
            raise RuntimeError(f"Folder already exists: {self.outpath}")
        

    def __create_in_files(self) -> None:
        '''
        Using the 'variables' member variable create a modified version of the in-file
            from the 'parent_project'. File will be written to this Job's output folder.
        '''
        #Build in-file name from parent project name and job name
        parent_in_file_name = os.path.basename(self.parent_project.infile_path)
        self.in_file_name = parent_in_file_name + "_" + self.name


        for i in range(self.n_seeds):
            seed_outpath = os.path.join(self.outpath, f"seed{i}")
            in_file_path = os.path.join(seed_outpath, self.in_file_name)

            #Check if the in-file for this job was already created previously
            if not os.path.isfile(in_file_path):
                #Copy parent-project in-file to this job's sub-folder
                shutil.copy2(self.parent_project.infile_path, seed_outpath)

                #Rename in-file to incldue job name
                os.rename(os.path.join(seed_outpath,parent_in_file_name), in_file_path)

                in_file = InFile(in_file_path)
                
                if self.variables is not None:
                    #Modify variables inside in-file to match user changes
                    in_file.edit_variables(self.variables)
                
                    #Modify seed_variables
                    for sv in self.seed_variables:
                        if sv in self.variables:
                            in_file.edit_variables({sv : np.random.randint(1000,1000000)})
                        else:
                            raise RuntimeError(f"Key {sv} was not found in file. Cannot modify. Aborting.")



    def run(self, lammps_env_var, seed_num) -> int:
        '''
        Executes job through LAMMPS CLI.
        Can pass env var as "lmp_serial" for serial or "mpirun -np {#} lmp_mpi" for mpi
        '''

        print("===============================")
        print(f"Attempting To Run: {self.name}")
        print("===============================\n")
        #Build and run command to exectue LAMMPS

        #cd to project folder cause LAMMPS dumps output at path it is run from
        os.chdir(os.path.join(self.outpath, f"seed{seed_num}"))   
        infile_path = os.path.join(self.outpath, f"seed{seed_num}",self.in_file_name)
        #Build and run lammps command
        start_time = time.time()
        res = os.system(f"{lammps_env_var} -in {infile_path} -screen none")
        print("--- %s seconds ---" % (time.time() - start_time))
        return res
