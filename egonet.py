import dash
import dash_cytoscape as cyto
import dash_html_components as html
from dash import html, Input, Output, State, dcc
import copy
from typing import List, Dict, Union

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
            'width' : 0.1,
            'line-color': 'gray',
            'text-opacity': 0.4,
            'opacity' : 0.1,


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

def run_network_visualization(network_data : Dict):
    """ Function runs dash_cytoscape based network visualization using provided network data. 
    
    params: network_data A dictionary with 'nodes' and 'edges', each containing cytoscape compatible lists
    of data entries: 
    for nodes:
        [{'data': {'id': <id of the node>, 'label': <label for the node>}}, ...]
    for edges:
        [{'data': {'source': <source node>, 'target': <target node>}}, ...]

    returns: app in run state.
    """
    ...
    # Initialize the app
    app = dash.Dash(__name__)
    # Define the layout
    app.layout = html.Div([
            cyto.Cytoscape(
                id='cytoscape',
                elements = network_data,
                stylesheet = STYLESHEET,
                style={'width': '1200px', 'height': '800px'},
                boxSelectionEnabled=True,
                layout = {
                    'name' : 'cose'
                }
            ),
            html.Div(id='selected-node-ids'),
            dcc.Store(id='default_stylesheet', data= copy.deepcopy(STYLESHEET))
        ]
    )
    @app.callback(
        Output('selected-node-ids', 'children'),
        Input('cytoscape', 'selectedNodeData'),
        State('selected-node-ids', 'children')
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
        
    @app.callback(
        Output('cytoscape', 'stylesheet'),
        Input('cytoscape', 'selectedNodeData'),
        State('default_stylesheet', 'data')
    )
    def update_edge_styles(selected_node_data : Union[None, List[Dict]], init_stylesheet : List[Dict]):
        if selected_node_data:
            updated_stylesheet = copy.deepcopy(init_stylesheet) # avoid stylesheet corruption by explicit copy
            node_ids = [node["id"] for node in selected_node_data]
            style_entries = list(map(create_edge_highlight_entry, node_ids))
            updated_stylesheet = updated_stylesheet + style_entries
            return updated_stylesheet
        else:
            return init_stylesheet
    app.run_server(debug=True)
    return app