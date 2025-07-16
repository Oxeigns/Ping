import sys
from pathlib import Path
# Ensure project root is in sys.path for module imports
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import os
os.environ.setdefault('BOT_TOKEN', 'dummy')
os.environ.setdefault('API_ID', '1')
os.environ.setdefault('API_HASH', 'hash')
os.environ.setdefault('OWNER_ID', '1')
os.environ.setdefault('MONGO_URI', 'mongodb://localhost:27017/testdb')
