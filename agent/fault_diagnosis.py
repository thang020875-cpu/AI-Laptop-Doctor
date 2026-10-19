# =========================================================
# AI LAPTOP DOCTOR - FAULT DIAGNOSIS ENGINE
# Version: 0.3.0
# =========================================================


def normalize_text(text):
    if not text:
        return ""

    return str(text).lower().strip()


# =========================================================
# 1. PHÂN LOẠI LỖI
# =========================================================

def classify_fault(user_input):

    text = normalize_text(user_input)

    # Hiệu năng
    performance_keywords = [
        "chậm",
        "lag",
        "giật",
        "treo",
        "đơ",
        "slow",
        "freeze",
        "nặng",
        "khựng"
    ]

    if any(keyword in text for keyword in performance_keywords):

        return {
            "fault_id": "R01",
            "category": "Performance",
            "title": "Hiệu năng hệ thống thấp",
            "required_data": [
                "cpu",
                "memory",
                "disk",
                "temperature"
            ]
        }

    # Nhiệt độ
    thermal_keywords = [
        "nóng",
        "nhiệt độ cao",
        "quá nóng",
        "quạt kêu",
        "quạt to",
        "fan",
        "overheat",
        "overheating"
    ]

    if any(keyword in text for keyword in thermal_keywords):

        return {
            "fault_id": "T01",
            "category": "Thermal",
            "title": "Nhiệt độ hoặc hệ thống tản nhiệt bất thường",
            "required_data": [
                "cpu",
                "temperature",
                "gpu"
            ]
        }

    # Pin
    battery_keywords = [
        "pin",
        "battery",
        "sạc",
        "sạc không vào",
        "tụt pin",
        "pin nhanh hết",
        "không nhận sạc"
    ]

    if any(keyword in text for keyword in battery_keywords):

        return {
            "fault_id": "B01",
            "category": "Battery",
            "title": "Vấn đề về pin hoặc sạc",
            "required_data": [
                "battery"
            ]
        }

    # Network
    network_keywords = [
        "wifi",
        "wi-fi",
        "mạng",
        "internet",
        "không vào mạng",
        "mất mạng",
        "dns",
        "ping"
    ]

    if any(keyword in text for keyword in network_keywords):

        return {
            "fault_id": "N01",
            "category": "Network",
            "title": "Vấn đề kết nối mạng",
            "required_data": [
                "network"
            ]
        }

    # Storage
    storage_keywords = [
        "ổ cứng",
        "ssd",
        "disk",
        "ổ đĩa",
        "đầy ổ",
        "ổ c",
        "không nhận ổ",
        "boot"
    ]

    if any(keyword in text for keyword in storage_keywords):

        return {
            "fault_id": "D01",
            "category": "Storage",
            "title": "Vấn đề về lưu trữ hoặc ổ đĩa",
            "required_data": [
                "disk"
            ]
        }

    # Màn hình
    display_keywords = [
        "màn hình",
        "sọc",
        "sọc màn hình",
        "nhấp nháy",
        "flicker",
        "đen màn hình",
        "display"
    ]

    if any(keyword in text for keyword in display_keywords):

        return {
            "fault_id": "D02",
            "category": "Display",
            "title": "Vấn đề hiển thị",
            "required_data": [
                "gpu",
                "system"
            ]
        }

    # Không xác định
    return {
        "fault_id": "UNKNOWN",
        "category": "Unknown",
        "title": "Chưa xác định được nhóm lỗi",
        "required_data": [
            "system"
        ]
    }


# =========================================================
# 2. CHẨN ĐOÁN HIỆU NĂNG
# =========================================================

def diagnose_performance(report):

    hardware = report.get("hardware", {})

    cpu = hardware.get("cpu", {})
    memory = hardware.get("memory", {})
    disk = hardware.get("disk", {})
    temperature = hardware.get("temperature", {})

    cpu_usage = cpu.get("usage_percent")
    memory_usage = memory.get("usage_percent")
    disk_usage = disk.get("usage_percent")

    cpu_temp = temperature.get("cpu", {}).get("package_c")

    findings = []

    if cpu_usage is not None and cpu_usage >= 90:

        findings.append({
            "cause": "CPU đang chịu tải rất cao",
            "evidence": f"CPU usage {cpu_usage}%",
            "confidence": 0.90
        })

    if memory_usage is not None and memory_usage >= 90:

        findings.append({
            "cause": "RAM đang được sử dụng rất cao",
            "evidence": f"RAM usage {memory_usage}%",
            "confidence": 0.90
        })

    if disk_usage is not None and disk_usage >= 90:

        findings.append({
            "cause": "Ổ đĩa gần đầy",
            "evidence": f"Disk usage {disk_usage}%",
            "confidence": 0.95
        })

    if cpu_temp is not None and cpu_temp >= 90:

        findings.append({
            "cause": "CPU đang có nhiệt độ cao",
            "evidence": f"CPU temperature {cpu_temp}°C",
            "confidence": 0.85
        })

    if findings:

        return {
            "status": "WARNING",
            "severity": "WARNING",
            "findings": findings,
            "recommendations": [
                "Kiểm tra Task Manager để xác định tiến trình sử dụng tài nguyên cao.",
                "Theo dõi CPU, RAM và nhiệt độ trong quá trình xảy ra lỗi.",
                "Không nên tự động xóa hoặc gỡ ứng dụng khi chưa xác định nguyên nhân."
            ]
        }

    return {
        "status": "NO_CLEAR_CAUSE",
        "severity": "INFO",
        "findings": [],
        "recommendations": [
            "Chưa phát hiện nguyên nhân rõ ràng từ dữ liệu hiện tại.",
            "Cần thu thập thêm thông tin về thời điểm và tình huống xảy ra lỗi."
        ]
    }


# =========================================================
# 3. CHẨN ĐOÁN NHIỆT ĐỘ
# =========================================================

def diagnose_thermal(report):

    hardware = report.get("hardware", {})

    temperature = hardware.get("temperature", {})

    cpu = temperature.get("cpu", {})
    gpu = temperature.get("gpu", {})

    cpu_temp = cpu.get("package_c")
    gpu_temp = gpu.get("core_c")

    findings = []

    if cpu_temp is not None and cpu_temp >= 90:

        findings.append({
            "cause": "CPU có nhiệt độ cao",
            "evidence": f"CPU Package {cpu_temp}°C",
            "confidence": 0.90
        })

    if gpu_temp is not None and gpu_temp >= 90:

        findings.append({
            "cause": "GPU có nhiệt độ cao",
            "evidence": f"GPU Core {gpu_temp}°C",
            "confidence": 0.90
        })

    if findings:

        return {
            "status": "WARNING",
            "severity": "WARNING",
            "findings": findings,
            "recommendations": [
                "Kiểm tra tải CPU/GPU.",
                "Kiểm tra khe thông gió và quạt.",
                "Đảm bảo laptop được đặt trên bề mặt thông thoáng.",
                "Không tự ý tháo máy nếu chưa có kinh nghiệm."
            ]
        }

    return {
        "status": "NO_CLEAR_CAUSE",
        "severity": "INFO",
        "findings": [],
        "recommendations": [
            "Nhiệt độ hiện tại chưa cho thấy dấu hiệu bất thường rõ ràng.",
            "Cần kiểm tra nhiệt độ trong thời gian xảy ra lỗi."
        ]
    }


# =========================================================
# 4. CHẨN ĐOÁN PIN
# =========================================================

def diagnose_battery(report):

    hardware = report.get("hardware", {})

    battery = hardware.get("battery", {})
    capacity = battery.get("capacity", {})

    design = capacity.get("design_mwh")
    full = capacity.get("full_charge_mwh")

    findings = []

    if design is not None and full is not None and design > 0:

        ratio = (full / design) * 100

        if ratio < 70:

            findings.append({
                "cause": "Dung lượng pin đã suy giảm đáng kể",
                "evidence": f"Capacity ratio {ratio:.2f}%",
                "confidence": 0.90
            })

    if findings:

        return {
            "status": "WARNING",
            "severity": "WARNING",
            "findings": findings,
            "recommendations": [
                "Kiểm tra Battery Report.",
                "Theo dõi thời lượng sử dụng thực tế.",
                "Nếu pin phồng hoặc có dấu hiệu bất thường về vật lý, ngừng sử dụng và kiểm tra kỹ thuật."
            ]
        }

    return {
        "status": "NO_CLEAR_CAUSE",
        "severity": "INFO",
        "findings": [],
        "recommendations": [
            "Chưa phát hiện dấu hiệu suy giảm pin rõ ràng từ dữ liệu hiện tại."
        ]
    }


# =========================================================
# 5. CHẨN ĐOÁN NETWORK
# =========================================================

def diagnose_network(report):

    network = report.get("network", {})

    tests = network.get("tests", {})

    ping = tests.get("internet_ping")
    dns = tests.get("dns_resolution")
    socket = tests.get("internet_socket")

    findings = []

    if ping is False:

        findings.append({
            "cause": "Không kết nối được đến Internet bằng ICMP",
            "evidence": "Internet ping = False",
            "confidence": 0.85
        })

    if dns is False:

        findings.append({
            "cause": "DNS resolution có vấn đề",
            "evidence": "DNS resolution = False",
            "confidence": 0.90
        })

    if socket is False:

        findings.append({
            "cause": "Không tạo được kết nối Internet qua socket",
            "evidence": "Socket test = False",
            "confidence": 0.85
        })

    if findings:

        return {
            "status": "WARNING",
            "severity": "WARNING",
            "findings": findings,
            "recommendations": [
                "Kiểm tra trạng thái Wi-Fi hoặc Ethernet.",
                "Kiểm tra IP, Gateway và DNS.",
                "Kiểm tra thiết bị mạng khác để xác định lỗi nằm ở laptop hay router."
            ]
        }

    return {
        "status": "NO_CLEAR_CAUSE",
        "severity": "INFO",
        "findings": [],
        "recommendations": [
            "Các kiểm tra kết nối mạng hiện tại đều hoạt động.",
            "Nếu người dùng vẫn không truy cập được một website cụ thể, cần kiểm tra thêm DNS hoặc ứng dụng."
        ]
    }


# =========================================================
# 6. HÀM CHẨN ĐOÁN CHÍNH
# =========================================================

def diagnose_fault(user_input, report):

    classification = classify_fault(user_input)

    fault_id = classification.get("fault_id")

    if fault_id == "R01":

        analysis = diagnose_performance(report)

    elif fault_id == "T01":

        analysis = diagnose_thermal(report)

    elif fault_id == "B01":

        analysis = diagnose_battery(report)

    elif fault_id == "N01":

        analysis = diagnose_network(report)

    else:

        analysis = {
            "status": "NEED_MORE_DATA",
            "severity": "INFO",
            "findings": [],
            "recommendations": [
                "Chưa đủ dữ liệu để chẩn đoán chính xác.",
                "Cần hỏi thêm người dùng về triệu chứng cụ thể."
            ]
        }

    return {
        "user_input": user_input,

        "classification": classification,

        "analysis": analysis,

        "safety": {
            "automatic_repair": False,
            "action_level": 0,
            "message": "Chỉ chẩn đoán. Không tự động thay đổi hệ thống."
        }
    }# =========================================================
# AI LAPTOP DOCTOR - FAULT DIAGNOSIS ENGINE
# Version: 0.3.0
# =========================================================


def normalize_text(text):
    if not text:
        return ""

    return str(text).lower().strip()


# =========================================================
# 1. PHÂN LOẠI LỖI
# =========================================================

def classify_fault(user_input):

    text = normalize_text(user_input)

    # Hiệu năng
    performance_keywords = [
        "chậm",
        "lag",
        "giật",
        "treo",
        "đơ",
        "slow",
        "freeze",
        "nặng",
        "khựng"
    ]

    if any(keyword in text for keyword in performance_keywords):

        return {
            "fault_id": "R01",
            "category": "Performance",
            "title": "Hiệu năng hệ thống thấp",
            "required_data": [
                "cpu",
                "memory",
                "disk",
                "temperature"
            ]
        }

    # Nhiệt độ
    thermal_keywords = [
        "nóng",
        "nhiệt độ cao",
        "quá nóng",
        "quạt kêu",
        "quạt to",
        "fan",
        "overheat",
        "overheating"
    ]

    if any(keyword in text for keyword in thermal_keywords):

        return {
            "fault_id": "T01",
            "category": "Thermal",
            "title": "Nhiệt độ hoặc hệ thống tản nhiệt bất thường",
            "required_data": [
                "cpu",
                "temperature",
                "gpu"
            ]
        }

    # Pin
    battery_keywords = [
        "pin",
        "battery",
        "sạc",
        "sạc không vào",
        "tụt pin",
        "pin nhanh hết",
        "không nhận sạc"
    ]

    if any(keyword in text for keyword in battery_keywords):

        return {
            "fault_id": "B01",
            "category": "Battery",
            "title": "Vấn đề về pin hoặc sạc",
            "required_data": [
                "battery"
            ]
        }

    # Network
    network_keywords = [
        "wifi",
        "wi-fi",
        "mạng",
        "internet",
        "không vào mạng",
        "mất mạng",
        "dns",
        "ping"
    ]

    if any(keyword in text for keyword in network_keywords):

        return {
            "fault_id": "N01",
            "category": "Network",
            "title": "Vấn đề kết nối mạng",
            "required_data": [
                "network"
            ]
        }

    # Storage
    storage_keywords = [
        "ổ cứng",
        "ssd",
        "disk",
        "ổ đĩa",
        "đầy ổ",
        "ổ c",
        "không nhận ổ",
        "boot"
    ]

    if any(keyword in text for keyword in storage_keywords):

        return {
            "fault_id": "D01",
            "category": "Storage",
            "title": "Vấn đề về lưu trữ hoặc ổ đĩa",
            "required_data": [
                "disk"
            ]
        }

    # Màn hình
    display_keywords = [
        "màn hình",
        "sọc",
        "sọc màn hình",
        "nhấp nháy",
        "flicker",
        "đen màn hình",
        "display"
    ]

    if any(keyword in text for keyword in display_keywords):

        return {
            "fault_id": "D02",
            "category": "Display",
            "title": "Vấn đề hiển thị",
            "required_data": [
                "gpu",
                "system"
            ]
        }

    # Không xác định
    return {
        "fault_id": "UNKNOWN",
        "category": "Unknown",
        "title": "Chưa xác định được nhóm lỗi",
        "required_data": [
            "system"
        ]
    }


# =========================================================
# 2. CHẨN ĐOÁN HIỆU NĂNG
# =========================================================

def diagnose_performance(report):

    hardware = report.get("hardware", {})

    cpu = hardware.get("cpu", {})
    memory = hardware.get("memory", {})
    disk = hardware.get("disk", {})
    temperature = hardware.get("temperature", {})

    cpu_usage = cpu.get("usage_percent")
    memory_usage = memory.get("usage_percent")
    disk_usage = disk.get("usage_percent")

    cpu_temp = temperature.get("cpu", {}).get("package_c")

    findings = []

    if cpu_usage is not None and cpu_usage >= 90:

        findings.append({
            "cause": "CPU đang chịu tải rất cao",
            "evidence": f"CPU usage {cpu_usage}%",
            "confidence": 0.90
        })

    if memory_usage is not None and memory_usage >= 90:

        findings.append({
            "cause": "RAM đang được sử dụng rất cao",
            "evidence": f"RAM usage {memory_usage}%",
            "confidence": 0.90
        })

    if disk_usage is not None and disk_usage >= 90:

        findings.append({
            "cause": "Ổ đĩa gần đầy",
            "evidence": f"Disk usage {disk_usage}%",
            "confidence": 0.95
        })

    if cpu_temp is not None and cpu_temp >= 90:

        findings.append({
            "cause": "CPU đang có nhiệt độ cao",
            "evidence": f"CPU temperature {cpu_temp}°C",
            "confidence": 0.85
        })

    if findings:

        return {
            "status": "WARNING",
            "severity": "WARNING",
            "findings": findings,
            "recommendations": [
                "Kiểm tra Task Manager để xác định tiến trình sử dụng tài nguyên cao.",
                "Theo dõi CPU, RAM và nhiệt độ trong quá trình xảy ra lỗi.",
                "Không nên tự động xóa hoặc gỡ ứng dụng khi chưa xác định nguyên nhân."
            ]
        }

    return {
        "status": "NO_CLEAR_CAUSE",
        "severity": "INFO",
        "findings": [],
        "recommendations": [
            "Chưa phát hiện nguyên nhân rõ ràng từ dữ liệu hiện tại.",
            "Cần thu thập thêm thông tin về thời điểm và tình huống xảy ra lỗi."
        ]
    }


# =========================================================
# 3. CHẨN ĐOÁN NHIỆT ĐỘ
# =========================================================

def diagnose_thermal(report):

    hardware = report.get("hardware", {})

    temperature = hardware.get("temperature", {})

    cpu = temperature.get("cpu", {})
    gpu = temperature.get("gpu", {})

    cpu_temp = cpu.get("package_c")
    gpu_temp = gpu.get("core_c")

    findings = []

    if cpu_temp is not None and cpu_temp >= 90:

        findings.append({
            "cause": "CPU có nhiệt độ cao",
            "evidence": f"CPU Package {cpu_temp}°C",
            "confidence": 0.90
        })

    if gpu_temp is not None and gpu_temp >= 90:

        findings.append({
            "cause": "GPU có nhiệt độ cao",
            "evidence": f"GPU Core {gpu_temp}°C",
            "confidence": 0.90
        })

    if findings:

        return {
            "status": "WARNING",
            "severity": "WARNING",
            "findings": findings,
            "recommendations": [
                "Kiểm tra tải CPU/GPU.",
                "Kiểm tra khe thông gió và quạt.",
                "Đảm bảo laptop được đặt trên bề mặt thông thoáng.",
                "Không tự ý tháo máy nếu chưa có kinh nghiệm."
            ]
        }

    return {
        "status": "NO_CLEAR_CAUSE",
        "severity": "INFO",
        "findings": [],
        "recommendations": [
            "Nhiệt độ hiện tại chưa cho thấy dấu hiệu bất thường rõ ràng.",
            "Cần kiểm tra nhiệt độ trong thời gian xảy ra lỗi."
        ]
    }


# =========================================================
# 4. CHẨN ĐOÁN PIN
# =========================================================

def diagnose_battery(report):

    hardware = report.get("hardware", {})

    battery = hardware.get("battery", {})
    capacity = battery.get("capacity", {})

    design = capacity.get("design_mwh")
    full = capacity.get("full_charge_mwh")

    findings = []

    if design is not None and full is not None and design > 0:

        ratio = (full / design) * 100

        if ratio < 70:

            findings.append({
                "cause": "Dung lượng pin đã suy giảm đáng kể",
                "evidence": f"Capacity ratio {ratio:.2f}%",
                "confidence": 0.90
            })

    if findings:

        return {
            "status": "WARNING",
            "severity": "WARNING",
            "findings": findings,
            "recommendations": [
                "Kiểm tra Battery Report.",
                "Theo dõi thời lượng sử dụng thực tế.",
                "Nếu pin phồng hoặc có dấu hiệu bất thường về vật lý, ngừng sử dụng và kiểm tra kỹ thuật."
            ]
        }

    return {
        "status": "NO_CLEAR_CAUSE",
        "severity": "INFO",
        "findings": [],
        "recommendations": [
            "Chưa phát hiện dấu hiệu suy giảm pin rõ ràng từ dữ liệu hiện tại."
        ]
    }


# =========================================================
# 5. CHẨN ĐOÁN NETWORK
# =========================================================

def diagnose_network(report):

    network = report.get("network", {})

    tests = network.get("tests", {})

    ping = tests.get("internet_ping")
    dns = tests.get("dns_resolution")
    socket = tests.get("internet_socket")

    findings = []

    if ping is False:

        findings.append({
            "cause": "Không kết nối được đến Internet bằng ICMP",
            "evidence": "Internet ping = False",
            "confidence": 0.85
        })

    if dns is False:

        findings.append({
            "cause": "DNS resolution có vấn đề",
            "evidence": "DNS resolution = False",
            "confidence": 0.90
        })

    if socket is False:

        findings.append({
            "cause": "Không tạo được kết nối Internet qua socket",
            "evidence": "Socket test = False",
            "confidence": 0.85
        })

    if findings:

        return {
            "status": "WARNING",
            "severity": "WARNING",
            "findings": findings,
            "recommendations": [
                "Kiểm tra trạng thái Wi-Fi hoặc Ethernet.",
                "Kiểm tra IP, Gateway và DNS.",
                "Kiểm tra thiết bị mạng khác để xác định lỗi nằm ở laptop hay router."
            ]
        }

    return {
        "status": "NO_CLEAR_CAUSE",
        "severity": "INFO",
        "findings": [],
        "recommendations": [
            "Các kiểm tra kết nối mạng hiện tại đều hoạt động.",
            "Nếu người dùng vẫn không truy cập được một website cụ thể, cần kiểm tra thêm DNS hoặc ứng dụng."
        ]
    }


# =========================================================
# 6. HÀM CHẨN ĐOÁN CHÍNH
# =========================================================

def diagnose_fault(user_input, report):

    classification = classify_fault(user_input)

    fault_id = classification.get("fault_id")

    if fault_id == "R01":

        analysis = diagnose_performance(report)

    elif fault_id == "T01":

        analysis = diagnose_thermal(report)

    elif fault_id == "B01":

        analysis = diagnose_battery(report)

    elif fault_id == "N01":

        analysis = diagnose_network(report)

    else:

        analysis = {
            "status": "NEED_MORE_DATA",
            "severity": "INFO",
            "findings": [],
            "recommendations": [
                "Chưa đủ dữ liệu để chẩn đoán chính xác.",
                "Cần hỏi thêm người dùng về triệu chứng cụ thể."
            ]
        }

    return {
        "user_input": user_input,

        "classification": classification,

        "analysis": analysis,

        "safety": {
            "automatic_repair": False,
            "action_level": 0,
            "message": "Chỉ chẩn đoán. Không tự động thay đổi hệ thống."
        }
    }