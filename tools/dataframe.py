from pathlib import Path
import zipfile

import pandas as pd


def load_dataframe(path: Path) -> pd.DataFrame:

    suffix = path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(path)

    if suffix in [".xls", ".xlsx"]:
        return pd.read_excel(path)

    if suffix == ".parquet":
        return pd.read_parquet(path)

    if suffix == ".json":
        return pd.read_json(path)

    if suffix == ".zip":

        extract_dir = path.parent / path.stem

        with zipfile.ZipFile(path) as z:
            z.extractall(extract_dir)

        for file in extract_dir.iterdir():

            if file.suffix.lower() == ".csv":
                return pd.read_csv(file)

            if file.suffix.lower() in [".xlsx", ".xls"]:
                return pd.read_excel(file)

    raise ValueError(
        f"Unsupported file format: {suffix}"
    )
