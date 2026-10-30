import os
import sys
import tempfile
from pathlib import Path

# Los tests usan una carpeta temporal: nunca tocan los CSV reales de data/.
os.environ["RSC_DATA_DIR"] = tempfile.mkdtemp(prefix="rsc_test_")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
