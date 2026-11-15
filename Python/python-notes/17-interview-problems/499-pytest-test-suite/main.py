"""Pytest suite example: code under test + tests (fixtures, parametrize, raises, mark, monkeypatch, tmp_path, mock).
Run:  pytest main.py -v     (or python main.py, which invokes pytest)"""
import json
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest


# ---------- code under test ----------
class InsufficientFunds(Exception):
    pass


class Account:
    def __init__(self, balance: int = 0) -> None:
        self.balance = balance

    def withdraw(self, amt: int) -> int:
        if amt <= 0:
            raise ValueError("amount must be positive")
        if amt > self.balance:
            raise InsufficientFunds(f"need {amt - self.balance} more")
        self.balance -= amt
        return self.balance


def load_config(path: Path) -> dict:
    return json.loads(path.read_text())


def get_price(client, sku: str) -> float:
    return client.get(f"/price/{sku}")["price"] * 1.18  # adds GST


def is_prod() -> bool:
    import os
    return os.environ.get("ENV") == "prod"


# ---------- tests ----------
@pytest.fixture
def acct() -> Account:  # fresh per test
    return Account(100)


@pytest.fixture
def resource():
    log = ["setup"]
    yield log  # test runs here
    log.append("teardown")  # cleanup


def test_withdraw_ok(acct):
    assert acct.withdraw(30) == 70


@pytest.mark.parametrize("amt, expected", [(0, "positive"), (-5, "positive"), (500, "more")])
def test_withdraw_errors(acct, amt, expected):
    with pytest.raises((ValueError, InsufficientFunds), match=expected):
        acct.withdraw(amt)


def test_config_with_tmp_path(tmp_path):
    p = tmp_path / "c.json"
    p.write_text('{"debug": true}')
    assert load_config(p) == {"debug": True}


def test_env_with_monkeypatch(monkeypatch):
    monkeypatch.setenv("ENV", "prod")
    assert is_prod() is True


def test_mock_client():
    client = Mock()
    client.get.return_value = {"price": 100}
    assert get_price(client, "A1") == pytest.approx(118.0)
    client.get.assert_called_once_with("/price/A1")


def test_float_approx():
    assert 0.1 + 0.2 == pytest.approx(0.3)


def test_fixture_teardown(resource):
    assert resource == ["setup"]


@pytest.mark.skip(reason="demo")
def test_skipped():
    assert False


@pytest.mark.xfail(reason="known bug", strict=True)
def test_known_bug():
    assert 1 + 1 == 3


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
