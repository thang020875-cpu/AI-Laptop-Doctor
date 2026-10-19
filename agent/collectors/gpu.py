import subprocess
from datetime import datetime


def collect_gpu():

    report = {
        "available": False,
        "gpus": [],
        "timestamp": datetime.now().isoformat()
    }

    try:

        command = [
            "nvidia-smi",
            "--query-gpu=name,memory.total,temperature.gpu,driver_version",
            "--format=csv,noheader,nounits"
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:

            report["error"] = (
                result.stderr.strip()
                or "nvidia-smi failed"
            )

            return report

        lines = result.stdout.strip().splitlines()

        for line in lines:

            parts = [
                item.strip()
                for item in line.split(",")
            ]

            if len(parts) != 4:
                continue

            name = parts[0]

            # VRAM
            try:
                vram_mb = float(parts[1])
                vram_gb = round(
                    vram_mb / 1024,
                    2
                )
            except (ValueError, TypeError):
                vram_gb = None

            # GPU temperature
            try:
                temperature_c = float(parts[2])
            except (ValueError, TypeError):
                temperature_c = None

            # Driver
            driver_version = parts[3]

            gpu_info = {
                "name": name,
                "vram_gb": vram_gb,
                "driver_version": driver_version,
                "temperature_c": temperature_c,
                "temperature_available": (
                    temperature_c is not None
                ),
                "temperature_source": "nvidia-smi",
                "video_mode": None,
                "timestamp": datetime.now().isoformat()
            }

            report["gpus"].append(gpu_info)

        if report["gpus"]:
            report["available"] = True

        return report

    except FileNotFoundError:

        report["error"] = (
            "nvidia-smi not found"
        )

        return report

    except subprocess.TimeoutExpired:

        report["error"] = (
            "nvidia-smi timed out"
        )

        return report

    except Exception as error:

        report["error"] = str(error)

        return report