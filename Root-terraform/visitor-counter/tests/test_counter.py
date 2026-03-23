import json
from lambdas.counter import lambda_handler


class FakeVisitorsTable:
    def __init__(self, existing_item=None):
        self.existing_item = existing_item
        self.put_called = False
        self.update_called = False
        self.last_put_item = None
        self.last_update_kwargs = None

    def get_item(self, Key):
        if self.existing_item is not None:
            return {"Item": self.existing_item}
        return {}

    def put_item(self, Item):
        self.put_called = True
        self.last_put_item = Item
        return {"ResponseMetadata": {"HTTPStatusCode": 200}}

    def update_item(self, **kwargs):
        self.update_called = True
        self.last_update_kwargs = kwargs
        return {"ResponseMetadata": {"HTTPStatusCode": 200}}


class FakeCounterTable:
    def __init__(self, count=0):
        self.count = count
        self.update_called = False

    def update_item(self, **kwargs):
        self.update_called = True
        self.count += 1
        return {"Attributes": {"count": self.count}}

    def get_item(self, Key):
        return {"Item": {"count": self.count}}


def test_new_visitor_increments_global_counter(monkeypatch):
    visitors_table = FakeVisitorsTable(existing_item=None)
    counter_table = FakeCounterTable(count=10)

    monkeypatch.setattr("lambdas.counter.get_visitors_table", lambda: visitors_table)
    monkeypatch.setattr("lambdas.counter.get_counter_table", lambda: counter_table)
    monkeypatch.setattr("lambdas.counter.time.time", lambda: 1700000000)

    event = {
        "headers": {},
        "requestContext": {
            "identity": {
                "sourceIp": "1.2.3.4"
            }
        }
    }

    response = lambda_handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert visitors_table.put_called is True
    assert visitors_table.update_called is False
    assert counter_table.update_called is True
    assert body["count"] == 11


def test_existing_visitor_within_cooldown_does_not_increment_global_counter(monkeypatch):
    now = 1700000000

    visitors_table = FakeVisitorsTable(
        existing_item={
            "visitor_id": "abc123",
            "first_visit": now - 1000,
            "last_visit": now - 100,
            "visit_count": 3
        }
    )
    counter_table = FakeCounterTable(count=10)

    monkeypatch.setattr("lambdas.counter.get_visitors_table", lambda: visitors_table)
    monkeypatch.setattr("lambdas.counter.get_counter_table", lambda: counter_table)
    monkeypatch.setattr("lambdas.counter.time.time", lambda: now)

    event = {
        "headers": {
            "x-visitor-id": "abc123"
        },
        "requestContext": {
            "identity": {
                "sourceIp": "1.2.3.4"
            }
        }
    }

    response = lambda_handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert visitors_table.put_called is False
    assert visitors_table.update_called is True
    assert counter_table.update_called is False
    assert body["count"] == 10


def test_existing_visitor_after_cooldown_increments_global_counter(monkeypatch):
    now = 1700000000

    visitors_table = FakeVisitorsTable(
        existing_item={
            "visitor_id": "abc123",
            "first_visit": now - 200000,
            "last_visit": now - 90000,
            "visit_count": 3
        }
    )
    counter_table = FakeCounterTable(count=10)

    monkeypatch.setattr("lambdas.counter.get_visitors_table", lambda: visitors_table)
    monkeypatch.setattr("lambdas.counter.get_counter_table", lambda: counter_table)
    monkeypatch.setattr("lambdas.counter.time.time", lambda: now)

    event = {
        "headers": {
            "x-visitor-id": "abc123"
        },
        "requestContext": {
            "identity": {
                "sourceIp": "1.2.3.4"
            }
        }
    }

    response = lambda_handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert visitors_table.update_called is True
    assert counter_table.update_called is True
    assert body["count"] == 11


def test_hash_ip_fallback_used_when_header_missing(monkeypatch):
    visitors_table = FakeVisitorsTable(existing_item=None)
    counter_table = FakeCounterTable(count=5)

    monkeypatch.setattr("lambdas.counter.get_visitors_table", lambda: visitors_table)
    monkeypatch.setattr("lambdas.counter.get_counter_table", lambda: counter_table)
    monkeypatch.setattr("lambdas.counter.time.time", lambda: 1700000000)

    event = {
        "headers": {},
        "requestContext": {
            "identity": {
                "sourceIp": "9.9.9.9"
            }
        }
    }

    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    assert visitors_table.put_called is True
    assert visitors_table.last_put_item["visitor_id"] != "9.9.9.9"