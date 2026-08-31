const months = [
    "Jan","Feb","Mar","Apr","May","Jun",
    "Jul","Aug","Sep","Oct","Nov","Dec"
];

const monthGrid = document.getElementById("monthGrid");

months.forEach((month, index) => {
    const label = document.createElement("label");
    label.innerHTML = `${month}
        <input class="usage-input" data-month="${index + 1}"
               type="number" min="0" step="0.1"
               placeholder="kWh">`;
    monthGrid.appendChild(label);
});

function getUsages() {
    return [...document.querySelectorAll(".usage-input")]
        .map(x => x.value.trim())
        .filter(x => x !== "")
        .map(Number);
}

async function analyze() {
    const usages = getUsages();
    const month = Number(document.getElementById("predictionMonth").value);
    const nightPercent = Number(document.getElementById("nightPercent").value);

    if (!usages.length) {
        alert("Please enter at least one monthly usage value.");
        return;
    }

    const response = await fetch("/api/analyze", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ usages, month, night_percent: nightPercent })
    });

    const data = await response.json();

    if (data.error) {
        alert(data.error);
        return;
    }

    document.getElementById("prediction").innerHTML =
        `${data.prediction} <small>kWh</small>`;
    document.getElementById("average").textContent = `${data.average} kWh`;
    document.getElementById("season").textContent = data.season;
    document.getElementById("factor").textContent = `${data.factor}×`;
    document.getElementById("trend").textContent = data.trend;

    const status = document.getElementById("statusBox");
    status.textContent = `${data.status} Usage`;
    status.className = `status ${data.status_class}`;

    const advice = document.getElementById("recommendations");
    advice.innerHTML = data.recommendations.map(r =>
        `<div class="advice-item"><b>${r.priority} Priority</b>${r.text}</div>`
    ).join("");

    updateChart(usages);
}

async function annualSummary() {
    const usages = getUsages();

    if (!usages.length) {
        alert("Please enter annual monthly usage first.");
        return;
    }

    const response = await fetch("/api/annual-summary", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ usages })
    });

    const data = await response.json();

    if (data.error) {
        alert(data.error);
        return;
    }

    document.getElementById("annualTotal").textContent = `${data.total} kWh`;
    document.getElementById("annualAverage").textContent = `${data.average} kWh`;
    document.getElementById("annualHighest").textContent =
        `${months[data.highest_month - 1]} — ${data.highest} kWh`;
    document.getElementById("annualLowest").textContent =
        `${months[data.lowest_month - 1]} — ${data.lowest} kWh`;
}

async function calculateCost() {
    const usage = Number(document.getElementById("costUsage").value);
    const rate = Number(document.getElementById("rate").value);

    if (usage < 0 || rate < 0 || Number.isNaN(usage) || Number.isNaN(rate)) {
        alert("Enter valid non-negative numbers.");
        return;
    }

    const response = await fetch("/api/cost", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ usage, rate })
    });

    const data = await response.json();

    document.getElementById("costResult").textContent =
        `Estimated cost: ₹${data.cost.toLocaleString("en-IN")}`;
}

let chart;

function updateChart(usages) {
    const ctx = document.getElementById("usageChart").getContext("2d");

    if (chart) chart.destroy();

    chart = new Chart(ctx, {
        type: "line",
        data: {
            labels: months.slice(0, usages.length),
            datasets: [{
                label: "Energy Usage (kWh)",
                data: usages,
                tension: 0.35,
                borderWidth: 3,
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: true } },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}
