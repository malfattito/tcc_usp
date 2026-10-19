import gzip
import json

from fiscal_risk.io.raw_reader import GzipJsonReader


def test_reads_records_from_gzip_json(tmp_path):
    path = tmp_path / "1100015.json.gz"
    records = [{"cod_conta": "RO1.0.0.0.00.0.0", "valor": 1.5}]
    with gzip.open(path, "wt", encoding="utf-8") as file:
        json.dump(records, file)

    assert GzipJsonReader().read(path) == records


def test_empty_file_returns_empty_list(tmp_path):
    path = tmp_path / "empty.json.gz"
    with gzip.open(path, "wt", encoding="utf-8") as file:
        json.dump([], file)

    assert GzipJsonReader().read(path) == []
