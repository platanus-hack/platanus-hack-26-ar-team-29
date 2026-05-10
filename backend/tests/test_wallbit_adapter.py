from app.providers.wallbit.adapter import (
    asset_to_price_usd,
    stocks_balance_to_rows,
    transaction_cost_basis_by_symbol,
)


def test_asset_to_price_usd_unwraps_wallbit_data() -> None:
    assert asset_to_price_usd({"data": {"symbol": "AAPL", "price": "293.85"}}) == 293.85


def test_stocks_balance_to_rows_values_position_from_inline_price() -> None:
    rows = stocks_balance_to_rows({"data": [{"symbol": "TSLA", "shares": "2", "price": 250}]})

    assert rows == [
        {
            "kind": "stocks",
            "account": "investment",
            "symbol": "TSLA",
            "shares": "2",
            "usd_value": 500.0,
            "current_price_usd": 250,
            "avg_cost_usd": None,
            "cost_basis_usd": None,
            "raw": {"symbol": "TSLA", "shares": "2", "price": 250},
        }
    ]


def test_transaction_cost_basis_by_symbol_uses_buy_trades_only() -> None:
    payload = {
        "data": {
            "data": [
                {
                    "type": "TRADE",
                    "status": "PENDING",
                    "trade_info": {"direction": "BUY", "symbol": "AAPL", "share_price": 100},
                    "source_amount": 200,
                    "dest_amount": 2,
                    "created_at": "2026-05-09T14:51:35.000000Z",
                },
                {
                    "type": "TRADE",
                    "status": "PENDING",
                    "trade_info": {"direction": "SELL", "symbol": "AAPL", "share_price": 120},
                    "source_amount": 120,
                    "dest_amount": 1,
                    "created_at": "2026-05-10T14:51:35.000000Z",
                },
                {
                    "type": "TRADE",
                    "status": "PENDING",
                    "trade_info": {"direction": "BUY", "symbol": "AAPL", "share_price": 110},
                    "dest_amount": 1,
                    "created_at": "2026-05-09T15:51:35.000000Z",
                },
                {
                    "type": "TRADE",
                    "status": "FAILED",
                    "trade_info": {"direction": "BUY", "symbol": "TSLA", "share_price": 427.99},
                    "source_amount": 427.99,
                    "dest_amount": 1,
                    "created_at": "2026-05-10T15:51:35.000000Z",
                },
            ]
        }
    }

    basis = transaction_cost_basis_by_symbol(payload)
    assert basis["AAPL"] == {
        "avg_cost_usd": 310 / 3,
        "latest_price_usd": 120,
        "total_bought_shares": 3,
        "total_bought_cost_usd": 310,
    }
    assert "TSLA" not in basis
