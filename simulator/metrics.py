import pandas as pd
from pathlib import Path    

def station_summary(engine):
    rows = []
    duration = max(engine.duration,1)
    
    for station_id,station in engine.stations.items():
        utilization = station.busy_time/duration
        for item_id,qty in station.outputs.items():
            quant = qty
        rows.append({
            "station_id" : station_id,
            "station_name": station.name,
            "station_type":station.type,
            "completed_cycles":station.completed_cycles,
            "busy_time": station.busy_time,
            "starved_time": station.starved_time,
            "blocked_time": station.blocked_time,
            "utilization": utilization,
            "finished_output_count": quant*station.completed_cycles,
            "final_state": station.state
            })
        
    return pd.DataFrame(rows)
        
def buffer_summary(engine):
    rows = []
    
    for conn_id,buffer in engine.buffers.items():
        if buffer.history:
            levels = [level for _,level in buffer.history]
            max_level = max(levels)
            min_level = min(levels)
        else:
            max_level = buffer.level
            min_level = buffer.level
            
        rows.append({
            "connection_id":conn_id,
            "buffer_id":buffer.buffer_id,
            "item_id":buffer.item_id,
            "capacity":buffer.capacity,
            "final_level":buffer.level,
            "max_level":max_level,
            "min_level":min_level,
            "fill_ratio":(buffer.level/buffer.capacity) if buffer.capacity else 0
        })
        
    return pd.DataFrame(rows)
    
def system_summary(engine):
    rows = []
    total_finished_products = 0
    for station in engine.stations.values():
        total_finished_products += station.finished_output_count

    total_wip = sum(buffer.level for conn_id,buffer in engine.buffers.items())

    rows.append({
        "duration": engine.duration,
        "tick": engine.tick,
        "total_finished_goods": total_finished_products,
        "throughput_per_time_unit": (total_finished_products / engine.duration) if engine.duration else 0,
        "total_wip": total_wip,
        "num_stations": len(engine.stations),
        "num_buffers": len(engine.buffers)
    })
    return pd.DataFrame(rows)
    

def save_metrics(engine,save_dir=None,name_prefix=None):
    station_df =  station_summary(engine)
    buffer_df = buffer_summary(engine)
    system_df = system_summary(engine)
    if save_dir is None:
        project_root = Path(__file__).parent.parent
        save_dir = project_root / "saved_data"
    else:
        save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)
    station_df.to_csv(save_dir / f"{name_prefix}_stations_summary.csv",index=False)
    buffer_df.to_csv(save_dir / f"{name_prefix}_buffers_summary.csv",index=False)
    system_df.to_csv(save_dir / f"{name_prefix}_system_summary.csv",index=False)

def buffer_history(engine,conn_id:str):
    buffer = engine.buffers[conn_id]
    if not buffer.history:
        return pd.DataFrame(columns=['time','level'])
    else:
        return pd.DataFrame(buffer.history,columns=['time','level'])
    
def buffer_info(engine,conn_id:str):
    df = buffer_history(engine,conn_id)
    df.set_index('time',inplace=True)
    return df
    
def diagnose(engine, accumulation_delta_threshold=0.05, accumulation_level_threshold=0.10, scarcity_threshold=0.50):
    station_df = station_summary(engine)
    buffer_df = buffer_summary(engine)

    diagnosis = {
        "most_utilized": [],
        "most_starved": [],
        "most_blocked": [],
        "largest_buffer_end_level": [],
        "largest_buffer_max_level": [],
        "local_bottlenecks": [],
        "likely_bottlenecks": [],
        "flow_bottleneck_analysis": {}
    }

    if not station_df.empty:
        diagnosis["most_utilized"] = list(station_df.loc[station_df["utilization"] == station_df["utilization"].max(), "station_name"].values)
        diagnosis["most_starved"] = list(station_df.loc[station_df["starved_time"] == station_df["starved_time"].max(), "station_name"].values)
        diagnosis["most_blocked"] = list(station_df.loc[station_df["blocked_time"] == station_df["blocked_time"].max(), "station_name"].values) if station_df["blocked_time"].max() > 0 else ["No Blocked Stations"]

    if not buffer_df.empty:
        diagnosis["largest_buffer_end_level"] = list(buffer_df.loc[buffer_df["final_level"] == buffer_df["final_level"].max(), "buffer_id"].values)
        diagnosis["largest_buffer_max_level"] = list(buffer_df.loc[buffer_df["max_level"] == buffer_df["max_level"].max(), "buffer_id"].values)

    recipe_map = {recipe["station_id"]: recipe for recipe in engine.config["recipes"]}
    station_name_map = {station["id"]: station["name"] for station in engine.config["stations"]}
    station_type_map = {station["id"]: station["type"] for station in engine.config["stations"]}

    downstream_ids = list(dict.fromkeys(conn["to_station"] for conn in engine.config["connections"]))
    local_ids = []

    for downstream in downstream_ids:
        if station_type_map.get(downstream) == "sink":
            continue

        inbound = [conn for conn in engine.config["connections"] if conn["to_station"] == downstream]
        accumulating_buffers, scarce_buffers = [], []

        for conn in inbound:
            buffer_obj = engine.buffers[conn["id"]]
            history = buffer_obj.history or [(0, buffer_obj.level)]
            levels = [level for _, level in history]
            n = len(levels)
            window = max(1, min(50, n // 4))

            early_avg = sum(levels[:window]) / window
            late_avg = sum(levels[-window:]) / window
            required_qty = recipe_map.get(downstream, {}).get("inputs", {}).get(conn["item_id"], 1)
            scarcity_ratio = sum(1 for level in levels if level < required_qty) / n if n else 0
            avg_delta_ratio = ((late_avg - early_avg) / buffer_obj.capacity) if buffer_obj.capacity else 0
            final_ratio = (buffer_obj.level / buffer_obj.capacity) if buffer_obj.capacity else 0
            max_ratio = (max(levels) / buffer_obj.capacity) if buffer_obj.capacity else 0

            is_accumulating = avg_delta_ratio >= accumulation_delta_threshold or final_ratio >= accumulation_level_threshold or max_ratio >= accumulation_level_threshold
            is_scarce = scarcity_ratio >= scarcity_threshold

            if is_accumulating:
                accumulating_buffers.append(conn)
            if is_scarce:
                scarce_buffers.append(conn)

        result = {
            "downstream_station": downstream,
            "accumulating_buffers": [conn["id"] for conn in accumulating_buffers],
            "scarce_buffers": [conn["id"] for conn in scarce_buffers],
            "likely_bottleneck": None
        }

        if len(inbound) == 1:
            if scarce_buffers:
                result["likely_bottleneck"] = inbound[0]["from_station"]
                local_ids.append(inbound[0]["from_station"])
            elif accumulating_buffers:
                result["likely_bottleneck"] = downstream
                local_ids.append(downstream)

        else:
            if len(scarce_buffers) == 1:
                result["likely_bottleneck"] = scarce_buffers[0]["from_station"]
                local_ids.append(scarce_buffers[0]["from_station"])
            elif len(scarce_buffers) > 1:
                ids = list(dict.fromkeys(conn["from_station"] for conn in scarce_buffers))
                result["likely_bottleneck"] = ids
                local_ids.extend(ids)
            elif len(accumulating_buffers) == len(inbound):
                result["likely_bottleneck"] = downstream
                local_ids.append(downstream)

        diagnosis["flow_bottleneck_analysis"][downstream] = result

    def _flat(items):
        out = []
        for item in items:
            out.extend(item if isinstance(item, list) else [item])
        return out

    local_ids = _flat(local_ids)
    diagnosis["local_bottlenecks"] = list(dict.fromkeys(station_name_map.get(station_id, station_id) for station_id in local_ids))

    local_map = {station_id: result["likely_bottleneck"] for station_id, result in diagnosis["flow_bottleneck_analysis"].items()}

    def _root(station_id, seen=None):
        seen = seen or set()
        if station_id in seen:
            return [station_id]
        seen.add(station_id)

        nxt = local_map.get(station_id)
        if nxt is None:
            return [station_id]
        if isinstance(nxt, list):
            roots = []
            for item in nxt:
                roots.extend(_root(item, seen.copy()))
            return roots
        if nxt == station_id:
            return [station_id]
        return _root(nxt, seen)

    root_ids = []
    for station_id in local_ids:
        root_ids.extend(_root(station_id))

    root_names = list(dict.fromkeys(station_name_map.get(station_id, station_id) for station_id in root_ids))

    if root_names:
        diagnosis["likely_bottlenecks"] = root_names
    elif not station_df.empty:
        candidates = station_df.loc[station_df["utilization"] == station_df["utilization"].max()].copy()
        candidates = candidates.loc[candidates["starved_time"] == candidates["starved_time"].min()].copy() if not candidates.empty else candidates
        candidates = candidates.loc[candidates["blocked_time"] == candidates["blocked_time"].min()].copy() if not candidates.empty else candidates
        diagnosis["likely_bottlenecks"] = list(candidates["station_name"].values)

    return diagnosis

def station_info(engine,station_id):
    station = engine.stations[station_id]
    
    info = {
        "station_id": station.id,
        "station_name": station.name,
        "station_type": station.type,
        "station_cycle_time": station.cycle_time,
        "station_inputs": station.inputs,
        "station_outputs": station.outputs,
    }
    return info