from math import isnan
import numpy as np
import json
import pandas as pd
import copy
from warnings import warn

def force_to_numeric(value, replacement_value):
  """ 
  Helper function to force special R output to valid numeric forms for json export. 
  
  Checks whether input is numeric or can be coerced to numeric, replaces it with provided default if not.

  Covered are: 
    string input, 
    empty string input, 
    None input, 
    "-inf", "-INF" and positive equivalents that are translated into infinite but valid floats.
  """
  if value is None: # catch None, since None breaks the try except in float(value)
    return replacement_value
  try:
    # Try to convert the value to a float
    num = float(value)
    # Check if the number is infinite or NaN
    if isnan(num):  # num != num is a check for NaN
      return replacement_value
    else:
      return num
  except ValueError:
    # return replacement_value if conversion did not work
    return replacement_value
  
def linear_range_transform(
    input_scalar : float, 
    original_lower_bound : float, 
    original_upper_bound : float, 
    new_lower_bound : float, 
    new_upper_bound : float
  ) -> float:
  """ Returns a linear transformation of a value in one range to another. 
  
  Use to scale statistical values into appropriate size ranges for visualization.
  """
  assert original_lower_bound < original_upper_bound, "Error: lower bound must be strictly smaller than upper bound."
  assert new_lower_bound < new_upper_bound, "Error: lower bound must be strictly smaller than upper bound."
  assert original_lower_bound <= input_scalar <= original_upper_bound, (
    f"Error: input must be within specified bounds but received {input_scalar}"
  )
  # Normalize x to [0, 1]
  normalized_scalar = (input_scalar - original_lower_bound) / (original_upper_bound - original_lower_bound)
  # Map the normalized value to the output range
  output_scalar = new_lower_bound + normalized_scalar * (new_upper_bound - new_lower_bound)
  return output_scalar

def transform_log2_fold_change_to_node_size(value : float) -> float:
  # transform to abs scale for positive and negative fold to be treated equally 
  # limit to range 0 to 10 (upper bounding to limit avoid a huge upper bound masking smaller effects), 
  # recast to size 10 to 50
  lb_node_size = 10
  ub_node_size = 50
  lb_original = 0
  ub_original = 13 # also max considered for visualization, equivalent of a 8192 fold increase or decrease
  round_decimals = 4
  # make sure the input is valid, and if not, replace with default lb (no size emphasis)
  value = force_to_numeric(value, lb_original)        
  size = round(
    linear_range_transform(
      np.clip(np.abs(value), lb_original, ub_original),
      lb_original, ub_original, lb_node_size, ub_node_size), 
    round_decimals
  )
  return size

def transform_similarity_score_to_width(score: float):
  """ 
  Function transforms edge similarity score in range 0 to 1 to edge widths using a discrete mapping.

  The range of scores between [0, 1] is divided into 
  0 to <0.2, 0.2 to <0.4, 0.4 to <0.6, 0.6 to <0.8, and 0.8 to < 1,
  Values below 0 are assigned width of 1. Values equal to or above 1 are assigned 26.

  """
  # multiply the score by one hundred and force to integer, take range from [0,1] to [0,100]
  # This avoids numpy floating point problems making discrete cut locations unexpected, e.g. 0.60000000000001 rather
  # than 0.6, leading to values of 0.6... being mapped to the wrong bin!
  score_int = np.int64(score * 100)
  digitized_score = np.digitize(score_int, np.linspace(20, 100, num=5, dtype= np.int64))
  mapping = dict(zip(np.arange(0, 6), [1, 6, 11, 16, 21, 26]))
  width = mapping[digitized_score]
  #if score > 1 or score < 0: 
  #  warn(f"Expected score in range [0,1] but received {score}, determined width to be {width}")
  return width