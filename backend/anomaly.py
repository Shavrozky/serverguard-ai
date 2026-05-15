from statistics import mean, stdev


Z_SCORE_THRESHOLD = 2.0
MIN_DATA_POINTS = 10


def calculate_z_score(value: float, values: list[float]) -> float:
    if len(values) < MIN_DATA_POINTS:
        return 0.0

    average = mean(values)
    deviation = stdev(values)

    if deviation == 0:
        return 0.0

    return abs((value - average) / deviation)


def detect_anomalies(metrics):
    if len(metrics) < MIN_DATA_POINTS:
        return {
            "status": "insufficient_data",
            "message": f"Need at least {MIN_DATA_POINTS} data points to detect anomalies",
            "anomalies": [],
        }

    latest = metrics[-1]

    cpu_values = [metric.cpu_percent for metric in metrics]
    ram_values = [metric.ram_percent for metric in metrics]
    disk_values = [metric.disk_percent for metric in metrics]

    checks = [
        {
            "name": "CPU",
            "value": latest.cpu_percent,
            "values": cpu_values,
        },
        {
            "name": "RAM",
            "value": latest.ram_percent,
            "values": ram_values,
        },
        {
            "name": "Disk",
            "value": latest.disk_percent,
            "values": disk_values,
        },
    ]

    anomalies = []

    for check in checks:
        z_score = calculate_z_score(check["value"], check["values"])

        if z_score >= Z_SCORE_THRESHOLD:
            anomalies.append({
                "metric": check["name"],
                "value": check["value"],
                "z_score": round(z_score, 2),
                "message": f"{check['name']} anomaly detected with Z-score {round(z_score, 2)}",
            })

    if anomalies:
        return {
            "status": "anomaly_detected",
            "message": "Anomaly detected in latest metrics",
            "anomalies": anomalies,
        }

    return {
        "status": "normal",
        "message": "No anomaly detected",
        "anomalies": [],
    }