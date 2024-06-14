import plotly.graph_objects as go
from scipy.cluster import hierarchy
import numpy as np
import itertools
import plotly.express as px
from typing import List

def generate_optimal_leaf_ordering_index(similarity_matrix : np.ndarray):
    """ Function generates optimal leaf ordering index for given similarity matrix. """

    linkage_matrix = hierarchy.ward(similarity_matrix) # hierarchical clustering using ward linkage
    index = hierarchy.leaves_list(
        hierarchy.optimal_leaf_ordering(linkage_matrix, similarity_matrix)
    )
    return index

def extract_sub_matrix(idx : List[int], similarity_matrix : np.ndarray) -> np.ndarray:
    """ Extract relevant subset of spec_ids from similarity matrix. """

    out_similarity_matrix = similarity_matrix[idx, :][:, idx]
    return out_similarity_matrix

def reorder_matrix(ordered_index : List[int], similarity_matrix : np.ndarray) -> np.ndarray:
    """ Function reorders matrices according to ordered_index provided. """

    out_similarity_matrix = similarity_matrix[ordered_index,:][:,ordered_index]
    return out_similarity_matrix


def construct_redblue_diverging_coloscale(threshold):
    """ 
    Creates a non-symmetric red-blue divergin color scale in range 0 to 1, with breakpoint at the provided threshold.
    """
    
    color_range = list(np.arange(0,1,0.01))
    closest_breakpoint = min(color_range, key=lambda x: abs(x - threshold))
    n_blues = int(closest_breakpoint * 100 - 1)
    n_reds = int(100 - (closest_breakpoint * 100) + 1)
    blues = px.colors.sample_colorscale(
        "Blues_r", 
        [ n/(n_blues -1) for n in range(n_blues) ]
    )
    reds = px.colors.sample_colorscale(
        "Reds", [n/(n_reds -1) for n in range(n_reds)])
    redblue_diverging = blues + reds
    return(redblue_diverging)

def generate_heatmap_colorscale(threshold, colorblind = False):
    """ Creates colorscale for heatmap in range 0 to 1, either grayscale or diverging around threshold. """

    if colorblind:
        # 100 increments between 0 to 1
        colorscale = px.colors.sample_colorscale("greys", [n/(100 -1) for n in range(100)]) 
    else:
        colorscale = construct_redblue_diverging_coloscale(threshold)
    return(colorscale)

def generate_heatmap_trace(
        ids, 
        similarity_matrix, 
        colorscale,
        ):
    """ Returns main heatmap trace for AugMap. """
    heatmap_trace = [
        go.Heatmap(
            x=ids, 
            y=ids, 
            z = similarity_matrix, 
            type = 'heatmap',
            colorscale=colorscale, 
            zmin = 0, 
            zmax = 1, 
            xgap=1, 
            ygap=1
        )
    ]
    return heatmap_trace

def generate_augmap_graph(
        feature_ilocs : List[int],
        similarity_matrix : np.ndarray, 
        feature_ids : List[str],
        threshold : float = 0.7, 
        colorblind : bool = False,
        ):
    """ 
    Constructs augmap figure object from provided data and threshold settings. The feature ilocs are the
    integer locations (index) of the elements in the similarity matrix to use. A list of integers. Threshold is used to
    as the divergance point in the heatmap colorscale. Colorblind allows switching to grayscale.
    
    Important:
    feature_ilocs is a subselection list.
    feature_ids and the similarity matrix are complete (not subselected)
    """
    
    # Convert string input to integer iloc
    idx_iloc_list = [int(elem) for elem in feature_ilocs]
    n_elements = len(idx_iloc_list)
    
    # Extract similarity matrices for selection
    similarity_matrix = extract_sub_matrix(idx_iloc_list, similarity_matrix)
  
    # Generate optimal order index based on primary similarity matrix
    ordered_index = generate_optimal_leaf_ordering_index(similarity_matrix)

    # Reorder similarity matrices according to optimal leaf ordering
    similarity_matrix = reorder_matrix(ordered_index, similarity_matrix)

    # Reorder ids and idx according to optimal leaf ordering (computed above)
    idx_iloc_array = np.array(feature_ids)[ordered_index]
    ids_string_list  = [str(e) for e in idx_iloc_array]
    
    # Generate heathmap and joint hover trace
    colorscale = generate_heatmap_colorscale(threshold, colorblind)
    heatmap_trace = generate_heatmap_trace(
        ids_string_list, 
        similarity_matrix, 
        colorscale,
    )
    augmap_figure = go.Figure(data = heatmap_trace)
    augmap_figure.update_layout(
        yaxis_nticks=n_elements, 
        xaxis_nticks=n_elements,
        margin = {
            "autoexpand":True, 
            "b" : 20, 
            "l":20, 
            "r":20, 
            "t":20
        }, 
        title_x=0.01, 
        title_y=0.01,
        width = 1500,
        height = 1400) 
    return augmap_figure