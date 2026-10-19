import json
import requests

from schema import create_system_report

from collectors.system import collect_system
from collectors.cpu import collect_cpu
from collectors.memory import collect_memory
from collectors.disk import collect_disk
from collectors.gpu import collect_gpu
from collectors.battery import collect_battery
from collectors.temperature import collect_temperature
from collectors.network import collect_network

from diagnostic import diagnose


# =========================================================
# CONFIGURATION
# =========================================================

BACKEND_URL = "http://127.0.0.1:8000/agent/report"


# =========================================================
# COLLECT REPORT
# =========================================================

def collect_report():

    system = collect_system()
    cpu = collect_cpu()
    memory = collect_memory()
    disk = collect_disk()
    gpu = collect_gpu()
    battery = collect_battery()
    temperature = collect_temperature()
    network = collect_network()

    return create_system_report(
        system=system,
        cpu=cpu,
        memory=memory,
        disk=disk,
        gpu=gpu,
        battery=battery,
        temperature=temperature,
        network=network
    )


# =========================================================
# SAVE REPORT
# =========================================================

def save_report(report):

    with open(
        "system_report.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )


# =========================================================
# SEND REPORT TO BACKEND
# =========================================================

def send_report(report):

    try:

        response = requests.post(
            BACKEND_URL,
            json=report,
            timeout=10
        )

        return response

    except requests.RequestException as error:

        print("\n[ERROR] Cannot connect to backend.")
        print(error)

        return None


# =========================================================
# SYSTEM INFORMATION
# =========================================================

def print_system_info(report):

    system = report.get(
        "system",
        {}
    )

    hardware = report.get(
        "hardware",
        {}
    )

    cpu = hardware.get(
        "cpu",
        {}
    )

    memory = hardware.get(
        "memory",
        {}
    )

    disk = hardware.get(
        "disk",
        {}
    )

    print()
    print("=" * 65)
    print("                AI LAPTOP DOCTOR")
    print("=" * 65)

    print(
        f" Computer : "
        f"{system.get('hostname', 'Unknown')}"
    )

    print(
        f" OS       : "
        f"{system.get('os', 'Unknown')}"
    )

    print(
        f" Version  : "
        f"{system.get('os_version', 'Unknown')}"
    )

    print(
        f" Arch     : "
        f"{system.get('architecture', 'Unknown')}"
    )

    print("-" * 65)

    # -----------------------------------------------------
    # CPU
    # -----------------------------------------------------

    print(" CPU")

    print(
        f"   Model          : "
        f"{cpu.get('name', 'Unknown')}"
    )

    print(
        f"   Physical cores : "
        f"{cpu.get('physical_cores', 'N/A')}"
    )

    print(
        f"   Logical cores  : "
        f"{cpu.get('logical_cores', 'N/A')}"
    )

    print(
        f"   Usage          : "
        f"{cpu.get('usage_percent', 'N/A')}%"
    )

    # -----------------------------------------------------
    # MEMORY
    # -----------------------------------------------------

    print()
    print(" MEMORY")

    print(
        f"   Total          : "
        f"{memory.get('total_gb', 'N/A')} GB"
    )

    print(
        f"   Used           : "
        f"{memory.get('used_gb', 'N/A')} GB"
    )

    print(
        f"   Available      : "
        f"{memory.get('available_gb', 'N/A')} GB"
    )

    print(
        f"   Usage          : "
        f"{memory.get('usage_percent', 'N/A')}%"
    )

    # -----------------------------------------------------
    # DISK
    # -----------------------------------------------------

    print()
    print(" DISK")

    print(
        f"   Total          : "
        f"{disk.get('total_gb', 'N/A')} GB"
    )

    print(
        f"   Used           : "
        f"{disk.get('used_gb', 'N/A')} GB"
    )

    print(
        f"   Free           : "
        f"{disk.get('free_gb', 'N/A')} GB"
    )

    print(
        f"   Usage          : "
        f"{disk.get('usage_percent', 'N/A')}%"
    )


# =========================================================
# GPU INFORMATION
# =========================================================

def print_gpu_info(report):

    hardware = report.get(
        "hardware",
        {}
    )

    gpu = hardware.get(
        "gpu",
        {}
    )

    print()
    print("-" * 65)
    print(" GPU")

    if not gpu.get("available"):

        print(
            "   Status         : "
            "Information unavailable"
        )

        if gpu.get("error"):

            print(
                f"   Error          : "
                f"{gpu.get('error')}"
            )

        return

    gpus = gpu.get(
        "gpus",
        []
    )

    if not gpus:

        print(
            "   Status         : "
            "No GPU detected"
        )

        return

    for index, item in enumerate(
        gpus,
        start=1
    ):

        print(
            f"   GPU {index}"
        )

        print(
            f"      Name         : "
            f"{item.get('name', 'Unknown')}"
        )

        print(
            f"      VRAM         : "
            f"{item.get('vram_gb', 'N/A')} GB"
        )

        print(
            f"      Driver       : "
            f"{item.get('driver_version', 'N/A')}"
        )

        temperature = item.get(
            "temperature_c"
        )

        if temperature is not None:

            print(
                f"      Temperature  : "
                f"{temperature} C"
            )

        else:

            print(
                "      Temperature  : N/A"
            )


# =========================================================
# BATTERY INFORMATION
# =========================================================

def print_battery_info(report):

    hardware = report.get(
        "hardware",
        {}
    )

    battery = hardware.get(
        "battery",
        {}
    )

    print()
    print("-" * 65)
    print(" BATTERY")

    if not battery.get("available"):

        print(
            "   Status         : "
            "Information unavailable"
        )

        return

    batteries = battery.get(
        "batteries",
        []
    )

    for item in batteries:

        print(
            f"   Battery        : "
            f"{item.get('name', 'Unknown')}"
        )

        print(
            f"   Charge         : "
            f"{item.get('charge_percent', 'N/A')}%"
        )

        status = item.get(
            "status"
        )

        if status == "Charging":

            status_text = "Charging"

        elif status == "Discharging":

            status_text = "Discharging"

        elif status == "Fully charged":

            status_text = "Fully charged"

        else:

            status_text = str(status)

        print(
            f"   Status         : "
            f"{status_text}"
        )

    # -----------------------------------------------------
    # BATTERY CAPACITY
    # -----------------------------------------------------

    capacity = battery.get(
        "capacity",
        {}
    )

    design = capacity.get(
        "design_mwh"
    )

    full = capacity.get(
        "full_charge_mwh"
    )

    ratio = capacity.get(
        "capacity_ratio_percent"
    )

    print()

    if design is not None:

        print(
            f"   Design capacity: "
            f"{design:,} mWh"
        )

    else:

        print(
            "   Design capacity: N/A"
        )

    if full is not None:

        print(
            f"   Full capacity  : "
            f"{full:,} mWh"
        )

    else:

        print(
            "   Full capacity  : N/A"
        )

    if ratio is not None:

        print(
            f"   Capacity ratio : "
            f"{ratio}%"
        )

    else:

        print(
            "   Capacity ratio : N/A"
        )


# =========================================================
# TEMPERATURE INFORMATION
# =========================================================

def print_temperature_info(report):

    hardware = report.get(
        "hardware",
        {}
    )

    temperature = hardware.get(
        "temperature",
        {}
    )

    print()
    print("-" * 65)
    print(" TEMPERATURE")

    if not temperature.get("available"):

        print(
            "   Status         : "
            "Sensor data unavailable"
        )

        return

    # -----------------------------------------------------
    # CPU TEMPERATURE
    # -----------------------------------------------------

    cpu = temperature.get(
        "cpu",
        {}
    )

    print("   CPU")

    package = cpu.get(
        "package_c"
    )

    core_max = cpu.get(
        "core_max_c"
    )

    core_average = cpu.get(
        "core_average_c"
    )

    if package is not None:

        print(
            f"      Package     : "
            f"{package} C"
        )

    else:

        print(
            "      Package     : N/A"
        )

    if core_max is not None:

        print(
            f"      Core Max    : "
            f"{core_max} C"
        )

    else:

        print(
            "      Core Max    : N/A"
        )

    if core_average is not None:

        print(
            f"      Core Average: "
            f"{core_average} C"
        )

    else:

        print(
            "      Core Average: N/A"
        )

    # -----------------------------------------------------
    # GPU TEMPERATURE
    # -----------------------------------------------------

    print()

    print("   GPU")

    gpu = temperature.get(
        "gpu",
        {}
    )

    gpu_core = gpu.get(
        "core_c"
    )

    gpu_hotspot = gpu.get(
        "hotspot_c"
    )

    if gpu_core is not None:

        print(
            f"      Core        : "
            f"{gpu_core} C"
        )

    else:

        print(
            "      Core        : N/A"
        )

    if gpu_hotspot is not None:

        print(
            f"      Hotspot     : "
            f"{gpu_hotspot} C"
        )

    else:

        print(
            "      Hotspot     : N/A"
        )


# =========================================================
# NETWORK INFORMATION
# =========================================================

def print_network_info(report):

    network = report.get(
        "network",
        {}
    )

    print()
    print("-" * 65)
    print(" NETWORK")

    if not network.get("available"):

        print(
            "   Status         : "
            "Information unavailable"
        )

        return

    # -----------------------------------------------------
    # ADAPTERS
    # -----------------------------------------------------

    adapters = network.get(
        "adapters",
        []
    )

    print("   Adapters")

    for adapter in adapters:

        print(
            f"      {adapter.get('name', 'Unknown')} "
            f": {adapter.get('status', 'Unknown')}"
        )

        print(
            f"         Description : "
            f"{adapter.get('description', 'N/A')}"
        )

        print(
            f"         Link speed  : "
            f"{adapter.get('link_speed', 'N/A')}"
        )

    # -----------------------------------------------------
    # IP CONFIGURATION
    # -----------------------------------------------------

    configurations = network.get(
        "configurations",
        []
    )

    print()
    print("   IP configuration")

    for config in configurations:

        interface = config.get(
            "interface",
            "Unknown"
        )

        ips = config.get(
            "ip_addresses",
            []
        )

        gateways = config.get(
            "gateways",
            []
        )

        dns = config.get(
            "dns_servers",
            []
        )

        print(
            f"      Interface : "
            f"{interface}"
        )

        print(
            f"      IP        : "
            f"{ips}"
        )

        print(
            f"      Gateway   : "
            f"{gateways}"
        )

        print(
            f"      DNS       : "
            f"{dns}"
        )

    # -----------------------------------------------------
    # CONNECTIVITY
    # -----------------------------------------------------

    tests = network.get(
        "tests",
        {}
    )

    print()
    print("   Connectivity")

    print(
        f"      Internet ping : "
        f"{tests.get('internet_ping')}"
    )

    print(
        f"      DNS resolution: "
        f"{tests.get('dns_resolution')}"
    )

    print(
        f"      Socket test   : "
        f"{tests.get('internet_socket')}"
    )


# =========================================================
# DIAGNOSIS
# =========================================================

def print_diagnosis(diagnosis):

    if not diagnosis:

        print(
            " Diagnosis data unavailable."
        )

        return

    status = diagnosis.get(
        "status",
        "UNKNOWN"
    )

    issue_count = diagnosis.get(
        "issue_count",
        0
    )

    issues = diagnosis.get(
        "issues",
        []
    )

    recommendations = diagnosis.get(
        "recommendations",
        []
    )

    print()
    print("=" * 65)
    print("                    DIAGNOSIS")
    print("=" * 65)

    print(
        f" Overall status : "
        f"{status}"
    )

    print(
        f" Issue count    : "
        f"{issue_count}"
    )

    # -----------------------------------------------------
    # ISSUES
    # -----------------------------------------------------

    if issues:

        print()
        print(" Issues:")

        for issue in issues:

            print()
            print(
                "  ----------------------------------------"
            )

            print(
                f"  ID         : "
                f"{issue.get('id', 'N/A')}"
            )

            print(
                f"  Category   : "
                f"{issue.get('category', 'N/A')}"
            )

            print(
                f"  Title      : "
                f"{issue.get('title', 'N/A')}"
            )

            print(
                f"  Severity   : "
                f"{issue.get('severity', 'N/A')}"
            )

            print(
                f"  Confidence : "
                f"{issue.get('confidence', 'N/A')}"
            )

            print(
                f"  Reason     : "
                f"{issue.get('reason', 'N/A')}"
            )

            print(
                f"  Action     : Level "
                f"{issue.get('action_level', 'N/A')}"
            )

            possible_causes = issue.get(
                "possible_causes",
                []
            )

            if possible_causes:

                print(
                    "  Possible causes:"
                )

                for cause in possible_causes:

                    print(
                        f"     - {cause}"
                    )

    else:

        print()
        print(
            " [OK] Không phát hiện vấn đề "
            "theo các rule hiện tại."
        )

    # -----------------------------------------------------
    # RECOMMENDATIONS
    # -----------------------------------------------------

    if recommendations:

        print()
        print(
            " Recommendations:"
        )

        for recommendation in recommendations:

            print(
                f"  - {recommendation}"
            )

    else:

        print()
        print(
            " Recommendations : None"
        )

    print()
    print("=" * 65)


# =========================================================
# MAIN PROGRAM
# =========================================================

if __name__ == "__main__":

    print()
    print("=" * 65)
    print("              AI LAPTOP DOCTOR AGENT")
    print("=" * 65)

    # =====================================================
    # STEP 1 - COLLECT
    # =====================================================

    print(
        "\n[1/4] Collecting system information..."
    )

    report = collect_report()

    # =====================================================
    # STEP 2 - DIAGNOSIS
    # =====================================================

    print(
        "[2/4] Analyzing system..."
    )

    diagnosis = diagnose(
        report
    )

    report["diagnosis"] = diagnosis

    print(
        "[OK] Diagnostic analysis completed."
    )

    # =====================================================
    # STEP 3 - SAVE
    # =====================================================

    print(
        "\n[3/4] Saving system report..."
    )

    save_report(
        report
    )

    print(
        "[OK] system_report.json updated."
    )

    # =====================================================
    # DISPLAY SYSTEM INFORMATION
    # =====================================================

    print_system_info(
        report
    )

    print_gpu_info(
        report
    )

    print_battery_info(
        report
    )

    print_temperature_info(
        report
    )

    print_network_info(
        report
    )

    # =====================================================
    # STEP 4 - SEND BACKEND
    # =====================================================

    print()

    print(
        "-" * 65
    )

    print(
        "[4/4] Sending report to backend..."
    )

    response = send_report(
        report
    )

    if response:

        if response.status_code == 200:

            print(
                "[OK] Report sent successfully."
            )

        else:

            print(
                f"[WARNING] Backend returned HTTP "
                f"{response.status_code}"
            )

    else:

        print(
            "[ERROR] Report could not be sent."
        )

    # =====================================================
    # SHOW DIAGNOSIS
    # =====================================================

    print(
        "\n[DIAGNOSIS]"
    )

    print_diagnosis(
        diagnosis
    )

    # =====================================================
    # COMPLETE
    # =====================================================

    print()

    print(
        "=" * 65
    )

    print(
        "                    SCAN COMPLETE"
    )

    print(
        "=" * 65
    )

    print()