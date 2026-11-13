import pytest

from inventory.csvio import read_items

SAMPLE_CSV = (
    "sku,name,supplier,on_hand,reserved,unit_cost,reorder_point,reorder_qty\n"
    "B-200,Hex bolt M6,Acme,500,20,0.08,200,1000\n"
    "N-310,Hex nut M6,Acme,120,0,0.05,200,1000\n"
    "W-110,Washer M6,Bolton,0,0,0.02,100,500\n"
    "G-900,Wood glue 250ml,,14,4,3.75,0,0\n"
)


@pytest.fixture
def sample_csv(tmp_path):
    path = tmp_path / "stock.csv"
    path.write_text(SAMPLE_CSV, encoding="utf-8")
    return path


@pytest.fixture
def items(sample_csv):
    return read_items(sample_csv)
