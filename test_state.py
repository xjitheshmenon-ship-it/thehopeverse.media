"""python test_state.py: the spend-log merge keeps lines from parallel runs."""
import tempfile
from pathlib import Path

from state import merge_log

p = Path(tempfile.mkdtemp()) / "history.jsonl"
p.write_text("a\nb\nc\n")
merge_log(p, "a\nb\nx\n")  # another run saved x meanwhile; this run added c
assert p.read_text() == "a\nb\nx\nc\n"
p.write_text("c\n")
merge_log(p, "a\nb\n")  # this run never loaded the log (1 Nov 2026): keep the saved lines
assert p.read_text() == "a\nb\nc\n"
print("ok")
