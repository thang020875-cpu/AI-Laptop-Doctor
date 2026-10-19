# =========================================================
# AI LAPTOP DOCTOR - PERFORMANCE MONITOR
# Version: 0.5.0
# =========================================================

import time
from datetime import datetime

import psutil

from collectors.temperature import collect_temperature


def collect_performance_sample():
    """
    Thu thập một mẫu dữ liệu hiệu năng.
    """

    cpu_usage = psutil.cpu_percent(interval=1)

    memory = psutil.virtual_memory()

    temperature = collect_temperature()

    cpu_temperature = (
        temperature
        .get("cpu", {})
        .get("package_c")
    )

    gpu_temperature = (
        temperature
        .get("gpu", {})
        .get("core_c")
    )

    return {
        "timestamp": datetime.now().isoformat(),

        "cpu_usage_percent": cpu_usage,

        "memory_usage_percent": memory.percent,

        "cpu_temperature_c": cpu_temperature,

        "gpu_temperature_c": gpu_temperature
    }


def monitor_performance(duration_seconds=30, interval_seconds=5):
    """
    Theo dõi hiệu năng trong một khoảng thời gian.

    duration_seconds:
        Tổng thời gian theo dõi.

    interval_seconds:
        Khoảng thời gian giữa các lần lấy mẫu.
    """

    samples = []

    print()
    print("=" * 70)
    print("              PERFORMANCE MONITOR")
    print("=" * 70)

    print()
    print(f"Monitoring time : {duration_seconds} seconds")
    print(f"Sampling every  : {interval_seconds} seconds")

    print()
    print("Starting monitor...")
    print()

    start_time = time.time()

    while True:

        elapsed = time.time() - start_time

        if elapsed >= duration_seconds:
            break

        sample = collect_performance_sample()

        samples.append(sample)

        print(
            f"[SAMPLE {len(samples):02d}] "
            f"CPU: {sample['cpu_usage_percent']}% | "
            f"RAM: {sample['memory_usage_percent']}% | "
            f"CPU Temp: {sample['cpu_temperature_c']}°C | "
            f"GPU Temp: {sample['gpu_temperature_c']}°C"
        )

        remaining = duration_seconds - (time.time() - start_time)

        if remaining <= 0:
            break

        time.sleep(
            min(interval_seconds, remaining)
        )

    print()
    print("[OK] Performance monitoring completed.")

    return samples


def analyze_performance_samples(samples):
    """
    Phân tích các mẫu dữ liệu sau khi monitor.
    """

    if not samples:
        return {
            "status": "NO_DATA",
            "findings": [],
            "recommendations": []
        }

    cpu_values = [
        sample["cpu_usage_percent"]
        for sample in samples
        if sample["cpu_usage_percent"] is not None
    ]

    memory_values = [
        sample["memory_usage_percent"]
        for sample in samples
        if sample["memory_usage_percent"] is not None
    ]

    cpu_temp_values = [
        sample["cpu_temperature_c"]
        for sample in samples
        if sample["cpu_temperature_c"] is not None
    ]

    gpu_temp_values = [
        sample["gpu_temperature_c"]
        for sample in samples
        if sample["gpu_temperature_c"] is not None
    ]

    findings = []
    recommendations = []

    # -----------------------------------------------------
    # CPU
    # -----------------------------------------------------

    if cpu_values:

        cpu_average = sum(cpu_values) / len(cpu_values)
        cpu_max = max(cpu_values)

        if cpu_max >= 90:

            findings.append({
                "id": "PM-CPU-01",
                "cause": "CPU có thời điểm chịu tải rất cao",
                "evidence": {
                    "average_percent": round(cpu_average, 2),
                    "maximum_percent": cpu_max
                },
                "confidence": 0.90
            })

            recommendations.append(
                "Kiểm tra tiến trình sử dụng CPU cao trong Task Manager."
            )

        elif cpu_average >= 70:

            findings.append({
                "id": "PM-CPU-02",
                "cause": "CPU duy trì mức tải tương đối cao",
                "evidence": {
                    "average_percent": round(cpu_average, 2),
                    "maximum_percent": cpu_max
                },
                "confidence": 0.75
            })

            recommendations.append(
                "Theo dõi tiến trình sử dụng CPU trong thời điểm xảy ra lỗi."
            )

    # -----------------------------------------------------
    # MEMORY
    # -----------------------------------------------------

    if memory_values:

        memory_average = sum(memory_values) / len(memory_values)
        memory_max = max(memory_values)

        if memory_max >= 90:

            findings.append({
                "id": "PM-RAM-01",
                "cause": "RAM có thời điểm sử dụng rất cao",
                "evidence": {
                    "average_percent": round(memory_average, 2),
                    "maximum_percent": memory_max
                },
                "confidence": 0.90
            })

            recommendations.append(
                "Kiểm tra ứng dụng hoặc tiến trình sử dụng nhiều RAM."
            )

    # -----------------------------------------------------
    # CPU TEMPERATURE
    # -----------------------------------------------------

    if cpu_temp_values:

        cpu_temp_average = (
            sum(cpu_temp_values)
            / len(cpu_temp_values)
        )

        cpu_temp_max = max(cpu_temp_values)

        if cpu_temp_max >= 95:

            findings.append({
                "id": "PM-TEMP-CPU-01",
                "cause": "CPU đạt nhiệt độ rất cao trong quá trình theo dõi",
                "evidence": {
                    "average_c": round(cpu_temp_average, 2),
                    "maximum_c": cpu_temp_max
                },
                "confidence": 0.90
            })

            recommendations.append(
                "Kiểm tra hệ thống tản nhiệt và luồng khí."
            )

    # -----------------------------------------------------
    # GPU TEMPERATURE
    # -----------------------------------------------------

    if gpu_temp_values:

        gpu_temp_average = (
            sum(gpu_temp_values)
            / len(gpu_temp_values)
        )

        gpu_temp_max = max(gpu_temp_values)

        if gpu_temp_max >= 90:

            findings.append({
                "id": "PM-TEMP-GPU-01",
                "cause": "GPU đạt nhiệt độ cao trong quá trình theo dõi",
                "evidence": {
                    "average_c": round(gpu_temp_average, 2),
                    "maximum_c": gpu_temp_max
                },
                "confidence": 0.85
            })

            recommendations.append(
                "Kiểm tra tải GPU và hệ thống tản nhiệt."
            )

    # -----------------------------------------------------
    # FINAL STATUS
    # -----------------------------------------------------

    if findings:

        status = "WARNING"

    else:

        status = "NO_CLEAR_CAUSE"

        recommendations.append(
            "Chưa phát hiện tải CPU, RAM hoặc nhiệt độ bất thường "
            "trong khoảng thời gian theo dõi."
        )

    return {
        "status": status,
        "sample_count": len(samples),
        "findings": findings,
        "recommendations": recommendations
    }