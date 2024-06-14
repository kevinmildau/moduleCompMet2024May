import matchms
from typing import List
import numpy as np
from ms2deepscore import MS2DeepScore
from ms2deepscore.models import load_model

def convert_similarity_to_distance(similarity_matrix : np.ndarray) -> np.ndarray:
  """ 
  Converts pairwise similarity matrix to distance matrix with values between 0 and 1. Assumes that the input is a
  similarity matrix with values in range 0 to 1 up to floating point error.
  """
  distance_matrix = 1.- similarity_matrix
  distance_matrix = np.round(distance_matrix, 6) # Round to deal with floating point issues
  distance_matrix = np.clip(distance_matrix, a_min = 0, a_max = 1) # Clip to deal with floating point issues
  return distance_matrix

def compute_similarities_cosine(
    spectrum_list:List[matchms.Spectrum], 
    cosine_type : str = "ModifiedCosine"
    ) -> np.ndarray:
    """ Function computes pairwise similarity matrix for list of spectra using specified cosine score. 
    
    Parameters:
        spectrum_list: List of matchms ms/ms spectra. These should be pre-processed and must incldue peaks.
        cosine_type: String identifier of supported cosine metric, options: ["ModifiedCosine", "CosineHungarian", 
        "CosineGreedy"]
    Returns:
        ndarray with shape (n, n) where n is the number of spectra (Pairwise similarity matrix).
    """
    valid_types = ["ModifiedCosine", "CosineHungarian", "CosineGreedy"]
    assert cosine_type in valid_types, f"Cosine type specification invalid. Use one of: {str(valid_types)}"
    if cosine_type == "ModifiedCosine":
        similarity_measure = matchms.similarity.ModifiedCosine()
    elif cosine_type == "CosineHungarian":
        similarity_measure = matchms.similarity.CosineHungarian()
    elif cosine_type == "CosineGreedy":
        similarity_measure = matchms.similarity.CosineGreedy()
    tmp = matchms.calculate_scores(
      spectrum_list, spectrum_list, similarity_measure, is_symmetric=True, array_type = "numpy"
    )
    scores = _extract_similarity_scores_from_matchms_cosine_array(tmp.to_array())
    scores = np.clip(scores, a_min = 0, a_max = 1) 
    return scores

def _extract_similarity_scores_from_matchms_cosine_array(
  tuple_array : np.ndarray
  ) -> np.ndarray:
  """ 
  Function extracts similarity matrix from matchms cosine scores array.
  
  The cosine score similarity output of matchms stores output in a numpy array of pair-tuples, where each tuple 
  contains (sim, n_frag_overlap). This function extracts the sim scores, and returns a numpy array corresponding to 
  pairwise similarity matrix.

  Parameters:
      tuple_array: A single matchms spectrum object.
  Returns:  
      A np.ndarray with shape (n, n) where n is the number of spectra deduced from the dimensions of the input
      array. Each element of the ndarray contains the pairwise similarity value.
  """
  sim_data = [ ]
  for row in tuple_array:
    for elem in row:
      sim_data.append(float(elem[0]))
  return(np.array(sim_data).reshape(tuple_array.shape[0], tuple_array.shape[1]))

def compute_similarities_ms2ds(
  spectrum_list:List[matchms.Spectrum], 
  model_path:str
  ) -> np.ndarray:
  """ Function computes pairwise similarity matrix for list of spectra using pretrained ms2deepscore model.
  
  Parameters
      spectrum_list: List of matchms ms/ms spectra. These should be pre-processed and must incldue peaks.
      model_path: Location of ms2deepscore pretrained model file path (filename ending in .hdf5 or file-directory)
  Returns: 
      ndarray with shape (n, n) where n is the number of spectra (Pairwise similarity matrix).
  """
  model = load_model(model_path) # Load ms2ds model
  similarity_measure = MS2DeepScore(model)
  scores_matchms = matchms.calculate_scores(
    spectrum_list, spectrum_list, similarity_measure, is_symmetric=True, array_type="numpy"
  )
  scores_ndarray = scores_matchms.to_array()
  scores_ndarray = np.clip(scores_ndarray, a_min = 0, a_max = 1) # Clip to deal with floating point issues
  return scores_ndarray