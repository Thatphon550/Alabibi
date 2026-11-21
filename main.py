from pathlib import Path

from app import App
from seed_data import DATA_PATH

IMAGE_FOLDER = Path(__file__).parent / "images"

app = App(DATA_PATH, IMAGE_FOLDER)
app.mainloop()
