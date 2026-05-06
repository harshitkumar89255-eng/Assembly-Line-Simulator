from simulator.engine import SimulationEngine
import pandas as pd
import simulator.metrics as mt
import simulator.comparison as comp


def run_engine(config):
    engine = SimulationEngine(config)
    engine.run()
    return engine


def run_analysis(config):
    engine = run_engine(config)

    system_summary = mt.system_summary(engine)
    station_summary = mt.station_summary(engine)
    buffer_summary = mt.buffer_summary(engine)

    station_info = {}

    for station_id in engine.stations.keys():
        station_info[station_id] = mt.station_info(engine, station_id)

    diagnosis = mt.diagnose(engine)

    return {
        'engine': engine,
        'system_summary': system_summary,
        'station_summary': station_summary,
        'buffer_summary': buffer_summary,
        'diagnosis': diagnosis,
        'station_info': station_info
    }


def run_scenario_analysis(base_config, scenario_config):
    baseline_result = run_analysis(base_config)
    scenario_result = run_analysis(scenario_config)

    engine_1 = baseline_result['engine']
    engine_2 = scenario_result['engine']

    system_comparison = comp.compare_system(engine_1, engine_2)
    station_comparison = comp.compare_all_stations(engine_1, engine_2)

    buffer_comparison = pd.DataFrame()

    for conn_id in engine_1.buffers.keys():
        buffer_comp = comp.compare_buffer(engine_1, engine_2, conn_id)
        buffer_comparison = pd.concat([buffer_comparison, buffer_comp], axis=1)

    diagnosis_comparison = compare_diagnosis(
        baseline_result['diagnosis'],
        scenario_result['diagnosis']
    )

    return {
        'baseline': baseline_result,
        'scenario': scenario_result,
        'system_comparison': system_comparison,
        'station_comparison': station_comparison,
        'buffer_comparison': buffer_comparison,
        'diagnosis_comparison': diagnosis_comparison
    }


def compare_diagnosis(baseline_diagnosis, scenario_diagnosis):
    rows = []

    all_keys = set(baseline_diagnosis.keys()) | set(scenario_diagnosis.keys())

    for key in all_keys:
        if key != 'flow_bottleneck_analysis':
            rows.append({
                'diagnosis_metric': key,
                'baseline': baseline_diagnosis.get(key),
                'scenario': scenario_diagnosis.get(key),
                'changed': baseline_diagnosis.get(key) != scenario_diagnosis.get(key)
            })

    return pd.DataFrame(rows)