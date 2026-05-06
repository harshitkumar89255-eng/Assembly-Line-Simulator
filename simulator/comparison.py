import pandas as pd
import simulator.metrics as mt

def compare_system(baseline_engine,scenario_engine):
    baseline_df = mt.system_summary(baseline_engine)
    scenario_df = mt.system_summary(scenario_engine)
    
    df = pd.concat([baseline_df,scenario_df],axis=0)
    df_flipped = df.T
    df_flipped.columns = ['baseline','scenario']
    df_flipped['delta'] = df_flipped['scenario'] - df_flipped['baseline']
    return df_flipped

def compare_station(baseline_engine,scenario_engine,station_id):
    baseline_df = mt.station_summary(baseline_engine)
    scenario_df = mt.station_summary(scenario_engine)
    
    baseline_station = baseline_df[baseline_df['station_id'] == station_id]
    scenario_station = scenario_df[scenario_df['station_id'] == station_id]
    
    if baseline_station.empty or scenario_station.empty:
        raise ValueError(f"Station ID {station_id} not found in one of the engines.")
    
    df = pd.concat([baseline_station,scenario_station],axis=0)
    df = df.select_dtypes(include="number")
    df_flipped = df.T
    df_flipped.columns = [f"{station_id}_baseline", f"{station_id}_scenario"]
    df_flipped[f'{station_id}delta'] = df_flipped[f"{station_id}_scenario"] - df_flipped[f"{station_id}_baseline"]
    return df_flipped

def compare_buffer(baseline_engine,scenario_engine,conn_id):
    baseline_df = mt.buffer_summary(baseline_engine)
    scenario_df = mt.buffer_summary(scenario_engine)
    
    baseline_buffer = baseline_df[baseline_df['connection_id'] == conn_id]
    scenario_buffer = scenario_df[scenario_df['connection_id'] == conn_id]
    
    if baseline_buffer.empty or scenario_buffer.empty:
        raise ValueError(f"Connection ID {conn_id} not found in one of the engines.")
    
    df = pd.concat([baseline_buffer,scenario_buffer],axis=0)
    df = df.select_dtypes(include="number")
    df_flipped = df.T
    df_flipped.columns = [f'{conn_id}_baseline', f'{conn_id}_scenario']
    df_flipped[f'{conn_id}_delta'] = df_flipped[f'{conn_id}_scenario'] - df_flipped[f'{conn_id}_baseline']
    return df_flipped

def compare_all_stations(baseline_engine,scenario_engine):
    df  = pd.DataFrame()
    for station_id in baseline_engine.stations.keys():
        station_comparison = compare_station(baseline_engine,scenario_engine,station_id)
        df = pd.concat([df,station_comparison],axis=1)
    return df
