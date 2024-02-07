import datetime
from unittest.mock import patch
from urllib.parse import urlencode
from uuid import uuid4

from fastapi.encoders import jsonable_encoder
from fastapi_sqlalchemy import db

from app.solomon.transactions.domain.models import Transaction
from app.solomon.transactions.domain.options import Kinds


class TestTransactionsResources:
    def test_create_recurrent_transaction(
        self,
        auth_client,
        current_user,
        transaction_create_factory,
        category_factory,
    ):
        with db():
            category = category_factory.create()
            body = transaction_create_factory.build(
                kind=Kinds.PIX.value,
                is_fixed=True,
                date=None,
                recurring_day=4,
                user_id=current_user.id,
                category_id=category.id,
            ).model_dump()

            response = auth_client.post("/transactions/", json=body)
            result = response.json()["data"]

            assert response.status_code == 201
            assert result["description"] == body["description"]
            assert result["kind"] == body["kind"]
            assert result["is_fixed"] == body["is_fixed"]
            assert result["installments"] == []

    def test_create_credit_card_variable_transaction(
        self,
        auth_client,
        current_user,
        transaction_create_factory,
        category_factory,
        credit_card_factory,
    ):
        with db():
            category = category_factory.create()
            credit_card = credit_card_factory.create(user=current_user)
            body = transaction_create_factory.build(
                kind=Kinds.CREDIT.value,
                is_fixed=False,
                recurring_day=None,
                credit_card_id=credit_card.id,
                category_id=category.id,
                amount=300.00,
                installments_number=3,
                date=datetime.date(2023, 5, 1),
            ).model_dump()

            response = auth_client.post("/transactions/", json=jsonable_encoder(body))
            result = response.json()["data"]

            assert response.status_code == 201
            assert result["description"] == body["description"]
            assert result["kind"] == body["kind"]
            assert result["is_fixed"] == body["is_fixed"]
            assert len(result["installments"]) == 3
            assert result["installments"][0]["amount"] == 100.00
            assert result["installments"][0]["date"] == "2023-05-01"

    def test_create_invalid_credit_card_variable_transaction(
        self,
        auth_client,
        current_user,
        transaction_create_factory,
        category_factory,
        credit_card_factory,
    ):
        with db():
            category = category_factory.create()
            credit_card = credit_card_factory.create(user=current_user)
            body = transaction_create_factory.build(
                kind=Kinds.CREDIT.value,
                is_fixed=False,
                recurring_day=None,
                user_id=current_user.id,
                credit_card_id=credit_card.id,
                category_id=category.id,
                amount=300.00,
                installments_number=3,
                date=datetime.date(2023, 5, 1),
            ).model_dump()

            with patch(
                "app.solomon.transactions.infrastructure.repositories.TransactionRepository.create_with_installments",
                side_effect=Exception("Database Not Available"),
            ):
                response = auth_client.post(
                    "/transactions/", json=jsonable_encoder(body)
                )
                assert response.status_code == 500

    def test_get_transaction(
        self, auth_client, current_user, transaction_factory, installment_factory
    ):
        with db():
            transaction = transaction_factory.create(
                user=current_user, kind=Kinds.CREDIT.value, amount=300.00
            )
            installment_factory.create_batch(3, transaction=transaction)

            response = auth_client.get(f"/transactions/{transaction.id}/")
            result = response.json()["data"]
            installments = result["installments"]

            assert response.status_code == 200
            assert result["id"] == transaction.id
            assert result["description"] == transaction.description
            assert result["kind"] == transaction.kind
            assert result["is_fixed"] == transaction.is_fixed
            assert result["amount"] == transaction.amount
            assert len(installments) == 3

    def test_get_invalid_transaction(self, auth_client):
        with db():
            response = auth_client.get(f"/transactions/{uuid4()}/")
            result = response.json()

            assert response.status_code == 404
            assert result["detail"] == "Transaction not found."

    def test_get_transactions_without_pagination_params(
        self, auth_client, transaction_factory, current_user
    ):
        with db():
            transactions = transaction_factory.create_batch(2, user=current_user)

            response = auth_client.get("/transactions/")

            assert response.status_code == 200
            assert len(transactions) == 2

    def test_get_transactions_with_pagination(
        self, auth_client, transaction_factory, current_user
    ):
        with db():
            transactions = transaction_factory.create_batch(15, user=current_user)

            response = auth_client.get("/transactions/?page=2&size=5")
            meta = response.json()["meta"]
            data = response.json()["data"]

            assert response.status_code == 200
            assert len(transactions) == 15
            assert meta["page"] == 2
            assert meta["size"] == 5
            assert meta["total"] == 15
            assert len(data) == 5
            assert isinstance(data, list)

    def test_get_transactions_with_filters(
        self, auth_client, category_factory, transaction_factory, current_user
    ):
        with db():
            food_category = category_factory.create(description="Food")
            home_category = category_factory.create(description="Home")

            transaction_factory.create_batch(
                45,
                user=current_user,
                is_fixed=False,
                kind=Kinds.CREDIT.value,
                category=food_category,
                date=datetime.date(2023, 5, 1),
                is_revenue=False,
            )
            transaction_factory.create_batch(
                23,
                user=current_user,
                is_fixed=True,
                kind=Kinds.DEBIT.value,
                category=home_category,
                date=datetime.date(2023, 8, 15),
                is_revenue=False,
            )
            base_url = "/transactions/"
            params = {
                "kind__eq": "debit",
                "is_fixed__eq": "true",
                "category_id__eq": home_category.id,
                "date__gt": "2023-08-01",
                "date__lt": "2023-08-30",
                "is_revenue__eq": "false",
            }
            url = f"{base_url}?{urlencode(params)}"
            total_transactions = db.session.query(Transaction).count()

            response = auth_client.get(url)

            data = response.json()["data"]

            assert response.status_code == 200
            assert total_transactions == 68
            assert len(data) == 23
            for item in data:
                assert item["kind"] == "debit"
                assert item["is_fixed"] is True
                assert item["category_id"] == home_category.id
                assert datetime.date.fromisoformat(item["date"]) > datetime.date(
                    2023, 8, 1
                )
                assert datetime.date.fromisoformat(item["date"]) < datetime.date(
                    2023, 8, 30
                )
                assert item["is_revenue"] is False
