import dash
import dash_cytoscape as cyto
from dash import html
from dash import html, Input, Output, State, dcc
import copy
from typing import List, Dict, Union
import numpy as np
from collections import namedtuple
from functools import partial
from compMetabolomics.spectrum import Spectrum, generate_single_spectrum_plot, generate_n_spectrum_plots, generate_mirror_plot

STYLESHEET = [ # beware of the edge highlight creator styling!
    {
        'selector': 'node',
        'style': {
            'content': 'data(label)',
            'opacity': 0.6,
            'color' : 'orange',
            'visibility': 'visible',
            'background-color': 'gray',
            'border-width': '1px', 
            'border-color': 'black',
            "width": "mapData(size, 0, 100, 20, 60)",
            "height": "mapData(size, 0, 100, 20, 60)",
        }
    },
    {
        'selector': 'edge',
        'style': {
            'label': 'data(label)',  # Show edge labels
            'font-size': '12px',  # Custo mize font size
            'text-opacity': 0.6,
            'line-color': 'magenta',  # Highlighted edge color
            'width': 'mapData(weight,0,1,1,10)',
            'opacity': 'mapData(weight,0,1,0.2,0.8)',  # Highlighted edge opacity
        }
    },
    {
        'selector': 'node:selected',
        'style': {
            'visibility': 'visible',
            'background-opacity': 0.8,
            'background-color': 'magenta',
        }
    }
]

def create_group_highlight_entry(selected_group : Union[str, int]):
    entry = {
            'selector': f'.{selected_group}',
            'style': {
                'color': 'magenta',
                'background-color' : 'magenta',
                'opacity': 0.8,  # Highlighted edge opacity
            }
        }
    return entry

def generate_edge_dict(edge_list: List[Dict]) -> Dict:
    """ 
    edges:
        [{'data': {'source': <source node>, 'target': <target node>}}, ...]
    """
    edge_dict = {
        "formatted_edges" : np.array(edge_list), 
        "sources" : np.array([elem["data"]["source"] for elem in edge_list], dtype = np.str_),
        "targets" : np.array([elem["data"]["target"] for elem in edge_list], dtype = np.str_)
    }
    return edge_dict


def update_edges(
        selected_node_data : Union[None, List[Dict]], 
        init_elements : List[Dict], 
        top_k : int, 
        edge_dict : Dict
        ):
        """ Add edges for node selection (topk). Assumes complete edgelist in descending weight order. """
        # Note that edge dict cannot be passed as a dcc.Store : the latter are json serialized, turning numpy arrays
        # into lists, hence breaking the code below!
        if selected_node_data:            
            node_ids = [node["id"] for node in selected_node_data]
            # for each node, get the top-k edges that belong to it
            selected_edge_arrays = []
            for node_id in node_ids:
                node_id = np.array([node_id], dtype = np.str_)
                mask = np.where(
                    np.logical_or(
                        edge_dict["sources"] == node_id, 
                        edge_dict["targets"] == node_id
                    ), 
                    True, False
                    )
                selected_edge_arrays.append(edge_dict["formatted_edges"][mask][0:top_k]) 
            selected_edges = np.concatenate(selected_edge_arrays).tolist()
            _, indices = np.unique([], return_index=True) # <-- continue here, add id array to get index
            #selected_edges_unique = [dict(s) for s in set(frozenset(entry_dict.items()) for entry_dict in selected_edges)]
            return init_elements + selected_edges
        else:
            return init_elements

def run_network_visualization(node_data : List[Dict], edge_data : List[Dict], max_k : int, spectra : List[Spectrum]):
    """ 
    Function runs dash_cytoscape based network visualization using provided network data. 
    
    params: node_data and edge_data lists with the following entry types:
    for nodes:
        [{'data': {'id': <id of the node>, 'label': <label for the node>}}, ...]
    for edges:
        [{'data': {'source': <source node>, 'target': <target node>}}, ...]

      max_k : integer indicating the maximum number of edges supported by the slider.
    returns: app in run state.
    """
    # named tuple Spectrum is not json serializable, and hence can't be used in dccStore
    # It is defined here as a "global" variable within the scope of the run_network_visualization function for 
    # accessibility within the update_spectrum_plots callback
    _SPECTRA = copy.deepcopy(spectra) 

    edge_dict = generate_edge_dict(edge_data)
    explainer_text = (
        "--> Hover over a node to highlight it's k-medoid cluster.\n"
        "--> Click on a node to see node information details, super-impose edges, and plot it's spectrum (below the main view).\n"
        "--> Select multiple nodes via holding shift, ctrl, or cmd & selecting. This adds more edges, more spectrum plots, and more node information pieces.\n"
        "--> Click on an empty space to de-select nodes.\n"
        "--> Use the slider to adjust the number of edges shown for a clicked node (requires deselect and click to work).\n"
    )
    # Initialize the app
    app = dash.Dash(__name__)
    # Define the layout
    app.layout = html.Div([
            html.Details([
                html.Summary('Interactive network visualization making use of a pre-computed t-SNE layout (expand for user manual).'),
                html.Div([
                    html.Div(id='explainer_text', style={'whiteSpace': 'pre-wrap'}, children=explainer_text),
                ])
            ]),
            cyto.Cytoscape(
                id='cytoscape',
                elements = node_data,
                stylesheet = STYLESHEET,
                style={'width': '1200px', 'height': '700px'},
                boxSelectionEnabled=True,
                zoom = 1,
                layout = {
                    'name' : 'preset', "fit": False,
                }
            ),
            dcc.Slider(min=1, max=max_k, step=1, value=5, id='top_k_slider'),
            html.Div(id='selected-node-ids', style={'whiteSpace': 'pre-wrap'}),
            html.Div(id='hover-group-text'),
            html.Div(id='spectrum-plots'),
            dcc.Store(id='default_stylesheet', data= copy.deepcopy(STYLESHEET)),
            dcc.Store(id='edge_dict', data=copy.deepcopy(edge_dict)),
            dcc.Store(id='init_elemenents', data=copy.deepcopy(node_data)),
        ]
    )

    @app.callback(
        Output('selected-node-ids', 'children'),
        Input('cytoscape', 'selectedNodeData'),
        State('selected-node-ids', 'children'),
    )
    def update_selected_node_ids(selected_nodes, _):
        if selected_nodes:
            # Extract the node IDs from the selected nodes
            selected_data = [f"{str(node)}\n"  for node in selected_nodes]
            # Append the new selection to the existing text
            updated_text = f"Data for selected Nodes: \n  {'  '.join(selected_data)}"
            return updated_text
        else:
            return "No nodes selected"
    
    @app.callback(
        Output('spectrum-plots', 'children'),
        Input('cytoscape', 'selectedNodeData')
    )
    def update_spectrum_plots(selectedNodeData):
        print("Reached Callback intro")
        max_n_spectra = 10
        if selectedNodeData:
            # ETL limiting to 5 spectra at most
            node_ids = [node['id'] for node in selectedNodeData]
            plot_spectra = [spec for spec in _SPECTRA if spec.feature_id in node_ids[0:min(max_n_spectra, len(selectedNodeData))]]
            if len(node_ids) == 1:
                figure = generate_single_spectrum_plot(plot_spectra[0])
                graph_object = dcc.Graph(id=f"specplot{1}", figure=figure)
                return graph_object
            elif len(node_ids) == 2:
                figure = generate_mirror_plot(plot_spectra[0], plot_spectra[1])
                graph_object = dcc.Graph(id=f"specplot{1}", figure=figure)
                return graph_object
            elif (len(node_ids) > 2) and (len(node_ids) <= max_n_spectra):
                figures = generate_n_spectrum_plots(plot_spectra)
                graph_object = [dcc.Graph(id=f"specplot{iloc}", figure=fig) for iloc, fig in enumerate(figures)]
                return graph_object
            else:
                return f"Select Node(s) to show spectra (up to {max_n_spectra})"
        else:
            return f"Select Node(s) to show spectra (up to {max_n_spectra})"
    
    update_edges_local = partial(update_edges, edge_dict = edge_dict)
    @app.callback(
        Output('cytoscape', 'elements'),
        Output('cytoscape', 'zoom'),
        Input('cytoscape', 'selectedNodeData'),
        State('init_elemenents', 'data'),
        State('top_k_slider', 'value'),
        State('cytoscape', 'zoom'),
    )
    def addEdgesToElements(selectedNodeData, init_elements, top_k, zoom):
        return update_edges_local(selectedNodeData, init_elements, top_k), zoom
    
    @app.callback(
        Output('cytoscape', 'stylesheet'),
        Output('hover-group-text', 'children'),
        Input('cytoscape', 'mouseoverNodeData'),
        State('default_stylesheet', 'data'),
    )
    def provideNodeGroupHighlight(mouseoverNodeData, default_stylesheet):
        if mouseoverNodeData:
            highlight_group = create_group_highlight_entry(mouseoverNodeData["group"])
            hover_group_text = f"The hover highlighted group is: {mouseoverNodeData['group']}"
            return default_stylesheet + [highlight_group], hover_group_text
        else:
          return default_stylesheet, ""
    return app