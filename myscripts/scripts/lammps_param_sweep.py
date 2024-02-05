#! /usr/bin/env python3

import pandas as pd
from joblib import Parallel, delayed
import time
from pathlib import Path
from rich import print as echo
import os
from typing import Optional, List
from typing_extensions import Annotated

from myscripts.src import LAMMPS_Project

import typer
app = typer.Typer()


def run(project, job_names, np, ncores, lmp_command): #Run all active jobs
    start_time = time.time()
    max_parallel_jobs = int(ncores//np)
    cmd = f"mpirun -np {np} {lmp_command}"
    if len(job_names) <= max_parallel_jobs:
        Parallel(n_jobs = max_parallel_jobs)(delayed(project.run_job)(job, cmd) for job in job_names)
    else: #chunk jobs into smaller arrays smaller than "max_parallel_jobs"
        job_names_chunked = [job_names[i:i + max_parallel_jobs] for i in range(0, len(job_names), max_parallel_jobs)]
        n_chunks = len(job_names_chunked)
        for i,chunk in enumerate(job_names_chunked):
            echo("===============");print(f"Batch {i+1} of {n_chunks}"); print("===============")
            Parallel(n_jobs = len(chunk))(delayed(project.run_job)(job, cmd) for job in chunk)
    echo("---All jobs took %s seconds ---" % (time.time() - start_time))

def setup(
        infile_path : Path,
        base_path : Path,
        project_name : str,
        param_combos_path : Path,
        n_runs : int, 
        seed_var_names : List[str]
    ):

    project = LAMMPS_Project(project_name, infile_path, base_path)

    combos = pd.read_csv(param_combos_path)
    job_names = []

    for _, combo in combos:
        job_name = ""
        for i, col in enumerate(combos.columns):
            job_name += f"{col}{i}"
        job_names.append(job_name)

        data = {col : combo[col] for col in combos.columns}
        project.new_job(job_name, n_runs, seed_var_names, data)

    return project, job_names

@app.command()
def main(
    infile_path: Annotated[
        Path, typer.Argument(help = "Path to lammps input script")
    ],
    base_path: Annotated[
        Path, typer.Argument(help = "Path where project files will be created")
    ],
    project_name: Annotated[
        str, typer.Argument(help = "Name of project folder to create")
    ],
    np: Annotated[
        int, typer.Argument(help = "Number of cores per job")
    ],
    ncores: Annotated[
        int, typer.Argument(help = "Number of cores to split jobs across")
    ],
    lmp_command: Annotated[
        Optional[str], typer.Argument(help = "Name of lammps command on this computer")
    ] = "lmp",
    seed_var_names: Annotated[
        Optional[List[str]], typer.Argument(help = "List of variables names in infile to be randomly generated")
    ] = ["velocity_seed"],
    param_combos_path: Annotated[
        Optional[str], typer.Argument(help = "File of parameter combos generated by `make_param_combos`")
    ] = os.path.join(os.getcwd(), "param_combos.csv")
):
    """
    Runs a set of jobs as defined by the set of parameter combinations at `param_combos_path`. Each job is run on
    `np` cores. If there the number of jobs times `np` is greater than `ncores` jobs will be queued.
    """
    proj, job_names = setup(infile_path, base_path, project_name, param_combos_path, seed_var_names)
    run(proj, job_names, np, ncores, lmp_command)

if __name__ == "__main__":
    app()