from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Dictionaries, tuples and sets
SEASON_RULES = {'Winter': 0.90, 'Summer': 1.20, 'Monsoon': 1.00, 'Normal': 1.00}
THRESHOLDS = (200, 400, 600)
WINTER_MONTHS = {12, 1, 2}
SUMMER_MONTHS = {3, 4, 5, 6}
MONSOON_MONTHS = {7, 8, 9}
MONTH_NAMES = ('January','February','March','April','May','June','July','August','September','October','November','December')

def get_season(month):
    if month in WINTER_MONTHS:
        return 'Winter'
    elif month in SUMMER_MONTHS:
        return 'Summer'
    elif month in MONSOON_MONTHS:
        return 'Monsoon'
    else:
        return 'Normal'

def calculate_average(usages):
    total = 0
    for value in usages:
        total = total + value
    if len(usages) > 0:
        return total / len(usages)
    else:
        return 0

def classify_usage(usage):
    low, high, critical = THRESHOLDS
    if usage < low:
        return 'Low', 'low'
    elif usage < high:
        return 'Normal', 'normal'
    elif usage < critical:
        return 'High', 'high'
    else:
        return 'Critical', 'critical'

def predict_usage(usages, month):
    average = calculate_average(usages)
    season = get_season(month)
    factor = SEASON_RULES[season]
    prediction = average * factor
    return round(prediction, 2), round(average, 2), season, factor

def detect_trend(usages):
    if len(usages) < 2:
        return 'Stable'
    previous = usages[-2]
    latest = usages[-1]
    if latest > previous * 1.05:
        return 'Increasing'
    elif latest < previous * 0.95:
        return 'Decreasing'
    else:
        return 'Stable'

def create_recommendations(usage, season, trend, night_percent):
    recommendations = []
    if usage >= 600:
        recommendations.append(('Critical', 'Reduce high-power appliance usage immediately.'))
    elif usage >= 400:
        recommendations.append(('High', 'Reduce unnecessary appliance usage and check high-power devices.'))
    if season == 'Summer' and usage >= 350:
        recommendations.append(('Medium', 'Optimize AC and cooling usage to reduce summer consumption.'))
    if night_percent > 30:
        recommendations.append(('Medium', 'Night consumption is high. Switch off standby devices.'))
    if trend == 'Increasing':
        recommendations.append(('High', 'Energy consumption is increasing. Check which appliances caused the rise.'))
    if usage < 200:
        recommendations.append(('Low', 'Good energy performance. Continue your energy-saving habits.'))
    if len(recommendations) == 0:
        recommendations.append(('Low', 'Maintain your current energy-saving habits.'))
    return [{'priority': p, 'text': t} for p, t in recommendations]  # list comprehension

def analyze_energy(usages, month, night_percent):
    prediction, average, season, factor = predict_usage(usages, month)
    status, status_class = classify_usage(prediction)
    trend = detect_trend(usages)
    advice = create_recommendations(prediction, season, trend, night_percent)
    return {'average': average, 'prediction': prediction, 'season': season, 'factor': factor,
            'status': status, 'status_class': status_class, 'trend': trend, 'recommendations': advice}

def annual_summary(usages):
    total = 0
    for value in usages:
        total = total + value
    average = total / len(usages)
    highest = max(usages)
    lowest = min(usages)
    return {'total': round(total,2), 'average': round(average,2), 'highest': highest, 'lowest': lowest,
            'highest_month': usages.index(highest)+1, 'lowest_month': usages.index(lowest)+1,
            'months_recorded': len(usages)}

def calculate_cost(usage, rate):
    return round(usage * rate, 2)

def clean_values(values):
    # Generator expression
    positive = (float(value) for value in values if float(value) >= 0)
    return list(positive)

def rule_check_table(usages):
    # Nested loops: every usage is checked against every rule level.
    levels = ['Low', 'Normal', 'High', 'Critical']
    checked = []
    for usage in usages:
        matches = []
        for level in levels:
            if level == 'Low' and usage < 200:
                matches.append(level)
            elif level == 'Normal' and 200 <= usage < 400:
                matches.append(level)
            elif level == 'High' and 400 <= usage < 600:
                matches.append(level)
            elif level == 'Critical' and usage >= 600:
                matches.append(level)
        checked.append(matches[0] if len(matches) > 0 else 'Unknown')
    return checked

@app.route('/')
def home():
    return render_template('index.html')

@app.post('/api/analyze')
def analyze_api():
    data = request.get_json(silent=True) or {}
    raw = data.get('usages', [])
    month = int(data.get('month', 1))
    night_percent = float(data.get('night_percent', 0))
    if not isinstance(raw, list):
        return jsonify({'error': 'Usage data must be a list.'}), 400
    try:
        usages = clean_values(raw)
    except (ValueError, TypeError):
        return jsonify({'error': 'Enter valid numeric values.'}), 400
    if len(usages) == 0:
        return jsonify({'error': 'Enter at least one usage value.'}), 400
    result = analyze_energy(usages, month, night_percent)
    result['rule_statuses'] = rule_check_table(usages)
    return jsonify(result)

@app.post('/api/annual-summary')
def annual_api():
    data = request.get_json(silent=True) or {}
    try:
        usages = clean_values(data.get('usages', []))
    except (ValueError, TypeError):
        return jsonify({'error': 'Enter valid numeric values.'}), 400
    if len(usages) == 0:
        return jsonify({'error': 'Enter annual usage data.'}), 400
    return jsonify(annual_summary(usages))

@app.post('/api/cost')
def cost_api():
    data = request.get_json(silent=True) or {}
    try:
        usage = float(data.get('usage', 0))
        rate = float(data.get('rate', 0))
    except (ValueError, TypeError):
        return jsonify({'error': 'Enter valid numbers.'}), 400
    if usage < 0 or rate < 0:
        return jsonify({'error': 'Values cannot be negative.'}), 400
    return jsonify({'cost': calculate_cost(usage, rate)})

if __name__ == '__main__':
    app.run(debug=True)

