"""E2 `anchor`: UserPromptSubmit hook that re-states the original task with every new user message.

Runs inside the agent container (python:3.11). The harness writes the task to /cfg/goal.md and creates
/cfg/probe before the goal-recall probe, so the probe is never answered with the hook's help.
"""
import json
import os
import sys
import time
from pathlib import Path

CFG = Path(os.environ.get("AHI_CFG", "/cfg"))

event = json.load(sys.stdin)
if (CFG / "probe").exists():
    sys.exit(0)
goal = (CFG / "goal.md").read_text().strip()
context = ("Reminder from the session harness. The ORIGINAL task of this session, verbatim:\n\n" + goal +
           "\n\nHandle the new message, but the original task stays the main objective until it is done.")
with open(CFG / "hooks.log", "a") as fh:
    fh.write(json.dumps({"t": time.time(), "hook": "anchor", "event": event.get("hook_event_name")}) + "\n")
print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": context}}))
