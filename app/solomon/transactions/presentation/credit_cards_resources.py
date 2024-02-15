from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.solomon.auth.application.security import get_current_user
from app.solomon.auth.presentation.models import (
    UserTokenAuthenticated,
)
from app.solomon.transactions.application.dependencies import (
    get_credit_card_service,
)
from app.solomon.transactions.application.services import (
    CreditCardService,
)
from app.solomon.transactions.domain.exceptions import CreditCardNotFound
from app.solomon.transactions.presentation.models import (
    CreditCard,
    CreditCardCreate,
    CreditCardResponseMapper,
    CreditCardsResponseMapper,
    CreditCardUpdate,
)

credit_card_router = APIRouter()


@credit_card_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def create_credit_card(
    credit_card: CreditCardCreate,
    credit_card_service: CreditCardService = Depends(get_credit_card_service),
    current_user: UserTokenAuthenticated = Depends(get_current_user),
) -> CreditCardResponseMapper:
    """
    Create a new credit card.

    This function receives a CreditCardCreate object and a CreditCardService instance,
    then tries to create a new credit card using the provided service.

    Parameters
    ----------
    credit_card : CreditCardCreate
        The credit card to be created.
    credit_card_service : CreditCardService, optional
        The service to be used to create the credit card, by default
        Depends(get_credit_card_service)
    current_user: UserTokenAuthenticated
        user logged in

    Returns
    -------
    JSONResponse
        The created credit card with a 201 status code.
    """
    credit_card_created = credit_card_service.create_credit_card(
        **credit_card.model_dump(), user_id=current_user.id
    )

    return CreditCardResponseMapper.create(credit_card_created)


@credit_card_router.get("/", response_model=CreditCardsResponseMapper)
async def get_all_credit_cards(
    credit_card_service: CreditCardService = Depends(get_credit_card_service),
    current_user: UserTokenAuthenticated = Depends(get_current_user),
) -> CreditCardsResponseMapper:
    """
    Get all credit cards.

    This function receives a CreditCardService instance and tries to get all credit
    cards using the provided service.

    Parameters
    ----------
    credit_card_service : CreditCardService, optional
        The service to be used to get all credit cards, by default
        Depends(get_credit_card_service)
    current_user: UserTokenAuthenticated
        user logged in

    Returns
    -------
    JSONResponse
        The list of credit cards with a 200 status code.
    """
    credit_cards = credit_card_service.get_credit_cards(user_id=current_user.id)
    return CreditCardsResponseMapper.create(credit_cards)


@credit_card_router.get(
    "/{credit_card_id}", response_model=CreditCardResponseMapper
)
async def get_credit_card(
    credit_card_id: str,
    credit_card_service: CreditCardService = Depends(get_credit_card_service),
    current_user: UserTokenAuthenticated = Depends(get_current_user),
) -> CreditCardResponseMapper:
    """
    Get a specific credit card by its ID.

    Parameters
    ----------
    credit_card_id : str
        The ID of the credit card to retrieve.
    credit_card_service : CreditCardService
        The service to use to retrieve the credit card
    current_user : UserTokenAuthenticated
        The current user, by default Depends(get_current_user)

    Returns
    -------
    Response
        The requested credit card with a 200 status code.
    """
    try:
        credit_card = credit_card_service.get_credit_card(
            credit_card_id=credit_card_id, user_id=current_user.id
        )
        return CreditCardResponseMapper.create(credit_card)
    except CreditCardNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@credit_card_router.delete(
    "/{credit_card_id}",
    response_model=CreditCardResponseMapper,
    status_code=status.HTTP_200_OK,
)
async def delete_credit_card(
    credit_card_id: str,
    credit_card_service: CreditCardService = Depends(get_credit_card_service),
    current_user: UserTokenAuthenticated = Depends(get_current_user),
) -> CreditCardResponseMapper:
    """
    Delete a credit card.

    This function deletes a credit card from the database.
    The user must be authenticated to delete a credit card.

    Parameters
    ----------
    credit_card_id : str
        The ID of the credit card to delete.
    credit_card_service : CreditCardService, optional
        The service to use for credit card operations. By default, it uses the service
        returned by `get_credit_card_service`.
    current_user : UserTokenAuthenticated
        The currently authenticated user. By default, it uses the user returned by
        `get_current_user`.

    Returns
    -------
    Response
        A response object indicating the result of the deletion operation.
    """
    try:
        credit_card = credit_card_service.delete_credit_card(
            credit_card_id=credit_card_id, user_id=current_user.id
        )
        return CreditCardResponseMapper.create(credit_card)
    except CreditCardNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@credit_card_router.put(
    "/{credit_card_id}", response_model=CreditCardResponseMapper
)
async def update_credit_card(
    credit_card_id: str,
    credit_card_update: CreditCardUpdate,
    credit_card_service: CreditCardService = Depends(get_credit_card_service),
    current_user: UserTokenAuthenticated = Depends(get_current_user),
) -> CreditCardResponseMapper:
    """
    Update a credit card.

    This function updates a credit card in the database.
    The user must be authenticated to update a credit_card.

    Parameters
    ----------
    credit_card_id : str
        The ID of the credit card to update.
    credit_card_update : CreditCardUpdateSchema
        The new data for the credit card.
    credit_card_service : CreditCardService, optional
        The service to use for credit card operations. By default, it uses the service
        returned by `get_credit_card_service`.
    current_user : UserTokenAuthenticated, optional
        The currently authenticated user. By default, it uses the user returned by
        `get_current_user`.

    Returns
    -------
    CreditCard
        The updated credit card.
    """
    try:
        updated_credit_card = credit_card_service.update_credit_card(
            credit_card_id=credit_card_id,
            user_id=current_user.id,
            **credit_card_update.model_dump(exclude_none=True),
        )
        return CreditCardResponseMapper.create(updated_credit_card)
    except CreditCardNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
