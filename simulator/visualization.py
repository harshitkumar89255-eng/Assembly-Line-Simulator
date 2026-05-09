import matplotlib.pyplot as plt
import networkx as nx
from simulator.config import load_config, get_recipe_map
import plotly.graph_objects as go

def map_stations(config):
    stat_inp_out ={}
    for station in config["stations"]:
        stat_inp_out[station["id"]] = {"input_station": [], "output_station": []}
    

    for conn in config["connections"]:
        stat_inp_out[conn["to_station"]]["input_station"].append(conn["from_station"])
        stat_inp_out[conn["from_station"]]["output_station"].append(conn["to_station"])
    return stat_inp_out
        
def find_layer(config):
    station_map = map_stations(config)
    layers = {}
    for station in station_map:
        calculate_layer(station,station_map,layers)
    return layers
            
def calculate_layer(station,station_map,layers):
    if station in layers:
        return layers[station]
    inputs = station_map[station]["input_station"]
    if not inputs:
        layers[station] = 0
        return 0
    
    layer = max([calculate_layer(inpt,station_map,layers) for inpt in inputs]) + 1
    layers[station] = layer
    return layer 

def generate_positions(layer_map,layer_spacing=4,vertical_spacing=2):
    grouped_by_layer = {}
    for station, layer in layer_map.items():
        if layer not in grouped_by_layer:
            grouped_by_layer[layer] = []
        grouped_by_layer[layer].append(station)
    positions = {}
    for layer, stations in grouped_by_layer.items():
        total = len(stations)
        for i, station in enumerate(stations):
            x = layer * layer_spacing
            y = -(i-(total-1)/2) * vertical_spacing
            positions[station] = (x, y)
    return positions

def generate_graph(config):
    layer = find_layer(config)
    G = nx.DiGraph()
    for conn in config["connections"]:
        G.add_edge(conn["from_station"], conn["to_station"], item=conn["item_id"], capacity=conn["buffer_capacity"])
    pos = generate_positions(layer)
    edge_x = []
    edge_y = []
    edge_text = []


    for source, target, in G.edges():
        x0, y0 = pos[source]
        x1, y1 = pos[target]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter( x=edge_x, y=edge_y, mode="lines", line=dict(width=2), hovertext=edge_text, hoverinfo="text")

    node_x = []
    node_y = []
    node_text = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

    node_trace = go.Scatter(x=node_x, y=node_y, mode="markers+text", text=node_text, textposition="top center", marker=dict(symbol="square", size=35,line=dict(width=2,color="black")), hoverinfo="text")

    fig = go.Figure(
        data=[
            edge_trace,
            node_trace,
        ]
    )

    fig.update_layout(showlegend=False, xaxis=dict(visible=False), yaxis=dict(visible=False), height=700)
    return fig

