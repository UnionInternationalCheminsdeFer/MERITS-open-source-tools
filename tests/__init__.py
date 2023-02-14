import sys
from pathlib import Path

src_path = (Path(__file__).parent.parent / "src/").absolute()
print(f"Adding sys path {src_path}")
sys.path.append(str(src_path) + "/")
