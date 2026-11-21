import os
import pickle

from models import StoreData

def save(data, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".tmp")
    with open(tmp_path, "wb") as f:
        pickle.dump(data, f)
    os.replace(tmp_path, path)

def load(path, default):
    try:
        with open(path, "rb") as f:
            data = pickle.load(f)
        if isinstance(data, StoreData):
            return data
        print(f"[storage] {path} does not contain StoreData, starting fresh")
    except FileNotFoundError:
        pass

    except Exception as error:
        backup = path.with_suffix(".bad")
        os.replace(path, backup)
        print(f"[storage] could not read {path} ({error}); moved it to {backup.name}")

    save(default, path)
    return default
