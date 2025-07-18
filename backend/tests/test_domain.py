from datetime import date
import pytest
from app.domain import load_sales, metrics
CSV = "order_id,date,product,quantity,unit_price_cents\nA,2026-01-01,Audit,2,1999\nB,2026-01-02,Design,1,10000\n"

def test_integer_revenue_and_inclusive_date_filter():
    rows = load_sales(CSV)
    result = metrics(rows, date(2026,1,1), date(2026,1,1))
    assert result['revenue_cents'] == 3998
    assert result['orders'] == 1
    assert result['units'] == 2
    assert result['daily'] == [{'date':'2026-01-01','revenue_cents':3998}]
    assert metrics(rows)['revenue_cents'] == 13998

def test_empty_range_and_reproducible_ingest():
    assert load_sales(CSV) == load_sales(CSV)
    result = metrics(load_sales(CSV), date(2027,1,1), date(2027,1,2))
    assert result['orders'] == 0
    assert result['revenue_cents'] == 0
    assert result['products'] == []

@pytest.mark.parametrize('bad',[
    '', 'wrong,columns\n1,2', CSV.replace('2,1999','0,1999'),
    CSV.replace('1999','-1'), CSV.replace('2026-01-01','2026-02-31'),
    CSV.replace('B,2026','A,2026'), CSV.replace('Audit',''),
    CSV.replace('1999','1.99')])
def test_rejects_invalid_csv(bad):
    with pytest.raises(ValueError): load_sales(bad)

def test_rejects_inverted_range():
    with pytest.raises(ValueError): metrics(load_sales(CSV), date(2026,2,1), date(2026,1,1))

@pytest.mark.parametrize('bad',[CSV.replace('1999','9007199254740992'), CSV.replace('2,1999','100001,1999')])
def test_bounds_keep_browser_currency_precise(bad):
    with pytest.raises(ValueError): load_sales(bad)

def test_total_cents_cannot_exceed_javascript_safe_integer():
    text = 'order_id,date,product,quantity,unit_price_cents\n' + ''.join(
        f'{index},2026-01-01,Design,100000,100000000\n' for index in range(901))
    with pytest.raises(ValueError): load_sales(text)
