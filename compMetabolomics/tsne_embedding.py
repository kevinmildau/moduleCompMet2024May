from dataclasses import dataclass
from typing import List, Union
import numpy as np
import pandas as pd
from sklearn.manifold import TSNE
from scipy.spatial.distance import pdist, squareform
from scipy.stats import spearmanr, pearsonr
import plotly
import plotly.graph_objects as go

@dataclass
class GridEntryTsne:
  """ 
  Container Class for t-SNE embedding optimization results. Contains a single entry. A list of these containers can be 
  converted to pandas for easy display.

  Parameters:
    perplexity : int with perplexity value used in t-SNE optimization.
    x_coordinates : List[int] x coordinates produced by t-SNE
    y_coordinates:  List[int] y coordinates produced by t-SNE
    pearson_score : float representing the pearson correlation between pairwise distances in embedding and 
      high dimensional space.
    spearman_score : float representing the spearman correlation between pairwise distances in embedding and 
      high dimensional space.
    random_seed_used : int or float with the random seed used in k-medoid clustering.
  """
  perplexity : int
  x_coordinates : List[int]
  y_coordinates:  List[int]
  pearson_score : float
  spearman_score : float
  random_seed_used : Union[int, float]
  def __str__(self) -> str:
    custom_print = (
      f"Perplexity = {self.perplexity}," 
      f"Pearson Score = {self.pearson_score}, "
      f"Spearman Score = {self.spearman_score}, \n"
      f"x coordinates = {', '.join(self.x_coordinates[0:4])}...",
      f"y coordinates = {', '.join(self.y_coordinates[0:4])}...")
    return custom_print

def extract_coordinates_from_entry(tsne_grid_entry : GridEntryTsne) -> pd.DataFrame:
  """ 
  Function returns data frame with x and y coordinates for each feature based on GridEntryTsne object. 

  Dev note: Feature ordering of rows follows that of the similarity matrix used to compute the tsne grid entry.
  """
  assert isinstance(tsne_grid_entry, GridEntryTsne), (
    f"Error: Expected signle tsne grid entry object but received {type(tsne_grid_entry)}"
  )
  output = pd.DataFrame({'x_coordinate': tsne_grid_entry.x_coordinates, 'y_coordinate': tsne_grid_entry.y_coordinates})
  return output

def check_perplexities(perplexity_values : List[Union[float, int]], max_perplexity : Union[float, int]) -> None:
  """ Function checks whether perplexity values match expected configuration. Aborts if not. """
  assert perplexity_values is not [], (
    "Error: perplexity_values list is empty! This may be a result of post-processing: there must be a "
    "perplexity value below the number of spectra for optimization to work."
  )
  assert isinstance(perplexity_values, list), (
    "Error: perplexity values must be a list. If only running one value, specify input as [value]."
  )
  for perplexity_value in perplexity_values: 
    assert isinstance(perplexity_value, (int, float)) and perplexity_value < max_perplexity, (
      "Error: perplexity values must be numeric (int, float) and smaller than number of features." 
    )
  return None

def run_tsne_grid(
  distance_matrix : np.ndarray,
  perplexity_values : List[int], 
  random_states : Union[List, None] = None
  ) -> List[GridEntryTsne]:
  """ Runs t-SNE embedding routine for every provided perplexity value in perplexity_values list.

  Parameters:
      distance_matrix: An np.ndarray containing pairwise distances.
      perplexity_values: A list of perplexity values to try for t-SNE embedding.
      random_states: None or a list of integers specifying the random state to use for each k-medoid run.
  Returns: 
      A list of GridEntryTsne objects containing grid results. 
  """
  check_perplexities(perplexity_values, distance_matrix.shape[0])
  if random_states is None:
      random_states = [ 0 for _ in perplexity_values ]
  output_list = []
  for idx, perplexity in enumerate(perplexity_values):
    model = TSNE(
      metric="precomputed", 
      random_state = random_states[idx], 
      init = "random", 
      perplexity = perplexity
    )
    z = model.fit_transform(distance_matrix)
    # Compute embedding quality
    dist_tsne = squareform(pdist(z, 'seuclidean'))
    spearman_score = np.array(spearmanr(distance_matrix.flat, dist_tsne.flat))[0]
    pearson_score = np.array(pearsonr(distance_matrix.flat, dist_tsne.flat))[0]
    output_list.append(
      GridEntryTsne(
        perplexity, 
        z[:,0], 
        z[:,1], 
        pearson_score, 
        spearman_score, 
        random_states[idx]
      )
    )
  return output_list

def plot_tsne_grid(tsne_list : List[GridEntryTsne]) -> None:
  """ Plots pearson and spearman scores vs perplexity for each entry in list of GridEntryTsne objects. """
  
  spearman_scores = [x.spearman_score for x in tsne_list]
  pearson_scores  = [x.pearson_score for x in tsne_list]
  iloc_perplexity = [ f"{x.perplexity} / {iloc}" for iloc, x in enumerate(tsne_list)]

  trace_spearman = go.Scatter(x = iloc_perplexity, y = spearman_scores, name="spearman_score", mode = "markers")
  trace_pearson = go.Scatter(x = iloc_perplexity, y = pearson_scores, name="pearson_score", mode = "markers")
  fig = go.Figure([trace_pearson, trace_spearman])
  fig.update_layout(xaxis_title="Perplexity / iloc", yaxis_title="Score")
  fig.show()
  return None

def print_tsne_grid(grid : List[GridEntryTsne]) -> None:   
  """ Prints all values in tsne grid in readable format via pandas conversion """
  tsne_results = pd.DataFrame.from_dict(data = grid).loc[
      :, ["perplexity", "pearson_score", "spearman_score", "random_seed_used"]
  ]
  tsne_results.insert(loc = 0, column = "iloc", value = [iloc for iloc in range(0, len(grid))])
  print("T-sne grid results. Use to inform t-sne embedding selection.")
  print(tsne_results)
  return None

def plot_embedding(embedding_coordinates_table : pd.DataFrame, feature_ids : List[str]) -> plotly.graph_objs.Figure:
  """ 
  Plots the provided t-sne embedding.
  
  Input
    embedding_coordinates_table : pd.DataFrame with assumed "x" and "y" coordinate entries and a "feature_id"
    column entry.
  """
  embedding_coordinates_table["feature_id"] = feature_ids
  figure  = plotly.express.scatter(
    data_frame= embedding_coordinates_table, x = "x_coordinate", y = "y_coordinate", hover_data=["feature_id"],
    width=800, height=800, title = "t-SNE Embedding Scatter Plot"
  )
  return(figure)


