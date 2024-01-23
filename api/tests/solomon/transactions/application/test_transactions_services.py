import pytest

from api.solomon.transactions.application.services import CreditCardService
from api.solomon.transactions.domain.exceptions import CreditCardNotFound
from api.tests.solomon.factories.credit_card_factory import CreditCardFactory


class TestCreditCardService:
    def test_get_credit_card(self, credit_card_service, mock_repository):
        mock_user_id = "123"
        credit_card = CreditCardFactory.build()
        mock_repository.get_by_id.return_value = credit_card

        result = credit_card_service.get_credit_card("credit_card_id", mock_user_id)

        mock_repository.get_by_id.assert_called_once_with(
            id="credit_card_id", user_id=mock_user_id
        )
        assert result == credit_card

    def test_get_invalid_credit_card(self, credit_card_service, mock_repository):
        mock_user_id = "123"
        mock_repository.get_by_id.return_value = None

        with pytest.raises(CreditCardNotFound):
            credit_card_service.get_credit_card("invalid_id", mock_user_id)

            mock_repository.get_by_id.assert_called_once_with(
                id="invalid_id", user_id=mock_user_id
            )

    def test_get_credit_cards(self, credit_card_service, mock_repository):
        mock_user_id = "123"
        mock_credit_cards = [CreditCardFactory.build(), CreditCardFactory.build()]
        mock_repository.get_all.return_value = mock_credit_cards

        result = credit_card_service.get_credit_cards(mock_user_id)

        assert result == mock_credit_cards
        assert isinstance(result, list)
        assert len(result) == 2
        mock_repository.get_all.assert_called_once_with(user_id=mock_user_id)

    def test_create_credit_card(self, credit_card_service, mock_repository):
        mock_credit_card = CreditCardFactory.build()
        mock_repository.create.return_value = mock_credit_card

        result = credit_card_service.create_credit_card(
            user_id=mock_credit_card.user_id,
            name=mock_credit_card.name,
            limit=mock_credit_card.limit,
            invoice_start_day=mock_credit_card.invoice_start_day,
        )

        assert result == mock_credit_card
        mock_repository.create.assert_called_once_with(
            user_id=mock_credit_card.user_id,
            name=mock_credit_card.name,
            limit=mock_credit_card.limit,
            invoice_start_day=mock_credit_card.invoice_start_day,
        )

    def test_create_invalid_credit_card(self, credit_card_service, mock_repository):
        mock_credit_card = CreditCardFactory.build()
        mock_repository.create.return_value = None

        result = credit_card_service.create_credit_card(
            user_id=mock_credit_card.user_id,
            name=mock_credit_card.name,
            limit=mock_credit_card.limit,
            invoice_start_day=mock_credit_card.invoice_start_day,
        )

        assert result is None
        mock_repository.create.assert_called_once_with(
            user_id=mock_credit_card.user_id,
            name=mock_credit_card.name,
            limit=mock_credit_card.limit,
            invoice_start_day=mock_credit_card.invoice_start_day,
        )

    def test_update_credit_card(self, credit_card_service, mock_repository):
        # Arrange
        mock_credit_card = CreditCardFactory.build()
        new_name = "New name"
        mock_credit_card.name = new_name

        mock_repository.get_by_id.return_value = mock_credit_card
        mock_repository.update.return_value = mock_credit_card

        credit_card_service = CreditCardService(mock_repository)

        # Act
        updated_credit_card = credit_card_service.update_credit_card(
            mock_credit_card, mock_credit_card.user_id, name=new_name
        )

        # Assert
        assert updated_credit_card.name == new_name
        mock_repository.update.assert_called_once_with(mock_credit_card, name=new_name)

    def test_update_credit_card_not_found(self, credit_card_service, mock_repository):
        # Arrange
        mock_credit_card = CreditCardFactory.build()
        mock_credit_card.user_id = "test_user_id"
        mock_repository.get_by_id.return_value = None

        # Act and Assert
        with pytest.raises(CreditCardNotFound):
            credit_card_service.update_credit_card(
                mock_credit_card, mock_credit_card.user_id, name="New Name"
            )

    def test_delete_credit_card(self, credit_card_service, mock_repository):
        # Arrange
        mock_credit_card = CreditCardFactory.build()
        mock_credit_card.user_id = "test_user_id"
        mock_repository.get_by_id.return_value = mock_credit_card

        # Act
        deleted_credit_card = credit_card_service.delete_credit_card(
            mock_credit_card.id, mock_credit_card.user_id
        )

        # Assert
        assert deleted_credit_card == mock_credit_card
        mock_repository.delete.assert_called_once_with(credit_card=mock_credit_card)

    def test_delete_credit_card_not_found(self, credit_card_service, mock_repository):
        # Arrange
        mock_credit_card = CreditCardFactory.build()
        mock_credit_card.user_id = "test_user_id"
        mock_repository.get_by_id.return_value = None

        # Act and Assert
        with pytest.raises(CreditCardNotFound):
            credit_card_service.delete_credit_card(
                mock_credit_card.id, mock_credit_card.user_id
            )
