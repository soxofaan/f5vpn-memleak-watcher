

F5 VPN Memory Leak Watcher
==========================


The F5 VPN utility has memory leak issues on Linux systems.
This script monitors the memory usage of the F5 VPN process
and sends a notification when the memory usage exceeds a specified threshold,
so you can take action (restart the client) when it suits you.


dependencies:
- `python3`
- `notify-send` (part of `libnotify-bin` on Debian-based systems)
