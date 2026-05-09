import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from simulator.visualization import generate_graph
from simulator.json_validation import validate_config
from simulator.config import load_config
import os
import simulator.metrics as mt
from simulator.analysis import run_analysis, run_scenario_analysis
from simulator.scenario import Scenario
from simulator.builder import Builder

def text_replace(text):
    return str(text).replace("_", " ").title()

def load_config_options(folder="examples"):
    config_options = {}

    if not os.path.exists(folder):
        st.error(f"Folder '{folder}' not found")
        return config_options

    for file in sorted(os.listdir(folder)):
        if file.endswith(".json"):
            display_name = text_replace(file.replace(".json", ""))
            full_path = os.path.join(folder, file)
            config_options[display_name] = full_path

    return config_options


def format_value(value):
    if isinstance(value, list):
        if len(value) == 0:
            return "None"
        return ", ".join(text_replace(item) for item in value)

    if isinstance(value, dict):
        return value

    if value is None:
        return "None"

    return text_replace(value)


st.set_page_config(
    page_title="Assembly Line Bottleneck Simulator",
    layout="wide"
)

st.title("Assembly Line Bottleneck Diagnosis Simulator")


config_options = load_config_options()

selected_config_name = st.sidebar.selectbox(
    "Choose example config",
    list(config_options.keys())
)

config_path = config_options[selected_config_name]

if st.sidebar.button("Run Simulation"):
    validate_config(config_path)
    config = load_config(config_path)
    result = run_analysis(config)
    st.session_state['station_ids'] = []
    st.session_state['buffers'] = []
    st.session_state["result"] = result
    st.session_state["base_config"] = config
    st.session_state["config_name"] = selected_config_name
    st.session_state["scenario_config"] = config

    if "scenario_result" in st.session_state:
        del st.session_state["scenario_result"]

    if "scenario_changes" in st.session_state:
        del st.session_state["scenario_changes"]
    
    st.session_state['builder_mode'] = False
    
if "builder" not in st.session_state:
    st.session_state["builder"] = Builder()


st.sidebar.divider()
st.sidebar.header('Create New Config')
if st.sidebar.button("Start New Config"):
    st.session_state['builder_mode'] = True
    
if st.session_state.get('builder_mode', False):
    builder = st.session_state["builder"]
    st.header("Config Builder")

    st.subheader("Simulation")
    duration = st.number_input("Duration", min_value=1, value=300, key="duration")
    tick = st.number_input("Tick", min_value=1, value=1, key="tick")

    if st.button("Set Simulation"):
        builder.define_simulation(duration, tick)
        st.success("Simulation defined")

    st.subheader("Add Station")

    col1, col2 = st.columns(2)
    station_id = col1.text_input("Station ID", key="station_id")
    station_name = col2.text_input("Station Name", key="station_name")
    station_type = col1.text_input("Station Type", key="station_type")
    cycle_time = col2.number_input("Cycle Time", min_value=1.0, value=1.0, key="cycle_time", step=0.5)

    if st.button("Add Station"):
        builder.define_station(station_id, station_name, station_type, cycle_time)
        st.success(f"Added station {station_name}")


    st.subheader("Add Item")

    item_id = st.text_input("Item ID", key="item_id")
    item_name = st.text_input("Item Name", key="item_name")
    produced_by = st.selectbox("Produced By Station", options=builder.station_ids, key="produced_by")

    if st.button("Add Item"):
        builder.define_items(item_id, item_name, produced_by)
        st.success(f"Added item {item_name}")

    st.subheader("Add Connection")

    connection_id = st.text_input("Connection ID", key="conn_id")
    from_station = st.selectbox("From Station", options=builder.station_ids, key="from_station")
    to_station = st.selectbox("To Station", options=builder.station_ids, key="to_station")
    item_id_conn = st.selectbox("Item in Connection", options=builder.items, key="item_id_conn")
    buffer_capacity = st.number_input("Buffer Capacity", min_value=0, value=10, key="buffer_capacity")

    if st.button("Add Connection"):
        builder.define_connections(connection_id, from_station, to_station, item_id_conn, buffer_capacity)
        st.success("Connection added")

    st.subheader("Recipes")

    item_ids = [i["id"] for i in builder.data["items"]]
    station_ids = [s["id"] for s in builder.data["stations"]]

    if not station_ids:
        st.warning("Add at least one station before defining recipes.")
    elif not item_ids:
        st.warning("Add at least one item before defining recipes.")
    else:
        station = st.selectbox("Select Station", station_ids, key="recipe_station")
        inputs = st.multiselect("Select Input Items (optional)", item_ids, key="inputs")

        input_qtys = []
        if inputs:
            for i in inputs:
                qty = st.number_input(f"Qty for {i}", min_value=1, value=1, key=f"in_{i}")
                input_qtys.append(qty)

        outputs = st.multiselect("Select Output Items (optional)", item_ids, key="outputs")

        output_qtys = []
        if outputs:
            for o in outputs:
                qty = st.number_input(f"Qty for {o}", min_value=1, value=1, key=f"out_{o}")
                output_qtys.append(qty)

        if st.button("Add Recipe"):
            builder.define_recipes(
                station,
                inputs if inputs else [],
                input_qtys if inputs else [],
                outputs if outputs else [],
                output_qtys if outputs else []
            )
            st.success("Recipe Added")
            
    st.subheader("Sink Item")

    sink_item = st.selectbox("Select Sink Item", options=builder.items, key="sink_item")

    if st.button("Add Sink Item"):
        builder.define_sink_item(sink_item)
        st.success("Sink item set")
    st.divider()
    st.subheader("Save Config")

    filename = st.text_input("Enter Name of the File", value="new_config.json", key="filename")
    col1,col2 = st.columns(2)
    
    if col1.button("Save Config"):
        builder.save_to_json(filename)
        st.success(f"Saved to {filename}")
        st.rerun()
    
    if col2.button("Reset Builder"):
        builder.reset()
        st.success("Builder reset successfully.")
        st.rerun()




if not st.session_state.get('builder_mode',True):
    config = st.session_state["base_config"]
    result = st.session_state["result"]
    engine = result["engine"]
    system_df = result["system_summary"]
    station_df = result["station_summary"]
    buffer_df = result["buffer_summary"]
    diagnosis = result["diagnosis"]
    station_info = result["station_info"]
    
    tab1,tab2,tab3 = st.tabs(['System Summary','Station Summary','Buffer Summary'])

    with tab1:
        st.subheader("System Summary")

        cols = st.columns(5)

        system_row = system_df.iloc[0]

        cols[0].metric("Duration", system_row["duration"])
        cols[1].metric("Finished Goods", system_row["total_finished_goods"])
        cols[2].metric("Throughput", round(system_row["throughput_per_time_unit"], 4))
        cols[3].metric("Total WIP", system_row["total_wip"])
        cols[4].metric("Stations", system_row["num_stations"])
    
    with tab2:
        st.subheader("Station Summary")
        st.dataframe(station_df, width="stretch")
    
    with tab3:
        st.subheader("Buffer Summary")
        st.dataframe(buffer_df, width="stretch")

    st.divider()
    
    
    station_ids = result['station_summary']['station_id'].tolist()
    st.subheader("Station Info")
    tab_names = [station_info[station_id]['station_name'] for station_id in station_ids]
    tabs = st.tabs(tab_names)
    for tab, station_id in zip(tabs, station_ids):
        info = station_info[station_id]
        with tab:
            col1, col2, col3 = st.columns(3)
            col1.metric("Station Name", info['station_name'])
            col2.metric("Station Type", info['station_type'])
            col3.metric("Station Cycle Time", info['station_cycle_time'])
            st.write("### Flow Details")

            flow_data = {
                "Property": ["Inputs", "Outputs"],
                "Value": [
                    format_value(list(info["station_inputs"].keys())),
                    format_value(list(info["station_outputs"].keys()))
                ]
            }

            st.table(flow_data)

    st.divider()

    st.subheader("Bottleneck Diagnosis")

    main_diagnosis = {
        key: value
        for key, value in diagnosis.items()
        if key != "flow_bottleneck_analysis"
    }

    diagnosis_rows = []

    for key, value in main_diagnosis.items():   
        diagnosis_rows.append({
            "Metric": text_replace(key),
            "Result": format_value(value)
        })

    diagnosis_df = pd.DataFrame(diagnosis_rows)

    st.table(diagnosis_df)
    
    flow_analysis = diagnosis.get("flow_bottleneck_analysis", {})

    if flow_analysis:
        st.subheader("Flow Bottleneck Analysis")

        flow_table = {}

        for station_key, station_details in flow_analysis.items():
            station_name = text_replace(station_key)

            flow_table[station_name] = {
                "Downstream Station": format_value(station_details.get("downstream_station")),
                "Accumulating Buffers": format_value(station_details.get("accumulating_buffers")),
                "Scarce Buffers": format_value(station_details.get("scarce_buffers")),
                "Likely Bottleneck": format_value(station_details.get("likely_bottleneck"))
            }

        flow_df = pd.DataFrame(flow_table)

        st.table(flow_df)
    st.divider()
    
    st.subheader("Metric Visualizations")
    
    station_graph_options = {
        "Utilization": "utilization",
        "Completed Cycles": "completed_cycles",
        "Busy Time": "busy_time",
        "Starved Time": "starved_time",
        "Blocked Time": "blocked_time"
    }
    
    selected_graph = st.selectbox(
    "Choose metric to visualize",
    list(station_graph_options.keys())
    )

    fig_util = px.bar(station_df,x="station_name",y=station_graph_options[selected_graph],text=station_graph_options[selected_graph],title=f"Station {selected_graph}")

    st.plotly_chart(fig_util, width="stretch")
    
    tab1,tab2 = st.tabs(["Buffer Final Level","Buffer Level Graph"])
    with tab1:
        fig_buffer = px.bar(buffer_df,x="connection_id",y="final_level",text="final_level",title="Final Buffer Levels")
        st.plotly_chart(fig_buffer, width="stretch")
    with tab2:
        buffer_conn_id = st.selectbox("Select buffer for level graph", buffer_df['connection_id'].tolist())
        data = mt.buffer_history(engine, buffer_conn_id)
        fig_buffer_hist = px.line(data,x="time",y="level",title=f"Buffer Level Over Time for {buffer_conn_id}")
        st.plotly_chart(fig_buffer_hist, width="stretch")

    st.divider()
    st.header("Assembly Line Visualization")
    st.session_state["graph"] = generate_graph(config)
    st.plotly_chart(st.session_state["graph"], width="stretch")
    st.divider()
    if "scenario" not in st.session_state:
        st.session_state["scenario"] = Scenario(st.session_state["scenario_config"])
    
    scenario = st.session_state["scenario"]
    st.header("Scenario Builder")
    st.subheader("Station Changes")
    selected_station_id = st.selectbox("Select station to modify", station_ids)
    selected_station_info = station_info[selected_station_id]
    current_cycle_time = float(selected_station_info['station_cycle_time'])
    cycle_time_change = st.number_input("New cycle time", min_value=0.0, value=current_cycle_time, step=0.5)
    left,right = st.columns(2)
    selected_input_item = left.selectbox("Select item to modify Input amount for", selected_station_info['station_inputs'])
    selected_input_qty = left.number_input("New input quantity", min_value=0, value=int(selected_station_info['station_inputs'][selected_input_item]), step=1) if selected_station_info['station_inputs'] else None
    selected_output_item = right.selectbox("Select item to modify Output amount for", selected_station_info['station_outputs'])
    selected_output_qty = right.number_input("New output quantity", min_value=0, value=int(selected_station_info['station_outputs'][selected_output_item]), step=1) if selected_station_info['station_outputs'] else None  
    if left.button("Apply Changes"):
        scenario.apply_cycle_time_change(selected_station_id, cycle_time_change)
        scenario.apply_recipe_input_change(selected_station_id, selected_input_item, selected_input_qty) if selected_input_qty is not None else None
        scenario.apply_recipe_output_change(selected_station_id, selected_output_item, selected_output_qty) if selected_output_qty is not None else None
        st.success("Changes applied to scenario config. Click 'Run Scenario Analysis' to see the impact of these changes.")
    
    if right.button("Reset Scenario"):

        if "scenario" in st.session_state:
            del st.session_state["scenario"]

        st.session_state["scenario"] = Scenario(
            st.session_state["scenario_config"]
        )

        st.success("Scenario reset successfully.")

        st.rerun()
    
    st.subheader("Buffer Changes")
    selected_buffer_id = st.selectbox("Select buffer to modify", buffer_df['connection_id'].tolist())
    capacity = buffer_df[buffer_df['connection_id'] == selected_buffer_id]['capacity'].iloc[0]
    selected_buffer_capacity = st.number_input("New buffer capacity", min_value=0, value=int(capacity), step=1)
    if st.button("Apply Buffer Change"):
        scenario.apply_buffer_capacity_change(selected_buffer_id, selected_buffer_capacity)
        st.success("Buffer capacity change applied to scenario config. Click 'Run Scenario Analysis' to see the impact of this change.")
            
    @st.dialog("show changes")
    def show_changes():
        st.write(scenario.changes)
        
    st.button("Show Applied Changes", on_click=show_changes)
    st.divider()
    st.header("Scenario Analysis")
    left,center,right = st.columns(3)
    center.write("Click the button below to run scenario analysis and compare the modified scenario against the baseline.")
    if center.button("Run Scenario Analysis"):
        scenario_result = run_scenario_analysis(st.session_state["base_config"], scenario.config)
        system_comparison = scenario_result['system_comparison']
        station_comparison = scenario_result['station_comparison']
        buffer_comparison = scenario_result['buffer_comparison']
        diagnosis_comparison = scenario_result['diagnosis_comparison']

        st.subheader("System Comparison")
        st.table(system_comparison, width="stretch")

        st.subheader("Station Comparison")
        st.dataframe(station_comparison, width="stretch")

        st.subheader("Buffer Comparison")
        st.dataframe(buffer_comparison, width="stretch")

        st.subheader("Diagnosis Comparison")
        diagnosis_rows = []
        formatted_df = diagnosis_comparison.copy()

        formatted_df["diagnosis_metric"] = formatted_df["diagnosis_metric"].apply(text_replace)
        formatted_df["baseline"] = formatted_df["baseline"].apply(format_value)
        formatted_df["scenario"] = formatted_df["scenario"].apply(format_value)
        formatted_df["changed"] = formatted_df["changed"].apply(format_value)

        st.dataframe(formatted_df, use_container_width=True)
        
        st.divider()
        
    else:
        st.info("Make changes in the scenario builder and click 'Run Scenario Analysis' to see the comparison results between the baseline and modified scenario.")

    
    

else:
    st.info("Choose a config from the sidebar and click Run Simulation.")

    