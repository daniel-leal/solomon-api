import uuid

from fastapi_sqlalchemy import db


class TestCreditCardsResources:
    def test_create_credit_card(self, auth_client):
        with db():
            body = {
                "name": "Credit Card",
                "limit": 1000.0,
                "invoice_start_day": 1,
            }

            response = auth_client.post("/credit-cards/", json=body)
            data = response.json()["data"]

            assert response.status_code == 201
            assert data == {
                "name": "Credit Card",
                "limit": 1000.0,
                "invoice_start_day": 1,
                "id": data["id"],
            }

    def test_create_invalid_credit_card(self, auth_client):
        with db():
            body = {}

            response = auth_client.post("/credit-cards/", json=body)

            assert response.status_code == 422

    def test_get_all_credit_cards(self, auth_client, current_user, credit_card_factory):
        with db():
            credit_card_factory.create_batch(3, user=current_user)
            credit_card_factory.create_batch(2)

            response = auth_client.get("/credit-cards/")
            data = response.json()["data"]

            assert response.status_code == 200
            assert len(data) == 3

    def test_get_credit_card(self, auth_client, current_user, credit_card_factory):
        with db():
            credit_card = credit_card_factory.create(user=current_user)

            response = auth_client.get(f"/credit-cards/{credit_card.id}")
            data = response.json()["data"]

            assert response.status_code == 200
            assert data == {
                "name": credit_card.name,
                "limit": credit_card.limit,
                "invoice_start_day": credit_card.invoice_start_day,
                "id": credit_card.id,
            }

    def test_get_credit_card_not_found(self, auth_client):
        with db():
            # Arrange
            non_existent_uuid = uuid.uuid4()

            # Act
            response = auth_client.get(f"/credit-cards/{non_existent_uuid}")

            # Assert
            assert response.status_code == 404

    def test_update_credit_card(self, auth_client, current_user, credit_card_factory):
        with db():
            # Arrange
            credit_card = credit_card_factory.create(user=current_user)
            body = {
                "name": "Updated Credit Card",
                "limit": 2000.0,
                "invoice_start_day": 2,
            }

            # Act
            response = auth_client.put(f"/credit-cards/{credit_card.id}", json=body)
            data = response.json()["data"]

            # Assert
            assert response.status_code == 200
            assert data == {
                "name": "Updated Credit Card",
                "limit": 2000.0,
                "invoice_start_day": 2,
                "id": credit_card.id,
            }

    def test_update_credit_card_not_found(self, auth_client):
        with db():
            # Arrange
            body = {
                "name": "Updated Credit Card",
                "limit": 2000.0,
                "invoice_start_day": 2,
            }
            non_existent_uuid = uuid.uuid4()

            # Act
            response = auth_client.put(f"/credit-cards/{non_existent_uuid}", json=body)

            # Assert
            assert response.status_code == 404

    def test_update_credit_card_invalid_body(
        self, auth_client, current_user, credit_card_factory
    ):
        with db():
            # Arrange
            credit_card = credit_card_factory.create(user=current_user)
            body = {
                "name": 123,  # Invalid type, should be a string
                "limit": "2000.0",  # Invalid type, should be a float
                "invoice_start_day": "2",  # Invalid type, should be an integer
            }

            # Act
            response = auth_client.put(f"/credit-cards/{credit_card.id}", json=body)

            # Assert
            assert response.status_code == 422

    def test_delete_credit_card(self, auth_client, current_user, credit_card_factory):
        with db():
            # Arrange
            credit_card = credit_card_factory.create(user=current_user)

            # Act
            response = auth_client.delete(f"/credit-cards/{credit_card.id}")

            # Assert
            assert response.status_code == 200

    def test_delete_credit_card_not_found(self, auth_client):
        with db():
            # Arrange
            non_existent_uuid = uuid.uuid4()

            # Act
            response = auth_client.delete(f"/credit-cards/{non_existent_uuid}")

            # Assert
            assert response.status_code == 404
