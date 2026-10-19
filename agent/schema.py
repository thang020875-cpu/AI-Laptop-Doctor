from datetime import datetime


def create_system_report(
    system,
    cpu,
    memory,
    disk,
    gpu,
    battery,
    temperature,
    network
):

    return {
        "schema_version": "1.0",

        "agent": {
            "name": "AI Laptop Doctor Agent",
            "version": "0.1.0"
        },

        "timestamp": datetime.now().isoformat(),

        "system": system,

        "hardware": {
            "cpu": cpu,
            "memory": memory,
            "disk": disk,
            "gpu": gpu,
            "battery": battery,
            "temperature": temperature
        },

        "network": network
    }