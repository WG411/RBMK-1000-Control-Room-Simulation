# RBMK-1000 Control Room Simulation

A Python-based RBMK-1000 control room simulator developed using Tkinter.

The simulator models reactor kinetics, reactivity feedback, thermal-hydraulic behavior, control rod movement, coolant flow, feedwater, turbine loading, reactor protection systems, and operator controls.

## Features

- Reactor power simulation
- Control rod insertion and withdrawal
- Automatic power hold control
- Fuel and coolant temperature modeling
- Reactor pressure modeling
- Coolant flow control
- Feedwater control
- Turbine load control
- Main circulation pump trips
- Turbine trips
- Steam dump system
- AZ-5 / SCRAM system
- Reactor alarms and status monitoring
- Real-time Tkinter control interface

## Project Structure

- `main.py` - Program entry point
- `config.py` - Simulator constants and configuration
- `reactor_model.py` - Reactor physics and simulation model
- `control_logic.py` - Reactor and plant control logic
- `ui.py` - Tkinter user interface
- `monitoring.py` - Readouts, alarms, and simulation update loop

## Running the Simulator

Python 3 is required.

```bash
python main.py
```


