from typing import Any, Optional, List
import numpy as np
from itertools import product


def make_param_combos(
    params : dict[str, List[Any]],
    index_by: Optional[List[int]] = None,
    ) -> dict[str, np.ndarray]:

    """
    Create a dictionary of all combinations of parameters. Combinations are returned as a dictionary of numpy arrays.
    
    Parameters:
    -----------
    - `params : dict`: Dictionary of parameter names and values. Names should be strings, value should be lists.
    - `index_by : Optional[List[int]]` : List of integers that tell the function how to generate the combinations.
       If the entry is -1, then the parameter is included when calculating all combinations.
       If an integer is given, then that parameter is always matched to the value in that list.

    Returns:
    --------
    - `data : dict` : Dictionary of parameter names and their value for a given combination. 
    For example, the entry in position 0 of each value in the dictionary is the first combination.

    Example:
    --------
    ```python
    params = {'Temp': [10, 20, 30], 'Interval': [1, 2], 'Lattice_const': [5.5, 5.4, 5.3]}
    outfile_path = "C:/Users/username/Desktop"
    index_by = [-1, -1, 0]
    ```
    These inputs will generate the following combinations. 
    ```python
    {'Temp': array([10., 10., 20., 20., 30., 30.]),
     'Interval': array([1., 2., 1., 2., 1., 2.]),
     'Lattice_const': array([5.5, 5.5, 5.4, 5.4, 5.3, 5.3])}
    ```
    The first parameter combo is the first enetry in each array, and so on. Note how the lattice constant
    is always pegged to the temperature.
    """

    if index_by == None:
            index_by = -1*np.ones(len(param_names))
    else:
        index_by = np.array(index_by)

    param_values =  [np.array(arr) for arr in params.values()]
    param_names = np.array(list(params.keys()))

    combos = product(*[pv for i,pv in enumerate(param_values) if index_by[i] == -1])
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

    return data