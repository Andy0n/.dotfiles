# -*- coding: utf-8 -*-
"""
Utility functions for the Fabric bar configuration.
"""

import re
import shlex
import subprocess
from datetime import datetime


def run_command(command):
    """Runs a command and returns its stdout, handling errors."""
    try:
        # Use shlex.split for safer command parsing if command is a string
        if isinstance(command, str):
            command = shlex.split(command)
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,  # Don't raise exception on non-zero exit
            timeout=5,  # Add a timeout
        )
        if result.returncode != 0:
            print(f"Command failed: {' '.join(command)}")
            print(f"Stderr: {result.stderr}")
            return None
        return result.stdout.strip()
    except FileNotFoundError:
        print(f"Error: Command not found: {command[0]}")
        return None
    except subprocess.TimeoutExpired:
        print(f"Error: Command timed out: {' '.join(command)}")
        return None
    except Exception as e:
        print(f"Error running command {' '.join(command)}: {e}")
        return None


def format_relative_time(time_obj: datetime) -> str:
    """Formats a datetime object into a relative time string (e.g., '5m ago')."""
    now = datetime.now()
    diff = now - time_obj
    seconds = diff.total_seconds()
    if seconds < 60:
        return "Now"
    elif seconds < 3600:
        return f"{int(seconds / 60)}m ago"
    elif seconds < 86400:
        return f"{int(seconds / 3600)}h ago"
    else:
        return f"{int(seconds / 86400)}d ago"


