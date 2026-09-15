"""
Simple Machine Health Monitor
------------------------------
Simulates temperature and vibration sensor readings from an industrial
machine, checks each reading against safe operating thresholds, logs
every reading (and any alerts) to CSV files, and plots the readings
over time with the alert points highlighted.

This is a rule-based (threshold) health monitor — a simplified,
software-only version of the kind of Predictive/Condition Monitoring
solution UCT builds for industrial machines.
"""

import csv
import random
from datetime import datetime, timedelta

import matplotlib.pyplot as plt

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------
NUM_READINGS = 200          # number of simulated sensor readings
READING_INTERVAL_SEC = 30   # simulated time gap between readings

TEMP_SAFE_MIN, TEMP_SAFE_MAX = 40.0, 80.0     # deg C
VIBRATION_SAFE_MAX = 5.0                       # mm/s (RMS velocity)

DATA_LOG_FILE = "sensor_data_log.csv"
ALERT_LOG_FILE = "alert_log.csv"
CHART_FILE = "health_monitor_chart.png"
SUMMARY_FILE = "summary_report.txt"


# ---------------------------------------------------------------------
# Data simulation
# ---------------------------------------------------------------------
def simulate_reading(index):
    """
    Generate one simulated sensor reading. Most readings are in the
    normal operating range; occasional spikes are injected to mimic
    a machine drifting toward a fault condition.
    """
    # Base "healthy" behaviour
    temperature = random.gauss(60, 5)       # centred around 60C
    vibration = random.gauss(2.0, 0.6)      # centred around 2 mm/s

    # Inject occasional anomalies (~8% of readings) to simulate
    # a developing fault (bearing wear, overheating, etc.)
    if random.random() < 0.08:
        temperature += random.uniform(15, 30)
        vibration += random.uniform(3, 6)

    return round(temperature, 2), round(vibration, 2)


# ---------------------------------------------------------------------
# Threshold / rule-based fault check
# ---------------------------------------------------------------------
def check_thresholds(temperature, vibration):
    """
    Return a list of triggered alert reasons for a single reading.
    Empty list = reading is within normal operating limits.
    """
    reasons = []
    if temperature > TEMP_SAFE_MAX:
        reasons.append(f"High temperature ({temperature} C > {TEMP_SAFE_MAX} C)")
    elif temperature < TEMP_SAFE_MIN:
        reasons.append(f"Low temperature ({temperature} C < {TEMP_SAFE_MIN} C)")

    if vibration > VIBRATION_SAFE_MAX:
        reasons.append(f"High vibration ({vibration} mm/s > {VIBRATION_SAFE_MAX} mm/s)")

    return reasons


# ---------------------------------------------------------------------
# Main monitoring loop
# ---------------------------------------------------------------------
def run_monitor():
    start_time = datetime.now()
    all_rows = []
    alert_rows = []

    for i in range(NUM_READINGS):
        timestamp = start_time + timedelta(seconds=i * READING_INTERVAL_SEC)
        temperature, vibration = simulate_reading(i)
        reasons = check_thresholds(temperature, vibration)
        status = "ALERT" if reasons else "OK"

        row = {
            "reading_id": i + 1,
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "temperature_C": temperature,
            "vibration_mm_s": vibration,
            "status": status,
        }
        all_rows.append(row)

        if reasons:
            alert_row = dict(row)
            alert_row["reason"] = "; ".join(reasons)
            alert_rows.append(alert_row)
            print(f"[ALERT] Reading {i + 1} @ {row['timestamp']}: {alert_row['reason']}")

    return all_rows, alert_rows


# ---------------------------------------------------------------------
# Output: CSV logs
# ---------------------------------------------------------------------
def write_csv_logs(all_rows, alert_rows):
    with open(DATA_LOG_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["reading_id", "timestamp", "temperature_C", "vibration_mm_s", "status"])
        writer.writeheader()
        writer.writerows(all_rows)

    with open(ALERT_LOG_FILE, "w", newline="") as f:
        fieldnames = ["reading_id", "timestamp", "temperature_C", "vibration_mm_s", "status", "reason"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(alert_rows)


# ---------------------------------------------------------------------
# Output: chart
# ---------------------------------------------------------------------
def plot_readings(all_rows):
    ids = [r["reading_id"] for r in all_rows]
    temps = [r["temperature_C"] for r in all_rows]
    vibs = [r["vibration_mm_s"] for r in all_rows]
    alert_ids = [r["reading_id"] for r in all_rows if r["status"] == "ALERT"]
    alert_temps = [r["temperature_C"] for r in all_rows if r["status"] == "ALERT"]
    alert_vibs = [r["vibration_mm_s"] for r in all_rows if r["status"] == "ALERT"]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)

    ax1.plot(ids, temps, color="#2a6fdb", linewidth=1, label="Temperature (C)")
    ax1.axhline(TEMP_SAFE_MAX, color="red", linestyle="--", linewidth=1, label="Upper safe limit")
    ax1.axhline(TEMP_SAFE_MIN, color="orange", linestyle="--", linewidth=1, label="Lower safe limit")
    ax1.scatter(alert_ids, alert_temps, color="red", zorder=5, label="Alert")
    ax1.set_ylabel("Temperature (C)")
    ax1.set_title("Machine Health Monitor — Simulated Sensor Readings")
    ax1.legend(loc="upper right", fontsize=8)

    ax2.plot(ids, vibs, color="#2ea043", linewidth=1, label="Vibration (mm/s)")
    ax2.axhline(VIBRATION_SAFE_MAX, color="red", linestyle="--", linewidth=1, label="Safe limit")
    ax2.scatter(alert_ids, alert_vibs, color="red", zorder=5, label="Alert")
    ax2.set_ylabel("Vibration (mm/s)")
    ax2.set_xlabel("Reading #")
    ax2.legend(loc="upper right", fontsize=8)

    fig.tight_layout()
    fig.savefig(CHART_FILE, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------
# Output: summary report
# ---------------------------------------------------------------------
def write_summary(all_rows, alert_rows):
    total = len(all_rows)
    n_alerts = len(alert_rows)
    pct_alerts = (n_alerts / total * 100) if total else 0

    temps = [r["temperature_C"] for r in all_rows]
    vibs = [r["vibration_mm_s"] for r in all_rows]

    lines = [
        "SIMPLE MACHINE HEALTH MONITOR — SUMMARY REPORT",
        "=" * 50,
        f"Total readings simulated : {total}",
        f"Readings flagged as ALERT: {n_alerts} ({pct_alerts:.1f}%)",
        "",
        f"Temperature  -> min: {min(temps):.2f} C, max: {max(temps):.2f} C, avg: {sum(temps)/total:.2f} C",
        f"Vibration    -> min: {min(vibs):.2f} mm/s, max: {max(vibs):.2f} mm/s, avg: {sum(vibs)/total:.2f} mm/s",
        "",
        f"Thresholds used: temperature {TEMP_SAFE_MIN}-{TEMP_SAFE_MAX} C, vibration <= {VIBRATION_SAFE_MAX} mm/s",
        "",
        "Files generated:",
        f"  - {DATA_LOG_FILE}  (all readings)",
        f"  - {ALERT_LOG_FILE} (only flagged readings, with reason)",
        f"  - {CHART_FILE}     (visual chart of readings + alerts)",
    ]
    text = "\n".join(lines)
    with open(SUMMARY_FILE, "w") as f:
        f.write(text)
    print("\n" + text)


if __name__ == "__main__":
    random.seed(42)  # reproducible results for the report
    all_rows, alert_rows = run_monitor()
    write_csv_logs(all_rows, alert_rows)
    plot_readings(all_rows)
    write_summary(all_rows, alert_rows)
