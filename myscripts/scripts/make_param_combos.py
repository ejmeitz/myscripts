#! /usr/bin/env python3

import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Optional
from typing_extensions import Annotated

from itertools import product
import os
import ast

import typer
app = typer.Typer()

def process(data: str):
    try:
        return ast.literal_eval(data)
    except (ValueError, SyntaxError) as e:
        typer.echo(f"Error parsing param_values as list of lists from string: {e}")

@app.command()
def main(
    param_names: Annotated[
        str, typer.Argument(help = "Names of parameters which match the names of the variables in the LAMMPS in file")
    ],
    param_values: Annotated[
        str, typer.Argument(help = "List of lists of parameter values formated as a string. For example, '[[1,2], [3,4]]'")
    ],
    index_by: Annotated[
        Optional[List[int]], typer.Argument(help = "List of integers that tell the function how to generate the combinations. If the entry is -1, then \
        the parameter is included when calculating all combinations. If an integer is given, then that parameter is always matched \
        to the value in that list.")
    ] = None,
    outfile_path: Annotated[
        Optional[Path], typer.Argument(help = "Dir where the combinations will be saved", show_default="current directory")
    ] = Path(os.getcwd())
):
    """
    Create a csv file with all combinations of parameters.
    
    Example:
    param_names = "['Temp', 'Interval', 'Lattice_const']"
    param_values = "[[10, 20, 30], [1, 2], [5.5, 5.4, 5.3]]"
    outfile_path = "C:/Users/<username>/Desktop"
    index_by = [-1, -1, 0]

    Example Usage:
    make_param_combos "['Temp', 'Interval', 'Lattice_const']" "[[10, 20, 30], [1, 2], [5.5, 5.4, 5.3]]" --index-by -1 --index-by -1 --index-by 0

    This will generate the following combinations. Note how the lattice constant is always pegged to the temperature.
    10 1 5.5
    10 2 5.5
    20 1 5.4
    20 2 5.4
    30 1 5.3
    30 2 5.3
    """

    param_names = process(param_names)
    param_values = process(param_values)

    assert len(param_names) == len(param_values), f"Number of parameter names ({len(param_names)}) does not match number of parameter values ({len(param_values)})"
    assert len(index_by) == len(param_names), f"Length of index_by ({len(index_by)}) does not match number of parameters ({len(param_names)})"
    assert np.all(index_by != np.arange(0,len(index_by))), f"Cannot index param with itself"

    if index_by == None:
        index_by = -1*np.ones(len(param_names))
    else:
        index_by = np.array(index_by)

    param_values = np.array(param_values, dtype = object)
    param_names = np.array(param_names)

    combos = product(*param_values[index_by == -1])
    n_combos = np.prod([len(param_values[i]) for i in range(len(param_values)) if index_by[i] == -1])
    data = {param_names[i] : np.zeros(n_combos) for i in range(len(param_names))}

    for i, combo in enumerate(combos):
        for j, param_name in enumerate(param_names):
            if index_by[j] == -1:
                data[param_name][i] = combo[j]
            else:
                combo_np = np.array(combo)
                other_idx = np.where(param_values[index_by[j]] == combo_np[index_by[j]])[0][0]
                data[param_name][i] = param_values[j][other_idx]

    df = pd.DataFrame(data)
    df.to_csv(os.path.join(outfile_path, "param_combos.csv"), index=False)


if __name__ == "__main__":
    app()