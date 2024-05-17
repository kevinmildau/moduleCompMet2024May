import numpy as np
from typing import List, Dict

def construct_edge_list_for_cytoscape(similarity_array : np.ndarray, feature_ids : List[str], top_k : int = 50) -> List[Dict]:
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