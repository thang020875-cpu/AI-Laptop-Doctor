# =========================================================
# AI LAPTOP DOCTOR - PROCESS MONITOR
# Version: 0.6.1
# =========================================================

import os
import time
from datetime import datetime

import psutil


# =========================================================
# CONFIGURATION
# =========================================================

SYSTEM_PROCESSES = {
    "system idle process",
    "system"
}

# Các process mà AI Laptop Doctor có thể tự tạo ra
SELF_PROCESS_NAMES = {
    "python.exe",
    "pythonw.exe"
}


# =========================================================
# HELPER
# =========================================================

def get_logical_cpu_count():
    """
    Lấy số logical CPU của máy.

    Ví dụ:
        12 logical CPUs
    """

    count = psutil.cpu_count(
        logical=True
    )

    if not count:
        return 1

    return count


def is_system_process(name):
    """
    Kiểm tra process hệ thống.
    """

    if not name:
        return False

    return (
        name.lower()
        in SYSTEM_PROCESSES
    )


def is_self_process(name):
    """
    Kiểm tra process có thể thuộc
    AI Laptop Doctor.

    Lưu ý:
    Python.exe có thể là chương trình khác.
    Vì vậy đây chỉ là cờ đánh dấu,
    không tự kết luận Python là AI Laptop Doctor.
    """

    if not name:
        return False

    return (
        name.lower()
        in SELF_PROCESS_NAMES
    )


# =========================================================
# COLLECT ONE PROCESS SAMPLE
# =========================================================

def collect_process_sample(
    top_n=10
):
    """
    Thu thập thông tin process.

    Chế độ:
        READ ONLY

    Không:
        - kill process
        - terminate process
        - đóng ứng dụng
        - thay đổi hệ thống
    """

    processes = []

    logical_cpu_count = (
        get_logical_cpu_count()
    )

    # -----------------------------------------------------
    # CPU BASELINE
    # -----------------------------------------------------

    for process in psutil.process_iter(
        [
            "pid",
            "name"
        ]
    ):

        try:

            # Khởi tạo bộ đếm CPU
            process.cpu_percent(
                interval=None
            )

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):

            continue

    # -----------------------------------------------------
    # Wait for CPU measurement
    # -----------------------------------------------------

    time.sleep(1)

    # -----------------------------------------------------
    # Collect process information
    # -----------------------------------------------------

    for process in psutil.process_iter(
        [
            "pid",
            "name",
            "memory_info"
        ]
    ):

        try:

            pid = process.info.get(
                "pid"
            )

            name = (
                process.info.get(
                    "name"
                )
                or "Unknown"
            )

            # -------------------------------------------------
            # Ignore system processes
            # -------------------------------------------------

            if is_system_process(
                name
            ):
                continue

            # -------------------------------------------------
            # CPU
            # -------------------------------------------------

            cpu_raw = process.cpu_percent(
                interval=None
            )

            # -------------------------------------------------
            # Normalize CPU
            #
            # psutil process CPU có thể >100%
            # trên CPU nhiều core.
            #
            # CPU total = raw / logical CPUs
            # -------------------------------------------------

            cpu_total = (
                cpu_raw
                / logical_cpu_count
            )

            # Giới hạn tối đa 100%
            cpu_total = min(
                cpu_total,
                100.0
            )

            # -------------------------------------------------
            # RAM
            # -------------------------------------------------

            memory_info = (
                process.info.get(
                    "memory_info"
                )
            )

            memory_mb = 0.0

            if memory_info:

                memory_mb = (
                    memory_info.rss
                    / (1024 ** 2)
                )

            # -------------------------------------------------
            # Self process
            # -------------------------------------------------

            self_process = (
                is_self_process(
                    name
                )
            )

            # -------------------------------------------------
            # Build process information
            # -------------------------------------------------

            process_info = {

                "pid":
                    pid,

                "name":
                    name,

                "cpu_percent_raw":
                    round(
                        cpu_raw,
                        2
                    ),

                "cpu_percent_total":
                    round(
                        cpu_total,
                        2
                    ),

                "memory_mb":
                    round(
                        memory_mb,
                        2
                    ),

                "is_system_process":
                    False,

                "is_possible_self_process":
                    self_process,

                "timestamp":
                    datetime.now().isoformat()
            }

            processes.append(
                process_info
            )

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):

            continue

        except Exception:

            continue

    # -----------------------------------------------------
    # Sort by CPU
    # -----------------------------------------------------

    processes_by_cpu = sorted(
        processes,
        key=lambda item: (
            item["cpu_percent_total"],
            item["memory_mb"]
        ),
        reverse=True
    )

    # -----------------------------------------------------
    # Sort by RAM
    # -----------------------------------------------------

    processes_by_memory = sorted(
        processes,
        key=lambda item:
            item["memory_mb"],
        reverse=True
    )

    # -----------------------------------------------------
    # Return
    # -----------------------------------------------------

    return {

        "timestamp":
            datetime.now().isoformat(),

        "logical_cpu_count":
            logical_cpu_count,

        "process_count":
            len(processes),

        "top_cpu_processes":
            processes_by_cpu[:top_n],

        "top_memory_processes":
            processes_by_memory[:top_n]
    }


# =========================================================
# MULTI-SAMPLE PROCESS MONITOR
# =========================================================

def monitor_processes(
    duration_seconds=20,
    interval_seconds=5,
    top_n=10
):
    """
    Theo dõi process trong một khoảng thời gian.

    READ ONLY.
    """

    samples = []

    print()
    print("=" * 70)
    print("                PROCESS MONITOR")
    print("=" * 70)

    print()

    print(
        f"Monitoring time : "
        f"{duration_seconds} seconds"
    )

    print(
        f"Sampling every  : "
        f"{interval_seconds} seconds"
    )

    print(
        f"Logical CPUs    : "
        f"{get_logical_cpu_count()}"
    )

    print()

    print(
        "Mode            : READ ONLY"
    )

    print()

    print(
        "Starting process monitor..."
    )

    start_time = time.time()

    while True:

        elapsed = (
            time.time()
            - start_time
        )

        if elapsed >= duration_seconds:
            break

        sample = collect_process_sample(
            top_n=top_n
        )

        samples.append(
            sample
        )

        # -------------------------------------------------
        # Display
        # -------------------------------------------------

        print()

        print(
            f"[SAMPLE {len(samples):02d}] "
            f"Processes: "
            f"{sample['process_count']}"
        )

        top_cpu = sample.get(
            "top_cpu_processes",
            []
        )

        for process in top_cpu[:5]:

            self_label = ""

            if process.get(
                "is_possible_self_process"
            ):

                self_label = (
                    " [SELF]"
                )

            print(
                f"   PID "
                f"{str(process['pid']):<7} "
                f"{process['name'][:28]:<28} "
                f"CPU "
                f"{process['cpu_percent_total']:>6.2f}% "
                f"RAW "
                f"{process['cpu_percent_raw']:>7.2f}% "
                f"RAM "
                f"{process['memory_mb']:>8.2f} MB"
                f"{self_label}"
            )

        # -------------------------------------------------
        # Remaining time
        # -------------------------------------------------

        remaining = (
            duration_seconds
            - (
                time.time()
                - start_time
            )
        )

        if remaining <= 0:
            break

        time.sleep(
            min(
                interval_seconds,
                remaining
            )
        )

    print()

    print(
        "[OK] Process monitoring completed."
    )

    return samples


# =========================================================
# PROCESS ANALYSIS
# =========================================================

def analyze_process_samples(
    samples,
    cpu_threshold=70,
    memory_threshold_mb=2048
):
    """
    Phân tích process sau khi monitor.

    Không tự động sửa hệ thống.
    """

    if not samples:

        return {

            "status":
                "NO_DATA",

            "sample_count":
                0,

            "findings":
                [],

            "recommendations":
                []
        }

    process_stats = {}

    # =====================================================
    # AGGREGATE DATA
    # =====================================================

    for sample in samples:

        for process in sample.get(
            "top_cpu_processes",
            []
        ):

            name = process.get(
                "name"
            )

            if not name:
                continue

            # ---------------------------------------------
            # Không đưa process của chính hệ thống
            # vào chẩn đoán.
            # ---------------------------------------------

            if is_system_process(
                name
            ):
                continue

            if name not in process_stats:

                process_stats[name] = {

                    "samples":
                        0,

                    "cpu_values":
                        [],

                    "memory_values":
                        [],

                    "pid_values":
                        [],

                    "possible_self":
                        False
                }

            stats = process_stats[
                name
            ]

            stats["samples"] += 1

            stats[
                "cpu_values"
            ].append(
                process.get(
                    "cpu_percent_total",
                    0
                )
            )

            stats[
                "memory_values"
            ].append(
                process.get(
                    "memory_mb",
                    0
                )
            )

            stats[
                "pid_values"
            ].append(
                process.get(
                    "pid"
                )
            )

            if process.get(
                "is_possible_self_process",
                False
            ):

                stats[
                    "possible_self"
                ] = True

    # =====================================================
    # ANALYSIS
    # =====================================================

    findings = []

    recommendations = []

    for name, stats in process_stats.items():

        cpu_values = stats[
            "cpu_values"
        ]

        memory_values = stats[
            "memory_values"
        ]

        if not cpu_values:
            continue

        average_cpu = (
            sum(cpu_values)
            / len(cpu_values)
        )

        maximum_cpu = max(
            cpu_values
        )

        average_memory = (
            sum(memory_values)
            / len(memory_values)
            if memory_values
            else 0
        )

        maximum_memory = (
            max(memory_values)
            if memory_values
            else 0
        )

        # -------------------------------------------------
        # SELF PROCESS
        # -------------------------------------------------

        if stats[
            "possible_self"
        ]:

            # Không đưa AI Laptop Doctor
            # thành nguyên nhân lỗi.

            continue

        # -------------------------------------------------
        # HIGH CPU
        # -------------------------------------------------

        if maximum_cpu >= cpu_threshold:

            findings.append({

                "id":
                    "PM-PROCESS-CPU",

                "cause":
                    f"Process {name} "
                    "có thời điểm sử dụng "
                    "CPU cao",

                "evidence": {

                    "process":
                        name,

                    "average_cpu_percent":
                        round(
                            average_cpu,
                            2
                        ),

                    "maximum_cpu_percent":
                        round(
                            maximum_cpu,
                            2
                        ),

                    "average_memory_mb":
                        round(
                            average_memory,
                            2
                        ),

                    "maximum_memory_mb":
                        round(
                            maximum_memory,
                            2
                        )
                },

                "confidence":
                    0.85
            })

            recommendations.append(
                f"Kiểm tra process "
                f"{name} khi hiện tượng "
                "chậm xảy ra."
            )

        # -------------------------------------------------
        # HIGH RAM
        # -------------------------------------------------

        if maximum_memory >= (
            memory_threshold_mb
        ):

            findings.append({

                "id":
                    "PM-PROCESS-RAM",

                "cause":
                    f"Process {name} "
                    "sử dụng lượng RAM "
                    "đáng kể",

                "evidence": {

                    "process":
                        name,

                    "average_memory_mb":
                        round(
                            average_memory,
                            2
                        ),

                    "maximum_memory_mb":
                        round(
                            maximum_memory,
                            2
                        ),

                    "average_cpu_percent":
                        round(
                            average_cpu,
                            2
                        )
                },

                "confidence":
                    0.80
            })

            recommendations.append(
                f"Kiểm tra mức sử dụng "
                f"RAM của process {name}."
            )

    # =====================================================
    # FINAL STATUS
    # =====================================================

    if findings:

        status = "WARNING"

    else:

        status = "NO_CLEAR_CAUSE"

        recommendations.append(
            "Chưa phát hiện process "
            "sử dụng CPU hoặc RAM "
            "bất thường theo ngưỡng "
            "hiện tại."
        )

    return {

        "status":
            status,

        "sample_count":
            len(samples),

        "findings":
            findings,

        "recommendations":
            recommendations
    }


# =========================================================
# MAIN TEST
# =========================================================

if __name__ == "__main__":

    print()

    print(
        "AI Laptop Doctor "
        "Process Monitor"
    )

    print(
        "READ ONLY MODE"
    )

    samples = monitor_processes(
        duration_seconds=20,
        interval_seconds=5,
        top_n=10
    )

    print()

    print(
        "=" * 70
    )

    print(
        "PROCESS ANALYSIS"
    )

    print(
        "=" * 70
    )

    result = analyze_process_samples(
        samples
    )

    print()

    print(
        f"Status       : "
        f"{result.get('status')}"
    )

    print(
        f"Sample count : "
        f"{result.get('sample_count')}"
    )

    print()

    print(
        "Findings:"
    )

    findings = result.get(
        "findings",
        []
    )

    if findings:

        for index, finding in enumerate(
            findings,
            start=1
        ):

            print()

            print(
                f"[{index}] "
                f"{finding.get('cause')}"
            )

            print(
                f"    Evidence   : "
                f"{finding.get('evidence')}"
            )

            print(
                f"    Confidence : "
                f"{finding.get('confidence')}"
            )

    else:

        print(
            "  - Không phát hiện "
            "process bất thường."
        )

    print()

    print(
        "Recommendations:"
    )

    for recommendation in result.get(
        "recommendations",
        []
    ):

        print(
            f"  - {recommendation}"
        )

    print()

    print(
        "=" * 70
    )

    print(
        "              TEST COMPLETED"
    )

    print(
        "=" * 70
    )