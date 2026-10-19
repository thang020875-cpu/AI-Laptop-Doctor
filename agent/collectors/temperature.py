import requests
from datetime import datetime


LHM_URL = "http://127.0.0.1:8085/data.json"


def collect_temperature():

    report = {
        "available": False,
        "cpu": {
            "package_c": None,
            "core_max_c": None,
            "core_average_c": None
        },
        "gpu": {
            "core_c": None,
            "hotspot_c": None
        },
        "source": "LibreHardwareMonitor",
        "timestamp": datetime.now().isoformat()
    }

    try:
        response = requests.get(
            LHM_URL,
            timeout=5
        )

        response.raise_for_status()

        data = response.json()

        def to_float(value):

            if value is None:
                return None

            try:
                return float(
                    str(value)
                    .replace("°C", "")
                    .strip()
                )

            except (ValueError, TypeError):
                return None

        def scan_node(node, path=""):

            if not isinstance(node, dict):
                return

            name = str(
                node.get("Text", "")
            ).strip()

            current_path = (
                f"{path} / {name}"
                if path
                else name
            )

            value = node.get("Value")

            if value is not None:

                value_text = str(value)

                if "°C" in value_text:

                    temperature = to_float(
                        value_text
                    )

                    if temperature is not None:

                        name_lower = name.lower()
                        path_lower = current_path.lower()

                        # =========================
                        # CPU
                        # =========================

                        if (
                            name_lower == "cpu package"
                            or "cpu package" in name_lower
                        ):
                            report["cpu"]["package_c"] = temperature

                        elif (
                            name_lower == "core max"
                            or "core max" in name_lower
                        ):
                            report["cpu"]["core_max_c"] = temperature

                        elif (
                            name_lower == "core average"
                            or "core average" in name_lower
                        ):
                            report["cpu"]["core_average_c"] = temperature

                        # =========================
                        # GPU
                        # =========================

                        elif (
                            "gpu core" in name_lower
                            and "hotspot" not in name_lower
                        ):
                            report["gpu"]["core_c"] = temperature

                        elif "hotspot" in name_lower:
                            report["gpu"]["hotspot_c"] = temperature

            children = node.get(
                "Children",
                []
            )

            if isinstance(children, list):

                for child in children:

                    scan_node(
                        child,
                        current_path
                    )

        scan_node(data)

        # Có ít nhất một sensor nhiệt độ
        if any([
            report["cpu"]["package_c"] is not None,
            report["cpu"]["core_max_c"] is not None,
            report["cpu"]["core_average_c"] is not None,
            report["gpu"]["core_c"] is not None,
            report["gpu"]["hotspot_c"] is not None
        ]):

            report["available"] = True

        return report

    except requests.RequestException as error:

        report["error"] = (
            "Cannot connect to LibreHardwareMonitor: "
            + str(error)
        )

        return report

    except ValueError as error:

        report["error"] = (
            "Invalid JSON from LibreHardwareMonitor: "
            + str(error)
        )

        return report

    except Exception as error:

        report["error"] = str(error)

        return report