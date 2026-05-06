# Assembly Line Bottleneck Diagnosis and Throughput Optimization Simulator

A configurable discrete-event manufacturing simulation platform built using SimPy and Streamlit.

This project simulates manufacturing systems with process stations, assembly stations, configurable material flow, buffers, and multi-stage production logic. It provides bottleneck diagnosis, throughput analysis, scenario experimentation, and interactive visualizations through a Streamlit dashboard.

---

# Features

## Manufacturing Simulation

* Discrete-event simulation using SimPy
* Configurable JSON-based production lines
* Process stations
* Assembly stations
* Multi-stage assembly workflows
* Automatic station and buffer wiring
* Sink output tracking
* Dynamic material flow configuration

---

## Buffer + WIP Analysis

* Buffer inventory tracking
* Buffer capacity modeling
* WIP tracking
* Buffer history recording
* Buffer level visualizations
* Starvation and blockage detection

---

## Bottleneck Diagnosis

Includes automatic diagnosis of:

* Most utilized station
* Most blocked station
* Most starved station
* Largest final buffer accumulation
* Largest peak buffer accumulation
* Flow bottleneck analysis
* Root bottleneck tracing

---

## Scenario Analysis

Supports counterfactual experimentation by modifying:

* Station cycle times
* Recipe input quantities
* Recipe output quantities
* Buffer capacities

Then compares:

* Throughput
* Utilization
* WIP
* Buffer behavior
* Diagnosis results

against the baseline system.

---

## Interactive Streamlit Dashboard

The dashboard includes:

* System summary metrics
* Station summary tables
* Buffer summary tables
* Station flow information
* Plotly metric visualizations
* Buffer history graphs
* Scenario builder
* Scenario comparison tools
* Interactive config builder

---

## Config Builder

The project includes an integrated configuration builder for creating manufacturing systems interactively.

Supports:

* Defining simulations
* Defining stations
* Defining items
* Defining connections
* Defining recipes
* Defining sink items
* Saving configs as JSON

---

# Example Manufacturing Logic

Supports workflows such as:

```text id="ex1"
A + B -> C
C + D -> E
```

including multi-stage assembly systems.

---

# Tech Stack

* Python
* SimPy
* Streamlit
* Pandas
* Plotly
* NumPy

---

# Project Structure

```text id="ex2"
Assembly Line Simulator/
│
├── examples/
│   ├── simple_line.json
│   ├── assembly_line.json
│   ├── multi_stage_assembly.json
│   ├── assembly_line_without_buffer.json
│   ├── new_config.json
│
├── simulator/
│   ├── analysis.py
│   ├── buffer.py
│   ├── builder.py
│   ├── comparison.py
│   ├── config.py
│   ├── engine.py
│   ├── metrics.py
│   ├── scenario.py
│   └── station.py
│
├── app.py
├── README.md
└── requirements.txt
```

---

# Installation

## Clone the repository

```bash id="ex3"
git clone <your-repository-url>
cd "Assembly Line Simulator"
```

---

## Create virtual environment

### Windows

```bash id="ex4"
python -m venv venv
venv\Scripts\activate
```

### Linux / Mac

```bash id="ex5"
python3 -m venv venv
source venv/bin/activate
```

---

## Install dependencies

```bash id="ex6"
pip install -r requirements.txt
```

---

# Run the Application

```bash id="ex7"
streamlit run app.py