import subprocess
import json
import socket


def collect_network():

    result = {
        "available": True,
        "adapters": [],
        "configurations": [],
        "tests": {
            "internet_ping": False,
            "dns_resolution": False,
            "internet_socket": False
        }
    }

    # =========================================
    # NETWORK ADAPTERS
    # =========================================

    try:
        command = """
        Get-NetAdapter |
        Select-Object Name, InterfaceDescription, Status, LinkSpeed, MacAddress |
        ConvertTo-Json
        """

        output = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                command
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        data = json.loads(output.stdout)

        if not isinstance(data, list):
            data = [data]

        for adapter in data:

            result["adapters"].append({
                "name": adapter.get("Name"),
                "description": adapter.get(
                    "InterfaceDescription"
                ),
                "status": adapter.get("Status"),
                "link_speed": adapter.get("LinkSpeed"),
                "mac_address": adapter.get("MacAddress")
            })

    except Exception as error:

        result["available"] = False
        result["error"] = str(error)

        return result

    # =========================================
    # IP / GATEWAY / DNS
    # =========================================

    try:
        command = """
        Get-NetIPConfiguration |
        Select-Object InterfaceAlias,
        IPv4Address,
        IPv4DefaultGateway,
        DNSServer |
        ConvertTo-Json -Depth 10
        """

        output = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                command
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        data = json.loads(output.stdout)

        if not isinstance(data, list):
            data = [data]

        for config in data:

            ips = []
            gateways = []
            dns_servers = []

            # IP
            ipv4 = config.get("IPv4Address")

            if isinstance(ipv4, list):

                for item in ipv4:

                    if isinstance(item, dict):

                        address = item.get(
                            "IPv4Address"
                        )

                        if address:
                            ips.append(address)

            elif isinstance(ipv4, dict):

                address = ipv4.get(
                    "IPv4Address"
                )

                if address:
                    ips.append(address)

            # Gateway
            gateway = config.get(
                "IPv4DefaultGateway"
            )

            if isinstance(gateway, list):

                for item in gateway:

                    if isinstance(item, dict):

                        address = item.get(
                            "NextHop"
                        )

                        if address:
                            gateways.append(address)

            elif isinstance(gateway, dict):

                address = gateway.get(
                    "NextHop"
                )

                if address:
                    gateways.append(address)

            # DNS
            dns = config.get("DNSServer")

            if isinstance(dns, dict):

                addresses = dns.get(
                    "ServerAddresses"
                )

                if isinstance(addresses, list):

                    dns_servers.extend(
                        addresses
                    )

            elif isinstance(dns, list):

                for item in dns:

                    if isinstance(item, dict):

                        addresses = item.get(
                            "ServerAddresses"
                        )

                        if isinstance(addresses, list):

                            dns_servers.extend(
                                addresses
                            )

            result["configurations"].append({
                "interface": config.get(
                    "InterfaceAlias"
                ),
                "ip_addresses": ips,
                "gateways": gateways,
                "dns_servers": dns_servers
            })

    except Exception:
        pass

    # =========================================
    # INTERNET PING
    # =========================================

    try:

        output = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Test-Connection 8.8.8.8 -Count 2 -Quiet"
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        result["tests"]["internet_ping"] = (
            "True" in output.stdout
        )

    except Exception:
        pass

    # =========================================
    # DNS
    # =========================================

    try:

        output = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Resolve-DnsName google.com -ErrorAction SilentlyContinue"
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        result["tests"]["dns_resolution"] = bool(
            output.stdout.strip()
        )

    except Exception:
        pass

    # =========================================
    # SOCKET
    # =========================================

    try:

        socket.create_connection(
            ("8.8.8.8", 53),
            timeout=3
        )

        result["tests"]["internet_socket"] = True

    except Exception:
        pass

    return result