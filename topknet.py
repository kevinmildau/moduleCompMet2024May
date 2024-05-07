import dash
import dash_cytoscape as cyto
from dash import html
from dash import html, Input, Output, State, dcc
import copy
from typing import List, Dict, Union
import numpy as np
from collections import namedtuple
from functools import partial

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
            'font-size': '12px',  # Customize font size
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

def create_edge_highlight_entry(selected_node_id : Union[str, int]):
    entry = {
            'selector': f'edge[source="{selected_node_id}"], edge[target="{selected_node_id}"]',
            'style': {
                'line-color': 'magenta',  # Highlighted edge color
                'width': 'mapData(weight,0,1,1,10)',
                'opacity': 'mapData(weight,0,1,0.2,0.8)',  # Highlighted edge opacity
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

def run_network_visualization(node_data : List[Dict], edge_data : List[Dict], max_k : int):
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

    edge_dict = generate_edge_dict(edge_data)

    # Initialize the app
    app = dash.Dash(__name__)
    # Define the layout
    app.layout = html.Div([
            cyto.Cytoscape(
                id='cytoscape',
                elements = node_data,
                stylesheet = STYLESHEET,
                style={'width': '1200px', 'height': '800px'},
                boxSelectionEnabled=True,
                zoom = 1,
                layout = {
                    'name' : 'preset', "fit": False,
                }
            ),
            html.Div(id='selected-node-ids'),
            dcc.Store(id='default_stylesheet', data= copy.deepcopy(STYLESHEET)),
            dcc.Store(id='edge_dict', data=copy.deepcopy(edge_dict)),
            dcc.Store(id='init_elemenents', data=copy.deepcopy(node_data)),
            dcc.Slider(min=1, max=max_k, step=1, value=5, id='top_k_slider')
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
            selected_ids = [f"Feature {node['id']}"  for node in selected_nodes]
            # Append the new selection to the existing text
            updated_text = f"Selected Node IDs: {', '.join(selected_ids)}"
            return updated_text
        else:
            return "No nodes selected"
    
    update_edges_local = partial(update_edges, edge_dict = edge_dict)
    @app.callback(
        Output('cytoscape', 'elements'),
        Output('cytoscape', 'zoom'),
        Input('cytoscape', 'selectedNodeData'),
        State('init_elemenents', 'data'),
        State('top_k_slider', 'value'),
        State('cytoscape', 'zoom'),
    )
    def callback(selectedNodeData, init_elements, top_k, zoom):
        print (zoom)
        return update_edges_local(selectedNodeData, init_elements, top_k), zoom

    app.run_server(debug=True)
    return app