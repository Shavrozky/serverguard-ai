import time
import requests
import psutil

API_URL = "http://localhost:8095/metrics"
INTERVAL_SECONDS = 5


def collect_metrics():
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "ram_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
    }


def send_metrics(metrics):
    response = requests.post(API_URL, json=metrics, timeout=10)
    response.raise_for_status()
    return response.json()


def main():
    print("ServerGuard AI Collector started...")

    while True:
        try:
            metrics = collect_metrics()
            result = send_metrics(metrics)

            print(
                f"Saved metric | "
                f"CPU: {metrics['cpu_percent']}% | "
                f"RAM: {metrics['ram_percent']}% | "
                f"Disk: {metrics['disk_percent']}%"
            )

        except Exception as error:
            print(f"Collector error: {error}")

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()