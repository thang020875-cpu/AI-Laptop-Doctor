from collectors.cpu import collect_cpu
from collectors.memory import collect_memory
from collectors.disk import collect_disk
from collectors.gpu import collect_gpu
from collectors.battery import collect_battery
from collectors.temperature import collect_temperature
from collectors.network import collect_network
from collectors.system import collect_system


def run_collectors(collector_names):

    data = {}

    for collector_name in collector_names:

        print()
        print(f"[COLLECT] {collector_name}")

        try:

            if collector_name == "cpu":
                data["cpu"] = collect_cpu()

            elif collector_name == "memory":
                data["memory"] = collect_memory()

            elif collector_name == "disk":
                data["disk"] = collect_disk()

            elif collector_name == "gpu":
                data["gpu"] = collect_gpu()

            elif collector_name == "battery":
                data["battery"] = collect_battery()

            elif collector_name == "temperature":
                data["temperature"] = collect_temperature()

            elif collector_name == "network":
                data["network"] = collect_network()

            elif collector_name == "system":
                data["system"] = collect_system()

            else:
                print(
                    f"[WARNING] Không tìm thấy collector: {collector_name}"
                )
                continue

            print(f"[OK] {collector_name}")

        except Exception as error:

            print(
                f"[ERROR] {collector_name}: {error}"
            )

            data[collector_name] = {
                "available": False,
                "error": str(error)
            }

    return data