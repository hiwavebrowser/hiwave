"""ab5.py with a 10 s live window after the load (`--live-ms 10000`), same arguments.
ab5.py captures at the end of the load and never runs a live turn (`pump_live`), so a
change that only acts on live turns (CH2.E20: stylesheets a script inserts) needs this."""
import pathlib
src = (pathlib.Path(__file__).parent / 'ab5.py').read_text()
assert "'--timeout-ms', '30000'," in src
exec(compile(src.replace("'--timeout-ms', '30000',", "'--timeout-ms', '30000', '--live-ms', '10000',"), 'ab5.py', 'exec'))
