import json
from collections import namedtuple
import numpy as np
from typing import List, Tuple, Union
import plotly.graph_objects as go

PLOT_LAYOUT_SETTINGS = {
    'template':"simple_white",
    'xaxis':dict(title="Mass to charge ratio"),
    'yaxis':dict(title="Intensity", fixedrange=True),
    'hovermode':"x",
    'showlegend':False
}

class Spectrum(namedtuple('Spectrum', 'feature_id precursor_mz retention_time fragment_intensities fragment_mass_to_charge_ratios')):
  """ 
  A spectrum entry (tuple) with the following entries:
    feature_id : str identifer for spectrum
    precursor_mz : float
    retention_time : retention time (assumed in seconds, unit not validated)
    fragment_intensities : fragment intensity array (np.array), assumed between [0 and 1]
    fragment_mass_to_charge_ratios : fragment mz array (np.array)
  """
  feature_id: str 
  precursor_mz: float
  retention_time : float
  fragment_intensities : np.ndarray 
  fragment_mass_to_charge_ratios : np.ndarray
  __slots__ = ()

def get_spectrum_ids(spectra : List[Spectrum]) -> List[str]:
    ids = [spectrum.feature_id for spectrum in spectra]
    return ids

def parse_json_spectrum(json_spectrum : dict) -> Spectrum:
    """ 
    Converts a spectrum of type dictionary as produced by matchms and converts it to Spectrum tuple. 
    
    Assumes:
      1. a feature_id column to be available
      2. no empty spectra
      3. all lowercase and standardized matchms entry names
    """
    spectrum = Spectrum(
        json_spectrum["feature_id"], 
        json_spectrum["precursor_mz"],
        json_spectrum["retention_time"], 
        np.array(json_spectrum["peaks_json"])[:,1],
        np.array(json_spectrum["peaks_json"])[:,0]
    ) 
    return spectrum

def load_json_spectra(filepath : str) -> List[Spectrum]:
  """ Loads matchms json export file into list of Spectrum tuples. """
  with open(filepath) as f:
    json_spectra = json.load(f)
  spectra = [ parse_json_spectrum(spectrum) for spectrum in json_spectra]
  return spectra

def get_min_max(spectra_list: List[Spectrum]) -> Tuple[float, float]:
  """ 
  Computes min and max mz from a list of Spectrum tuples. 
  
  When providing a single spectrum, it must be packaged into a list as well.
  """
  max = -9999
  min = 9999 
  for spectrum in spectra_list:
    tmp_min = np.min(spectrum.fragment_mass_to_charge_ratios)
    tmp_max = np.max(spectrum.fragment_mass_to_charge_ratios)
    if tmp_min < min:
      min = tmp_min
    if tmp_max > max:
      max = tmp_max
  return (min, max)

def generate_n_spectrum_plots(spectra : List[Spectrum]) -> List[go.Figure]:
    """ 
    Generate list of single spectrum plots, each of which embedded into a separate dcc.Graph containers.
    
    Parameters:
    -----------
    spectra : List[Spectrum]
        List of specxplore.data.Spectrum objects
    
    Returns:
    --------
        List of dcc.Graph objects; one spectrum plot per spectrum provided.
    """
    min_x, max_x = get_min_max(spectra) 
    figure_list = []
    for spectrum in spectra:
        spectrum_figure = generate_single_spectrum_plot(spectrum, min_x, max_x)
        figure_list.append(spectrum_figure)
    return figure_list

def generate_mirror_plot(top_spectrum : Spectrum, bottom_spectrum: Spectrum) -> go.Figure:
    """ Generates spectrum mirrorplot. """
    min_x, max_x = get_min_max([top_spectrum, bottom_spectrum]) 
    range_margin = 25
    xticks = np.round(np.linspace(min_x - range_margin, max_x + range_margin, num=10, endpoint=True))
    top_hover_trace_invisible = generate_bar_hover_trace(
        top_spectrum.fragment_mass_to_charge_ratios, 
        top_spectrum.fragment_intensities, 
        top_spectrum.feature_id
    )
    bottom_hover_trace_invisible = generate_bar_hover_trace(
        bottom_spectrum.fragment_mass_to_charge_ratios, 
        bottom_spectrum.fragment_intensities * -1.0, 
        bottom_spectrum.feature_id
    )
    top_visible_trace = generate_bar_line_trace(
        top_spectrum.fragment_mass_to_charge_ratios, 
        top_spectrum.fragment_intensities
    )
    bottom_visible_trace = generate_bar_line_trace(
        bottom_spectrum.fragment_mass_to_charge_ratios, 
        bottom_spectrum.fragment_intensities * -1.0
    )
    data = [top_hover_trace_invisible, bottom_hover_trace_invisible] + top_visible_trace + bottom_visible_trace

    figure = go.Figure(data = data)
    figure.update_yaxes(range=[-1, 1])
    figure.add_hline(y=0.0, line_width=1, line_color="black", opacity=1)
    figure.update_layout(
        title = {
            'text': f"Spectrum {top_spectrum.feature_id} vs Spectrum {bottom_spectrum.feature_id}"
        },
        **PLOT_LAYOUT_SETTINGS
    )
    figure.update_xaxes(range = [min_x - range_margin, max_x + range_margin], tickvals= xticks.tolist())
    return figure

def generate_single_spectrum_plot(
      spectrum : Spectrum, 
      min_x : Union[float, None] = None, 
      max_x : Union[float, None] = None
      ) -> go.Figure:
    """ Generates single spectrum plot. """
    # Handle min max setting
    if max_x is None and min_x is None:
        tmp_min, tmp_max = get_min_max([spectrum])
    if max_x is None:
       max_x = tmp_max
    if min_x is None: 
       min_x = tmp_min
    
    range_margin = 25
    xticks = np.round(np.linspace(min_x - range_margin, max_x + range_margin, num=10, endpoint=True))
    
    hover_trace_invisible = generate_bar_hover_trace(
        spectrum.fragment_mass_to_charge_ratios, 
        spectrum.fragment_intensities, 
        spectrum.feature_id
    )
    visual_trace = generate_bar_line_trace(
        spectrum.fragment_mass_to_charge_ratios, 
        spectrum.fragment_intensities
    )
    figure = go.Figure(
        data = [hover_trace_invisible] + visual_trace
    )
    figure.update_yaxes(range=[0, 1])
    figure.update_xaxes(range=[min_x - range_margin, max_x + range_margin], tickvals= xticks.tolist())
    figure.update_layout(
        title = {'text': f"Spectrum {spectrum.feature_id}"}, 
        **PLOT_LAYOUT_SETTINGS
    )
    return figure


def generate_bar_line_trace(x_values: np.ndarray, y_values: np.ndarray) -> List[go.Scatter]:
    """ Generates bar lines for arrays containing x and y values. """

    kwargs = {
        'mode': 'lines', 
        'opacity': 1, 
        'hoverinfo': "skip", 
        'name' : '', 
        'showlegend':False
    }
    lines_scatters = [
        go.Scatter(x = [x,x], y =  [0,y], meta=np.abs(y), marker={'color': "black"}, **kwargs) 
        for x, y 
        in zip(x_values, y_values)
    ]
    return lines_scatters


def generate_bar_hover_trace(x_values: np.ndarray, y_values: np.ndarray, feature_id : int) -> go.Scatter:
    """ Generates the hover trace information for each x, y value pair. """
    kwargs = {
        'mode': 'markers', 
        'opacity': 0, 
        'hovertemplate': "%{meta:.4f}<extra></extra>", 
        'name' : f'Spectrum ID = {feature_id}'
    }
    output_figure = go.Scatter(
        x=x_values, 
        y=y_values, 
        meta= np.abs(y_values),
        marker={'color': "black"}, 
        **kwargs
    )
    return output_figure