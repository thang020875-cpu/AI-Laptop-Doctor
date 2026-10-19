def analyze_report(report):
    findings = []
    recommendations = []

    overall_status = "NORMAL"

    # =========================
    # 1. PHÂN TÍCH CPU
    # =========================

    cpu = report.get("cpu", {})
    cpu_usage = cpu.get("usage_percent")

    if cpu_usage is not None:

        if cpu_usage >= 90:
            findings.append({
                "component": "CPU",
                "status": "WARNING",
                "message": f"CPU usage is high at {cpu_usage}%."
            })

            recommendations.append(
                "Check which processes are using high CPU."
            )

            overall_status = "WARNING"

        else:
            findings.append({
                "component": "CPU",
                "status": "NORMAL",
                "message": f"CPU usage is normal at {cpu_usage}%."
            })

    # =========================
    # 2. PHÂN TÍCH RAM
    # =========================

    memory = report.get("memory", {})
    memory_usage = memory.get("usage_percent")

    if memory_usage is not None:

        if memory_usage >= 90:

            findings.append({
                "component": "RAM",
                "status": "WARNING",
                "message": f"Memory usage is very high at {memory_usage}%."
            })

            recommendations.append(
                "Close unnecessary applications and check background processes."
            )

            overall_status = "WARNING"

        elif memory_usage >= 80:

            findings.append({
                "component": "RAM",
                "status": "WARNING",
                "message": f"Memory usage is relatively high at {memory_usage}%."
            })

            recommendations.append(
                "Monitor memory usage and close unnecessary applications."
            )

            if overall_status == "NORMAL":
                overall_status = "WARNING"

        else:

            findings.append({
                "component": "RAM",
                "status": "NORMAL",
                "message": f"Memory usage is normal at {memory_usage}%."
            })

    # =========================
    # 3. PHÂN TÍCH DISK
    # =========================

    disk = report.get("disk", {})
    disk_usage = disk.get("usage_percent")
    disk_free = disk.get("free_gb")

    if disk_usage is not None:

        if disk_usage >= 90:

            findings.append({
                "component": "DISK",
                "status": "WARNING",
                "message": f"Disk usage is very high at {disk_usage}%."
            })

            recommendations.append(
                "Free up storage space and remove unnecessary files."
            )

            overall_status = "WARNING"

        else:

            findings.append({
                "component": "DISK",
                "status": "NORMAL",
                "message": f"Disk usage is normal at {disk_usage}%."
            })

    # =========================
    # 4. KẾT QUẢ TỔNG QUÁT
    # =========================
    # =========================
    # GPU
    # =========================

    gpu = report.get("gpu", {})

    if gpu.get("available"):
        gpus = gpu.get("gpus", [])

        for item in gpus:
            gpu_name = item.get("name")
            vram_gb = item.get("vram_gb")
            driver_version = item.get("driver_version")
            video_mode = item.get("video_mode")

            findings.append({
                "component": "GPU",
                "status": "NORMAL",
                "message": (
                    f"GPU detected: {gpu_name}. "
                    f"VRAM: {vram_gb} GB. "
                    f"Driver: {driver_version}. "
                    f"Display mode: {video_mode}."
                )
            })
                # =========================
    # BATTERY
    # =========================

    battery = report.get("battery", {})

    if battery.get("available"):
        batteries = battery.get("batteries", [])

        for item in batteries:
            battery_name = item.get("name")
            charge = item.get("charge_percent")
            status = item.get("status")
            runtime = item.get("estimated_runtime_minutes")

            findings.append({
                "component": "BATTERY",
                "status": "NORMAL",
                "message": (
                    f"Battery: {battery_name}. "
                    f"Charge: {charge}%. "
                    f"Status code: {status}. "
                    f"Estimated runtime: {runtime} minutes."
                )
            })
    return {
        "overall_status": overall_status,
        "findings": findings,
        "recommendations": recommendations
    }