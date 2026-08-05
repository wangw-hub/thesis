#!/usr/bin/env bash
set -Eeuo pipefail

mode="${1:---json}"
targets=(192.168.6.129 192.168.6.130 192.168.6.131 192.168.6.132 192.168.6.133)

if [[ "$mode" == "--text" ]]; then
  echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "hostname=$(hostname)"
  echo "whoami=$(whoami)"
  cat /etc/os-release
  echo "machine_id=$(cat /etc/machine-id)"
  echo "ipv4:"
  ip -4 -o addr show scope global
  echo "default_route:"
  ip route show default
  echo "java:"
  java -version 2>&1
  echo "cpu:"
  lscpu
  echo "memory:"
  free -b
  echo "disk:"
  df -B1 /
  echo "clock:"
  timedatectl
  echo "sudo_noninteractive:"
  sudo -n true
  echo "ports:"
  ss -lntup | grep -E ':(30303|8545|8546)\b' || true
  echo "besu_commands:"
  command -v besu || true
  [[ -x /opt/besu/bin/besu ]] && /opt/besu/bin/besu --version || true
  echo "besu_processes:"
  pgrep -af '[b]esu' || true
  echo "besu_units:"
  systemctl list-unit-files --type=service --no-legend --no-pager | awk '$1 ~ /^besu/' || true
  echo "besu_paths:"
  for path in /etc/besu /var/lib/besu /opt/besu; do
    if [[ -e "$path" || -L "$path" ]]; then
      stat -c '%F %a %U:%G %n' "$path"
    else
      echo "ABSENT $path"
    fi
  done
  echo "peer_ping:"
  for target in "${targets[@]}"; do
    if ping -c 1 -W 1 "$target" >/dev/null 2>&1; then
      echo "$target=reachable"
    else
      echo "$target=unreachable"
    fi
  done
  exit 0
fi

python3 - "${targets[@]}" <<'PY'
import json
import os
import pathlib
import re
import shutil
import socket
import subprocess
import sys
from datetime import datetime, timezone

targets = sys.argv[1:]

def run(args, check=False):
    result = subprocess.run(args, text=True, capture_output=True)
    if check and result.returncode:
        raise RuntimeError(f"{args!r}: {result.stderr.strip()}")
    return {
        "exit_code": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }

os_release = {}
for line in pathlib.Path("/etc/os-release").read_text().splitlines():
    if "=" in line:
        key, value = line.split("=", 1)
        os_release[key] = value.strip('"')

java = run(["java", "-version"])
java_text = java["stderr"] or java["stdout"]
match = re.search(r'version "(\d+)', java_text)
ports = {}
ss = run(["ss", "-lntup"])
for port in (30303, 8545, 8546):
    ports[str(port)] = any(
        re.search(rf":{port}\b", line) for line in ss["stdout"].splitlines()
    )

paths = {}
for value in ("/etc/besu", "/var/lib/besu", "/opt/besu"):
    path = pathlib.Path(value)
    paths[value] = {
        "exists": path.exists() or path.is_symlink(),
        "is_symlink": path.is_symlink(),
    }

report = {
    "collected_at_utc": datetime.now(timezone.utc).isoformat(),
    "hostname": socket.gethostname(),
    "whoami": run(["whoami"], True)["stdout"],
    "os_release": os_release,
    "machine_id": pathlib.Path("/etc/machine-id").read_text().strip(),
    "ipv4": run(["ip", "-4", "-o", "addr", "show", "scope", "global"], True)["stdout"].splitlines(),
    "default_route": run(["ip", "route", "show", "default"], True)["stdout"],
    "peer_reachability": {
        target: run(["ping", "-c", "1", "-W", "1", target])["exit_code"] == 0
        for target in targets
    },
    "java": java,
    "java_major": int(match.group(1)) if match else None,
    "cpu": run(["lscpu"], True)["stdout"],
    "memory": run(["free", "-b"], True)["stdout"],
    "disk": run(["df", "-B1", "/"], True)["stdout"],
    "timedatectl": run(["timedatectl"], True)["stdout"],
    "timezone": run(["timedatectl", "show", "-p", "Timezone", "--value"], True)["stdout"],
    "sudo_noninteractive": run(["sudo", "-n", "true"])["exit_code"] == 0,
    "ports_in_use": ports,
    "commands": {
        "python3": shutil.which("python3"),
        "unzip": shutil.which("unzip"),
        "sha256sum": shutil.which("sha256sum"),
        "besu": shutil.which("besu"),
    },
    "besu_processes": run(["pgrep", "-af", "[b]esu"])["stdout"].splitlines(),
    "besu_units": [
        line for line in run(["systemctl", "list-unit-files", "--type=service", "--no-legend", "--no-pager"])["stdout"].splitlines()
        if line.split() and line.split()[0].startswith("besu")
    ],
    "besu_paths": {
        value: {
            **metadata,
            "entries": sorted(child.name for child in pathlib.Path(value).iterdir()) if metadata["exists"] and pathlib.Path(value).is_dir() else [],
        }
        for value, metadata in paths.items()
    },
}
print(json.dumps(report, ensure_ascii=False, indent=2))
PY
