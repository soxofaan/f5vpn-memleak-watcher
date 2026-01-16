#!/usr/bin/env python3
import argparse
import logging
import re
import subprocess
import time

_log = logging.getLogger(__name__)


def pretty_size(size: int) -> str:
    """Human-readable byte count."""
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if size < 1024 or unit == "TiB":
            return f"{size:.2f} {unit}" if unit != "B" else f"{size} B"
        size /= 1024


def get_total_memory_usage() -> int:
    """
    Return total RSS (bytes) of all /opt/f5/vpn/libexec/QtWebEngineProcess processes
    """
    usage = 0
    ps_dump = subprocess.check_output(
        ["ps", "-C", "QtWebEngineProcess", "-o", "pid=,rss=,args="],
        text=True,
        encoding="utf-8",
    )
    for match in re.finditer(r"^\s*(\d+)\s+(\d+)\s+(.*)$", ps_dump, re.MULTILINE):
        pid, rss_kb, cmdline = match.group(1, 2, 3)
        _log.debug(f"ps dump: {pid=}, {rss_kb=}, {cmdline[:100]=}")
        if "/opt/f5/vpn/libexec/QtWebEngineProcess" in cmdline:
            usage += int(rss_kb) * 1024

    return usage


def notify(title: str, body: str):
    subprocess.run(
        ["notify-send", "-i", "dialog-warning", title, body],
        check=False,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--threshold", type=float, default=1.0, help="Memory threshold in GiB."
    )
    parser.add_argument(
        "--interval", type=int, default=600, help="Polling interval in seconds."
    )
    args = parser.parse_args()
    threshold_bytes = int(args.threshold * 1024**3)
    poll_interval = args.interval

    logging.basicConfig(
        level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s"
    )
    _log.info(f"{threshold_bytes=:_d}, {poll_interval=}")

    while True:
        memory_usage = get_total_memory_usage()
        _log.info(f"Total F5 VPN memory usage: {pretty_size(memory_usage)}")
        if memory_usage > threshold_bytes:
            notify(
                "High F5 VPN memory usage",
                f"Total RSS is {pretty_size(memory_usage)} (above threshold {pretty_size(threshold_bytes)}).",
            )
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
