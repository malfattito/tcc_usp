from pathlib import Path

import pandas as pd


class ParquetRepository:
    def __init__(self, directory: Path) -> None:
        self._directory = directory

    def save(self, frame: pd.DataFrame, name: str) -> Path:
        self._directory.mkdir(parents=True, exist_ok=True)
        path = self._directory / f"{name}.parquet"
        frame.to_parquet(path, index=False)
        return path

    def load(self, name: str) -> pd.DataFrame:
        return pd.read_parquet(self._directory / f"{name}.parquet")
