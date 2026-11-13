"""E2 `checklist`: Stop hook that makes the agent check the original task before it may stop.

The first stop of each turn is blocked with the task as an external checklist; `stop_hook_active` is set
on the retry, so the agent can always stop the second time (no loop). Skipped during the probe.
"""
import json
import os
import sys
import time
from pathlib import Path

CFG = Path(os.environ.get("AHI_CFG", "/cfg"))

event = json.load(sys.stdin)
if (CFG / "probe").exists() or event.get("stop_hook_active"):
    sys.exit(0)
goal = (CFG / "goal.md").read_text().strip()
reason = ("Before stopping, go through the ORIGINAL task of this session as a checklist. For each "
          "numbered requirement, check the current code (run the tests if useful) and fix anything that "
          "is missing. If every requirement is already met, say so briefly and stop.\n\nORIGINAL task:\n\n"
          + goal)
with open(CFG / "hooks.log", "a") as fh:
    fh.write(json.dumps({"t": time.time(), "hook": "stop_checklist"}) + "\n")
print(json.dumps({"decision": "block", "reason": reason}))
