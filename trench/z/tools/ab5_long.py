"""ab5.py with a 90 s capture limit, same arguments. For sites that pass 30 s under load (cnn, squarespace)."""
import pathlib
src = (pathlib.Path(__file__).parent / 'ab5.py').read_text()
assert "'30000'" in src
exec(compile(src.replace("'30000'", "'90000'"), 'ab5.py', 'exec'))
