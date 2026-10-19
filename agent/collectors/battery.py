import subprocess
import re
from datetime import datetime
from pathlib import Path


def collect_battery():

    report = {
        "available": False,

        "batteries": [],

        "capacity": {
            "design_mwh": None,
            "full_charge_mwh": None,
            "capacity_ratio_percent": None
        },

        "cycle_count": None,

        "swelling_detected": None,

        "source": "Windows",

        "timestamp": datetime.now().isoformat()
    }

    try:

        # =====================================================
        # 1. THÔNG TIN PIN CƠ BẢN
        # =====================================================

        command = [
            "powershell",
            "-NoProfile",
            "-Command",
            """
            Get-CimInstance Win32_Battery |
            Select-Object Name, BatteryStatus, EstimatedChargeRemaining |
            ConvertTo-Json -Compress
            """
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0 and result.stdout.strip():

            import json

            data = json.loads(result.stdout)

            if not isinstance(data, list):
                data = [data]

            status_map = {
                1: "Discharging",
                2: "Charging",
                3: "Fully charged"
            }

            for battery in data:

                status_code = battery.get(
                    "BatteryStatus"
                )

                report["batteries"].append({
                    "name": battery.get(
                        "Name",
                        "Unknown"
                    ),

                    "charge_percent": battery.get(
                        "EstimatedChargeRemaining"
                    ),

                    "status": status_map.get(
                        status_code,
                        f"Code {status_code}"
                    ),

                    "status_code": status_code
                })

        # =====================================================
        # 2. TẠO WINDOWS BATTERY REPORT
        # =====================================================

        report_path = Path(
            "battery-report.html"
        ).resolve()

        battery_command = [
            "powercfg",
            "/batteryreport",
            "/output",
            str(report_path)
        ]

        battery_result = subprocess.run(
            battery_command,
            capture_output=True,
            text=True,
            timeout=15
        )

        # =====================================================
        # 3. ĐỌC BATTERY REPORT
        # =====================================================

        if report_path.exists():

            html = report_path.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            # -------------------------------------------------
            # Design Capacity
            # -------------------------------------------------

            design_match = re.search(
                r"DESIGN CAPACITY.*?([\d,]+)\s*mWh",
                html,
                re.IGNORECASE |
                re.DOTALL
            )

            # -------------------------------------------------
            # Full Charge Capacity
            # -------------------------------------------------

            full_match = re.search(
                r"FULL CHARGE CAPACITY.*?([\d,]+)\s*mWh",
                html,
                re.IGNORECASE |
                re.DOTALL
            )

            if design_match:

                design = int(
                    design_match.group(1)
                    .replace(",", "")
                )

                report["capacity"][
                    "design_mwh"
                ] = design

            if full_match:

                full = int(
                    full_match.group(1)
                    .replace(",", "")
                )

                report["capacity"][
                    "full_charge_mwh"
                ] = full

            # -------------------------------------------------
            # Capacity ratio
            # -------------------------------------------------

            design = report["capacity"][
                "design_mwh"
            ]

            full = report["capacity"][
                "full_charge_mwh"
            ]

            if design and full:

                report["capacity"][
                    "capacity_ratio_percent"
                ] = round(
                    (full / design) * 100,
                    2
                )

            # -------------------------------------------------
            # Xóa file tạm
            # -------------------------------------------------

            try:
                report_path.unlink()
            except Exception:
                pass

        # =====================================================
        # 4. XÁC ĐỊNH AVAILABLE
        # =====================================================

        if (
            report["batteries"]
            or report["capacity"]["design_mwh"] is not None
            or report["capacity"]["full_charge_mwh"] is not None
        ):

            report["available"] = True

        return report

    except subprocess.TimeoutExpired:

        report["error"] = (
            "Battery information request timed out."
        )

        return report

    except Exception as error:

        report["error"] = str(error)

        return report