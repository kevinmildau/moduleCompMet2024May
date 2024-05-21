import numpy as np
def convert_similarity_to_distance(similarity_matrix : np.ndarray) -> np.ndarray:
  """ 
  Converts pairwise similarity matrix to distance matrix with values between 0 and 1. Assumes that the input is a
  similarity matrix with values in range 0 to 1 up to floating point error.
  """
  distance_matrix = 1.- similarity_matrix
  distance_matrix = np.round(distance_matrix, 6) # Round to deal with floating point issues
  distance_matrix = np.clip(distance_matrix, a_min = 0, a_max = 1) # Clip to deal with floating point issues
  return distance_matrix