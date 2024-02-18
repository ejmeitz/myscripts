# ### Run multiple MD simulations with different velocity seeds
# ### to get set of configurations that are uncorrelated and better
# ### represent all of phase space.

# from src import LAMMPS_Project
# from joblib import Parallel, delayed
# import numpy as np
# import os

# ## MD PARAMETERS ################

# # Different configurations to generate
# # Will generate max from this list and sample to create others
# N_samples = [10,20,30,40,50,75,100,150,200,300,400]

# # Number of simulations to run to generate configurations
# N_simulations = 20
# N_steps_per_simulation = 1000000


# temp = 1600
# infile_path = "/home/emeitz/scripts/TDEP/SW/TDEP_SW.in"
# project_name = f"SW_3UC_TDEP_Samples_{temp}"
# base_path = os.getenv("EXTRA_STORAGE")

# ncores = 40
# n_mpi_domains = 4
# dump_header_len = 9

# ## TDEP PARAMETERS #############

# r_cut2 = 3.77118
# r_cut3 = 3.77118
# dt_fs = 1
# num_unit_cell = 3
# N_atoms = 216
# ucposcar_path = r"/home/emeitz/scripts/TDEP/SW/infile.ucposcar"
# tdep_bin = "/home/emeitz/software/tdep-devel/bin"
# TDEP_script_path = "/home/emeitz/scripts/TDEP/TDEP_from_MD.py"

# ##############################


# N_samples_max = np.amax(N_samples)
# samples_per_simulation = N_samples_max / N_simulations
# data_interval = int(np.ceil(N_steps_per_simulation/samples_per_simulation))


# #Run Simulations
# folder_name = "simulation_results"
# proj = LAMMPS_Project(project_name, infile_path, base_path)
# proj.new_job(folder_name, N_simulations, ["velocity_seed"], {"T" : temp, "N_steps" : N_steps_per_simulation, "data_interval" : data_interval})
# proj.run_all_jobs_mpi(ncores, n_mpi_domains)


# # Compile Outputs from Each Simulation into One File
# compiled_data_path = os.path.join(proj.outpath, "COMPILED_DATA")
# os.mkdir(compiled_data_path)

# dump_files_to_concat = ["dump.positions", "dump.positions_unrolled", "dump.forces"]
# printed_files_to_concat = ["dump.stat"] #first line is comment each other line corresponds to one step
# files_to_copy = ["equilibrium.atom", "equilibrium.energies"]

# #Copy eq.atom and eq.energies to each folder
# for n_samp in np.sort(N_samples):
#     out_file_path = os.path.join(compiled_data_path, f"N_{n_samp}")
#     os.mkdir(out_file_path)
#     for file in files_to_copy:
#         current_path = os.path.join(proj.outpath, folder_name, f"seed0", file)
#         copy_to = os.path.join(out_file_path, file)
#         os.system(f"cp {current_path} {copy_to}")

# #Create version with all samples
# lines_per_sample = (N_atoms + dump_header_len)
# max_lines_to_copy = N_samples_max * lines_per_sample
# first_out_file_path = os.path.join(compiled_data_path, f"N_{N_samples_max}")
# for file in dump_files_to_concat:
#     lines_copied = 0
#     with open(os.path.join(first_out_file_path, file), "w") as outfile:   
#         for i in range(N_simulations):
#             infile_path = os.path.join(proj.outpath, folder_name, f"seed{i}", file)
#             with open(infile_path, "r") as infile:
#                 for line in infile:
#                     if lines_copied < max_lines_to_copy:
#                         outfile.write(line)
#                         lines_copied += 1

# max_lines_to_copy = N_samples_max
# for file in printed_files_to_concat:
#     lines_copied = 0
#     with open(os.path.join(first_out_file_path, file), "w") as outfile:
#         outfile.write("# Comment line: Fix print output\n")
#         for i in range(N_simulations):
#             infile_path = os.path.join(proj.outpath, folder_name, f"seed{i}", file)
#             with open(infile_path, "r") as infile:
#                 for line_num, line in enumerate(infile):
#                     if line_num != 0 and lines_copied < max_lines_to_copy:
#                         outfile.write(line)
#                         lines_copied += 1

# #Create folders for other samples and copy portion of compiled data
# for n_samp in np.sort(N_samples)[:-1]:
#     out_file_path = os.path.join(compiled_data_path, f"N_{n_samp}")

#     sample_idxs = np.sort(np.random.choice(range(N_samples_max), n_samp, replace=False))

#     for file in printed_files_to_concat:
#         with open(os.path.join(out_file_path, file), "w") as outfile:
#             outfile.write("# Comment line: Fix print output\n")
#             infile_path = os.path.join(compiled_data_path, f"N_{N_samples_max}", file)
#             with open(infile_path, "r") as infile:
#                 for line_num, line in enumerate(infile):
#                     if line_num != 0 and (line_num-1) in sample_idxs:
#                         outfile.write(line)

#     #Sample Dump Files
#     for file in dump_files_to_concat:
#         infile_path = os.path.join(compiled_data_path, f"N_{N_samples_max}", file)
#         with open(os.path.join(out_file_path, file), "w") as outfile, open(infile_path, "r") as infile:

#             lines_per_sample = (N_atoms + dump_header_len)
#             sample_idx = 0
#             it = np.nditer(sample_idxs);
#             next_sample_idx = it[0]
#             while not it.finished:
#                 if sample_idx == next_sample_idx:
#                     for _ in range(lines_per_sample):
#                         outfile.write(infile.readline())
#                     sample_idx += 1
#                     it.iternext()
#                     if not it.finished:
#                         next_sample_idx = it[0]
#                     else:
#                         break
#                 else: #skip lines and iterator sample_idx
#                     for _ in range(lines_per_sample):
#                         infile.readline();
#                     sample_idx += 1
                

# #Activate version of TDEP that can remap-forceconstants
# current_path = os.environ.get('PATH', '')
# new_path = f'{tdep_bin}:{current_path}'
# os.environ['PATH'] = new_path

# #Call Main TDEP Script

# for i, n_samp in enumerate(N_samples):
#     print(f"Running TDEP on {n_samp} Samples")
#     path = os.path.join(compiled_data_path, f"N_{n_samp}")
#     os.system(f"python3 {TDEP_script_path} -T {temp} -dt {dt_fs} -nuc {num_unit_cell} -p {path} -ucp {ucposcar_path} -nt {ncores} -r2 {r_cut2} -r3 {r_cut3} -nsteps {n_samp}")


# # Parse Force Constants to Julia

