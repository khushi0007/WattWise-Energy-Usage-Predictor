# Energy Usage Predictor — Rule-Based

A Python Flask decision-support website for an Advanced Python assignment.

## Features

- Rule-based usage forecast
- Seasonal adjustment
- Threshold warnings
- Conservation advice
- Annual summary
- Usage trend chart
- Electricity cost estimator

## Technology

- Backend: Python + Flask only
- Frontend: HTML + CSS + JavaScript
- Chart: Chart.js

C/C++ is not required for the browser frontend. If your assignment specifically requires a C/C++ component, it can be added separately as an optional compiled module, while Flask remains the Python backend.

## Run on Windows

1. Install Python 3.
2. Open Command Prompt inside this folder.
3. Install dependencies:

   `pip install -r requirements.txt`

4. Start the server:

   `python app.py`

5. Open:

   `http://127.0.0.1:5000`

## How the rules work

Seasonal factors:
- Winter = 0.90
- Summer = 1.20
- Monsoon = 1.00
- Normal = 1.00

Thresholds:
- Below 200 kWh = Low
- 200–399 kWh = Normal
- 400–599 kWh = High
- 600+ kWh = Critical

Forecast:
Historical average × seasonal factor

Trend:
- Latest month > previous month by more than 5% = Increasing
- Latest month < previous month by more than 5% = Decreasing
- Otherwise = Stable
