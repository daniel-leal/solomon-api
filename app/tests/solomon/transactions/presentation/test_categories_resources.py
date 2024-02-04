from uuid import uuid4

from fastapi_sqlalchemy import db


class TestCategoriesResources:
    def test_get_all_categories(self, client, category_factory):
        with db():
            # Arrange
            category_factory.create_batch(2)

            # Act
            response = client.get("/categories")

            # Assert
            assert response.status_code == 200
            assert len(response.json()) == 2

    def test_get_category(self, client, category_factory):
        with db():
            # Arrange
            category = category_factory.create()

            # Act
            response = client.get(f"/categories/{category.id}")
            data = response.json()["data"]

            # Assert
            assert response.status_code == 200
            assert data == {
                "id": category.id,
                "description": category.description,
            }

    def test_get_category_not_found(self, client):
        with db():
            invalid_id = uuid4()

            response = client.get(f"/categories/{invalid_id}")

            assert response.status_code == 404
            assert response.json() == {
                "detail": "Category not found.",
            }
