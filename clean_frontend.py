import shutil
import os

frontend_path = os.path.join(os.path.dirname(__file__), 'frontend')
if os.path.exists(frontend_path):
    shutil.rmtree(frontend_path)
