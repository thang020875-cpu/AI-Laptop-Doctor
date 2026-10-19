def diagnose(report):
    print("\n[DEBUG] Diagnostic Engine is running")

    hardware = report.get("hardware", {})

    print("[DEBUG] Hardware keys:", hardware.keys())

    temperature = hardware.get("temperature", {})
    memory = hardware.get("memory", {})
    disk = hardware.get("disk", {})
    battery = hardware.get("battery", {})

    print("[DEBUG] Temperature:", temperature)
    print("[DEBUG] Memory:", memory)
    print("[DEBUG] Disk:", disk)
    print("[DEBUG] Battery:", battery)

    issues = []
    recommendations = []
def diagnose(report):
    print("\n[DEBUG] Diagnostic input:")
    print(report)

    issues = []
    recommendations = []
def diagnose(report):
    issues = []
    recommendations = []

    hardware = report.get("hardware", {})

    # ==================================================
    # TEMPERATURE
    # ==================================================

    temperature = hardware.get("temperature", {})

    cpu = temperature.get("cpu", {})
    gpu = temperature.get("gpu", {})

    cpu_temp = cpu.get("package_c")
    gpu_temp = gpu.get("core_c")

    # CPU >= 95°C
    if cpu_temp is not None and cpu_temp >= 95:

        issues.append({
            "id": "T01",
            "category": "Thermal",
            "title": "Nhiệt độ CPU rất cao",
            "severity": "HIGH",
            "confidence": 0.90,

            "evidence": {
                "cpu_package_temperature_c": cpu_temp
            },

            "possible_causes": [
                "CPU đang chịu tải cao",
                "Hệ thống tản nhiệt hoạt động không hiệu quả",
                "Quạt hoặc khe thông gió có thể bị bụi hoặc cản trở"
            ],

            "reason": (
                f"CPU Package đang ở khoảng {cpu_temp}°C."
            ),

            "action_level": 1
        })

        recommendations.append(
            "Kiểm tra mức tải CPU và hệ thống tản nhiệt."
        )

    # CPU 85-94°C
    elif cpu_temp is not None and cpu_temp >= 85:

        issues.append({
            "id": "T01",
            "category": "Thermal",
            "title": "Nhiệt độ CPU cao",
            "severity": "WARNING",
            "confidence": 0.80,

            "evidence": {
                "cpu_package_temperature_c": cpu_temp
            },

            "possible_causes": [
                "CPU đang hoạt động dưới tải",
                "Hệ thống tản nhiệt có thể đang chịu tải cao",
                "Luồng khí làm mát có thể chưa tối ưu"
            ],

            "reason": (
                f"CPU Package đang ở khoảng {cpu_temp}°C."
            ),

            "action_level": 1
        })

        recommendations.append(
            "Theo dõi nhiệt độ CPU khi máy hoạt động dưới tải."
        )

    # ==================================================
    # GPU TEMPERATURE
    # ==================================================

    if gpu_temp is not None and gpu_temp >= 90:

        issues.append({
            "id": "T02",
            "category": "Thermal",
            "title": "Nhiệt độ GPU cao",
            "severity": "HIGH",
            "confidence": 0.85,

            "evidence": {
                "gpu_core_temperature_c": gpu_temp
            },

            "possible_causes": [
                "GPU đang chịu tải cao",
                "Hệ thống tản nhiệt GPU hoạt động không hiệu quả",
                "Luồng khí làm mát bị hạn chế"
            ],

            "reason": (
                f"GPU Core đang ở khoảng {gpu_temp}°C."
            ),

            "action_level": 1
        })

        recommendations.append(
            "Kiểm tra tải GPU và hệ thống tản nhiệt."
        )

    elif gpu_temp is not None and gpu_temp >= 80:

        issues.append({
            "id": "T02",
            "category": "Thermal",
            "title": "Nhiệt độ GPU cao",
            "severity": "WARNING",
            "confidence": 0.75,

            "evidence": {
                "gpu_core_temperature_c": gpu_temp
            },

            "possible_causes": [
                "GPU đang hoạt động dưới tải",
                "Hệ thống tản nhiệt đang làm việc nhiều"
            ],

            "reason": (
                f"GPU Core đang ở khoảng {gpu_temp}°C."
            ),

            "action_level": 1
        })

        recommendations.append(
            "Theo dõi nhiệt độ GPU trong quá trình sử dụng."
        )

    # ==================================================
    # RAM
    # ==================================================

    memory = hardware.get("memory", {})
    memory_usage = memory.get("usage_percent")

    if memory_usage is not None and memory_usage >= 90:

        issues.append({
            "id": "R01",
            "category": "Memory",
            "title": "RAM đang sử dụng rất cao",
            "severity": "WARNING",
            "confidence": 0.85,

            "evidence": {
                "memory_usage_percent": memory_usage
            },

            "possible_causes": [
                "Có nhiều ứng dụng đang chạy",
                "Ứng dụng sử dụng nhiều RAM",
                "Một tiến trình có thể đang sử dụng RAM bất thường"
            ],

            "reason": (
                f"RAM đang sử dụng khoảng {memory_usage}%."
            ),

            "action_level": 1
        })

        recommendations.append(
            "Kiểm tra Task Manager để xác định ứng dụng sử dụng nhiều RAM."
        )

    # ==================================================
    # DISK
    # ==================================================

    disk = hardware.get("disk", {})
    disk_usage = disk.get("usage_percent")

    if disk_usage is not None and disk_usage >= 90:

        issues.append({
            "id": "D01",
            "category": "Storage",
            "title": "Ổ đĩa gần đầy",
            "severity": "WARNING",
            "confidence": 0.95,

            "evidence": {
                "disk_usage_percent": disk_usage
            },

            "possible_causes": [
                "Dung lượng dữ liệu người dùng lớn",
                "Ứng dụng hoặc file tạm chiếm nhiều dung lượng",
                "Windows Update hoặc dữ liệu hệ thống chiếm dung lượng"
            ],

            "reason": (
                f"Ổ đĩa đang sử dụng khoảng {disk_usage}%."
            ),

            "action_level": 1
        })

        recommendations.append(
            "Kiểm tra dung lượng ổ đĩa trước khi quyết định dọn dẹp."
        )

    # ==================================================
    # BATTERY
    # ==================================================

    battery = hardware.get("battery", {})
    capacity = battery.get("capacity", {})

    ratio = capacity.get("capacity_ratio_percent")

    if ratio is not None and ratio < 70:

        issues.append({
            "id": "B01",
            "category": "Battery",
            "title": "Dung lượng pin có dấu hiệu suy giảm",
            "severity": "WARNING",
            "confidence": 0.85,

            "evidence": {
                "capacity_ratio_percent": ratio
            },

            "possible_causes": [
                "Pin đã trải qua nhiều chu kỳ sử dụng",
                "Dung lượng pin thực tế đã giảm",
                "Pin có thể cần được kiểm tra thực tế"
            ],

            "reason": (
                f"Tỷ lệ dung lượng hiện tại khoảng {ratio}%."
            ),

            "action_level": 1
        })

        recommendations.append(
            "Kiểm tra Battery Report và tình trạng pin thực tế."
        )

    # ==================================================
    # RESULT
    # ==================================================

    if not issues:
        status = "NORMAL"
    else:
        status = "WARNING"

    return {
        "status": status,
        "issue_count": len(issues),
        "issues": issues,
        "recommendations": recommendations
    }