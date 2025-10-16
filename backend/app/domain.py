"""Immutable fixture ingestion and exact currency aggregation."""
import csv
from dataclasses import dataclass
from datetime import date
from io import StringIO

@dataclass(frozen=True)
class Sale:
    order_id: str
    date: date
    product: str
    quantity: int
    unit_price_cents: int

def load_sales(text: str) -> tuple[Sale, ...]:
    reader = csv.DictReader(StringIO(text))
    expected = ['order_id', 'date', 'product', 'quantity', 'unit_price_cents']
    if reader.fieldnames != expected:
        raise ValueError('CSV must contain: ' + ', '.join(expected))
    rows, seen = [], set()
    total_cents = 0
    for line, raw in enumerate(reader, 2):
        try:
            if None in raw or any(value is None for value in raw.values()):
                raise ValueError('Incorrect number of columns')
            order_id, product = raw['order_id'].strip(), raw['product'].strip()
            quantity, price = int(raw['quantity']), int(raw['unit_price_cents'])
            if not order_id or not product or order_id in seen:
                raise ValueError('Order IDs must be unique and product names nonempty')
            if not 1 <= quantity <= 100000 or not 0 <= price <= 100000000:
                raise ValueError('Quantity must be 1–100,000 and price 0–100,000,000 cents')
            total_cents += quantity * price
            if total_cents > 9007199254740991:
                raise ValueError('Dataset total exceeds exact browser currency range')
            rows.append(Sale(order_id, date.fromisoformat(raw['date']), product, quantity, price))
            seen.add(order_id)
        except (ValueError, TypeError) as error:
            raise ValueError(f'CSV row {line}: {error}') from error
    if not rows:
        raise ValueError('CSV must contain at least one sale')
    return tuple(rows)

def metrics(rows: tuple[Sale, ...], start: date | None = None, end: date | None = None) -> dict:
    if start and end and start > end:
        raise ValueError('Start date must be on or before end date')
    selected = [row for row in rows if (not start or row.date >= start) and (not end or row.date <= end)]
    daily, products = {}, {}
    for row in selected:
        revenue = row.quantity * row.unit_price_cents
        day = row.date.isoformat()
        daily[day] = daily.get(day, 0) + revenue
        product = products.setdefault(row.product, {'product': row.product, 'revenue_cents': 0, 'units': 0})
        product['revenue_cents'] += revenue
        product['units'] += row.quantity
    return {
        'revenue_cents': sum(row.quantity * row.unit_price_cents for row in selected),
        'orders': len(selected), 'units': sum(row.quantity for row in selected),
        'daily': [{'date': day, 'revenue_cents': revenue} for day, revenue in sorted(daily.items())],
        'products': sorted(products.values(), key=lambda item: (-item['revenue_cents'], item['product'])),
        'available_range': {'start': min(row.date for row in rows).isoformat(), 'end': max(row.date for row in rows).isoformat()} if rows else None,
    }
