import os
import tempfile

# Pre-set persistent MPLCONFIGDIR so matplotlib does not rebuild font cache on every test run
os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "matplotlib_cache"))
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)
