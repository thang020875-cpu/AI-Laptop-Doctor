# =========================================================
# AI LAPTOP DOCTOR - SCAN SERVICE
# Version: 0.7.0
# =========================================================

import json
from pathlib import Path

from collectors.cpu import collect_cpu
from collectors.memory import collect_memory
from collectors.disk import collect_disk
from collectors.gpu import collect_gpu
from collectors.battery import collect_battery
from collectors.temperature import collect_temperature
from collectors.network import collect_network
from collectors.system import collect_system

from schema import create_system_report
from diagnostic import diagnose


REPORT_PATH = Path(__file__).parent / "system_report.json"


def run_scan():

    print("[SCAN] Collecting system information...")

    system = collect_system()
    cpu = collect_cpu()
    memory = collect_memory()
    disk = collect_disk()
    gpu = collect_gpu()
    battery = collect_battery()
    temperature = collect_temperature()
    network = collect_network()

    report = create_system_report(
        system=system,
        cpu=cpu,
        memory=memory,
        disk=disk,
        gpu=gpu,
        battery=battery,
        temperature=temperature,
        network=network
    )

    print("[SCAN] Running diagnostic...")

    diagnosis = diagnose(report)

    report["diagnosis"] = diagnosis

    with open(
        REPORT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=4
        )

    print(
        "[OK] Scan completed."
    )

    return report


if __name__ == "__main__":

    result = run_scan()

    print()
    print("=" * 65)
    print("AI LAPTOP DOCTOR SCAN")
    print("=" * 65)

    print(
        "Status:",
        result.get(
            "diagnosis",
            {}
        ).get(
            "status"
        )
    )

    print(
        "Issues:",
        result.get(
            "diagnosis",
            {}
        ).get(
            "issue_count",
            0
        )
    )