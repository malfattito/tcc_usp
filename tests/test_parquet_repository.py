import pandas as pd

from fiscal_risk.io.parquet_repository import ParquetRepository


def test_save_then_load_round_trips_the_frame(tmp_path):
    repository = ParquetRepository(tmp_path / "processed")
    frame = pd.DataFrame({"ibge_code": [1, 2], "year": [2019, 2019], "x": [0.5, None]})

    path = repository.save(frame, "sample")
    loaded = repository.load("sample")

    assert path.exists()
    pd.testing.assert_frame_equal(loaded, frame)
