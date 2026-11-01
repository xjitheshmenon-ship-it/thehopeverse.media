"""python test_budget.py: a run stops starting paid work at RUN_BUDGET, even with the daily cap lifted."""
import os
import tempfile
from pathlib import Path

os.environ.update(DAILY_BUDGET="1000", RUN_BUDGET="3", ANTHROPIC_API_KEY=os.environ.get("ANTHROPIC_API_KEY", "x"))
import agents

agents.RUN_SPEND = Path(tempfile.mkdtemp()) / "run-spend.txt"
agents.HISTORY = agents.RUN_SPEND.with_name("history.jsonl")
assert agents.budget_ok()
agents.log_spend(2.5, "yt-instinct-ja")
assert agents.budget_ok() and not agents.budget_ok(0.6)
agents.log_spend(0.6, "yt-instinct-ja")
assert not agents.budget_ok()
print("ok")
