import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import MaxNLocator


def block_ave(array,threshold=0.025, time_step=1, visualize=False):
    """
    Given a 1D array of equally spaced time-series data with an unknown correlation time,
    this function estimates the correlation time and variance associated
    with the best block transformation of the data.

    inputs: 
        array: numpy array of equally space time-series data
        threshold: float, threshold for the first derivative of the normalized variance
        time_step: float, time step between data points
        visualize: boolean, whether or not to plot the variance as a function of block size
    
    returns: 
        best_transform: number of block transformations that gave the best estimate of the variance
        t_decorrelation: estimated correlation time
        estimate_var: estimated variance of the data given len(array) // 2 ** (best_transform + 1) decorrelated samples
    """
    # Number of block transformations we apply corresponds to the number of times we divide by 2 and still have (at least) 10 blocks 
    upper_limit = len(array) // 10
    n_transforms = int(np.floor(np.log2(upper_limit)))
    variances = np.empty(n_transforms)
    errors = np.empty(n_transforms)
    block_sizes = np.empty(n_transforms)
    block_size = 1
    block_sizes[0] = block_size
    for i in range(n_transforms):
        n_blocks = len(array) // block_size
        blocks = np.mean(array[:n_blocks * block_size].reshape(-1, block_size), axis=1)
        mu = np.mean(blocks)
        var = np.var(blocks) 
        forth_mom = np.mean((blocks - mu)**4)
        variances[i] = var / (n_blocks - 1)
        errors[i] = np.sqrt(2*forth_mom/(n_blocks-1)**3)
        block_size *= 2
        block_sizes[i] = block_size
    
    # Normalize variances 
    vars_norm = (variances - variances.min()) / (variances.max() - variances.min())
    # Approximate first derivative with finite difference
    d_var = np.diff(vars_norm)
    d_block = np.diff(block_sizes)
    slopes = d_var / d_block
    # Normalize slopes to be within -1 to 1 
    slopes /= np.abs(slopes).max()
    # Find the first value where the slope is less than the threshold
    for i, slope in enumerate(slopes):
        if slope < threshold:
            best_transform = i
            t_decorrelation = block_sizes[i]*time_step
            estimate_var = variances[i]
            break
    
    if visualize:
        sns.set_style("darkgrid")  # or try "darkgrid", "white", "ticks"
        sns.set_context("talk")  # or "paper", "notebook", "poster" for varying sizes and scaling
        fig, ax = plt.subplots(figsize=(8, 6))  # Adjust figsize for your needs
        # Plot using the axis object
        ax.errorbar(
            np.arange(n_transforms), variances, yerr=errors, 
            fmt='o', capsize=5, 
            markeredgecolor='darkblue', markerfacecolor='lightblue', 
            alpha=0.7, markersize=8, 
            elinewidth=1, ecolor='darkblue', 
            label='Variance with error'
        )        
        # Color point that was calculated to be the decorrelation time
        ax.scatter(best_transform, estimate_var, color='black', marker='+', s=250, zorder=1e3,label='Best block transform')
        ax.set_xlabel('N block transforms')
        ax.set_ylabel('Variance')
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.legend()
        plt.show()


    return best_transform, t_decorrelation, estimate_var