import numpy as np
from typing import List, Dict
import pandas as pd
from compMetabolomics.spectrum import Spectrum

def generate_edge_list(similarity_array : np.ndarray, feature_ids : List[str], top_k : int = 50) -> List[Dict]:
  """ 
  Constructs edge list using feature_id source and target. 
  
  Assumes feature_ids to follow order used in similarity_array 
  """
  assert top_k + 1 <= similarity_array.shape[0], "Error: topK exceeds number of possible neighbors!"
  top_k = top_k + 1 # to accommodate self being among top-k; removed downstream.
  edge_list = []

  # Get top-k neighbor index array; for each row, the top K neighbors are are extracted
  top_k_indices_sorted = np.argsort(similarity_array, axis=1)[:, ::-1][:, :top_k]

  # Using the top-k neighbours, construct the edge list (prevent duplicate edge entries using set comparison)
  node_pairs_covered = set()
  
  # Create edge list
  for row_index, column_indices in enumerate(top_k_indices_sorted):
    feature_id = feature_ids[row_index]
    for column_index in column_indices:
      neighbor_id = feature_ids[column_index]
      if frozenset([feature_id, neighbor_id]) not in node_pairs_covered and feature_id is not neighbor_id:
        node_pairs_covered.add(frozenset([feature_id, neighbor_id]))
        score = similarity_array[row_index, column_index]
        edge = {"data": {
          "source": str(feature_id), 
          "target": str(neighbor_id), 
          "weight": score, 
          "label" : str(round(score, 2)),
          "id": f"{str(feature_id)}-to-{str(neighbor_id)}"
          }
        }
        edge_list.append(edge)
  return edge_list



def generate_cytoscape_node_entry(
    feature_id : str, 
    x_coordinate : float, 
    y_coordinate : float, 
    node_size : float, 
    log2ratio: float,
    effect_direction : str,
    group_id : int, 
    precursor_mz : float,
    coordinate_scaler : int = 1000 
    ) -> dict:
  """ Generates a single cytoscape node entry in required format. """
  output = {
    'data' : {
      'id': str(feature_id),
      'precursor_mz': precursor_mz,
      'label': str(feature_id) + "; " + str(round(precursor_mz, 6)), 
      'size' : node_size,
      'log2ratio' : str(log2ratio),
      'effect_direction' : effect_direction,
      'group': "group_" + str(group_id)
    },
    'position' : {'x' : x_coordinate * coordinate_scaler, 'y': y_coordinate * coordinate_scaler},
    'classes' : "group_" + str(group_id)
  }
  return output

def generate_node_list(
    spectra : List[Spectrum], 
    coordinates_table : pd.DataFrame, 
    group_ids : List[int],
    summary_statistics_df : pd.DataFrame,
    coordinate_scaler : int = 100,
    ) -> List[dict]:
  node_list = []
  for iloc, spectrum in enumerate(spectra):
    node_list.append(
      generate_cytoscape_node_entry(
        spectrum.feature_id, 
        coordinates_table.iloc[iloc]["x_coordinate"], 
        coordinates_table.iloc[iloc]["y_coordinate"], 
        summary_statistics_df.at[iloc, "node_size"], 
        summary_statistics_df.at[iloc, "log2ratio"], 
        summary_statistics_df.at[iloc, "effect_direction"], 
        group_ids[iloc], 
        spectrum.precursor_mz,
        coordinate_scaler
      )
    )
  return node_list

def generate_node_list_no_stats(
    spectra : List[Spectrum], 
    coordinates_table : pd.DataFrame, 
    group_ids : List[int],
    coordinate_scaler : int = 100,
    ) -> List[dict]:
  node_list = []
  for iloc, spectrum in enumerate(spectra):
    node_list.append(
      generate_cytoscape_node_entry(
        spectrum.feature_id, 
        coordinates_table.iloc[iloc]["x_coordinate"], 
        coordinates_table.iloc[iloc]["y_coordinate"], 
        25, 
        "none", 
        "none", 
        group_ids[iloc], 
        spectrum.precursor_mz,
        coordinate_scaler
      )
    )
  return node_list