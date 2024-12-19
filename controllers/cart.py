from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from core import get_db_session
from models import CartItemMapper, ProductMapper
from schemas import CartItemSchemaOut, CartItemSchemaIn
from services import IsAuthenticated

router = APIRouter(prefix="/cart", tags=["SHOPPING CART"])


@router.get("", response_model=List[CartItemSchemaOut])
async def get(
    session: Session = Depends(get_db_session),
    auth_user: dict = Depends(IsAuthenticated()),
):
    """
    Retrieve all cart items for the authenticated user.

    This function fetches all items in the shopping cart associated with the authenticated user. The user's
    ID is retrieved from the authentication token.

    Args:
        session (Session): The database session to interact with the database.
        auth_user (dict): The authenticated user's details, extracted from the token.

    Dependencies:
        IsAuthenticated: A dependency that ensures only authenticated users can access this endpoint.

    Returns:
        List[CartItemSchemaOut]: A list of cart items associated with the authenticated user.
    """
    return CartItemMapper.get_all_by_user_id(
        session=session, user_id=auth_user["user_id"]
    )


@router.post("", response_model=CartItemSchemaOut)
async def create(
    data: CartItemSchemaIn,
    session: Session = Depends(get_db_session),
    auth_user: dict = Depends(IsAuthenticated()),
):
    """
    Add a product to the authenticated user's shopping cart.

    This function either creates a new cart item for the specified product or updates the quantity
    of an existing cart item if the product is already in the user's cart.

    Args:
        data (CartItemSchemaIn): The input data containing the product ID and quantity.
        session (Session): The database session to interact with the database.
        auth_user (dict): The authenticated user's details, extracted from the token.

    Dependencies:
        IsAuthenticated: Ensures only authenticated users can access this endpoint.

    Returns:
        CartItemSchemaOut: The cart item that was added or updated.

    Raises:
        HTTPException: If the specified product does not exist.
    """
    product = ProductMapper.get_by_id(session=session, pk_id=data.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    cart_item = CartItemMapper.get_by_user_id(
        session=session, product_id=data.product_id, user_id=auth_user["user_id"]
    )
    if cart_item:
        cart_item.quantity += data.quantity
        session.commit()
        session.refresh(cart_item)
        return cart_item
    cart_item_obj = data.model_dump()
    cart_item_obj.update(
        {
            "user_id": auth_user["user_id"],
        }
    )
    return CartItemMapper.create(session=session, data=cart_item_obj)


@router.put("/{id}", response_model=CartItemSchemaOut)
async def update(
    id: int,
    data: CartItemSchemaIn,
    session: Session = Depends(get_db_session),
    auth_user: dict = Depends(IsAuthenticated()),
):
    """
    Update the quantity of a cart item for the authenticated user.

    This function updates the quantity of a product in the user's cart if the product exists.

    Args:
        id (int): The ID of the cart item to update.
        data (CartItemSchemaIn): The input data containing the updated quantity and product ID.
        session (Session): The database session to interact with the database.
        auth_user (dict): The authenticated user's details, extracted from the token.

    Dependencies:
        IsAuthenticated: Ensures only authenticated users can access this endpoint.

    Returns:
        CartItemSchemaOut: The updated cart item.

    Raises:
        HTTPException: If the cart or the specified cart item does not exist.
    """
    cart = CartItemMapper.get_by_id(session=session, pk_id=id)
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found"
        )

    cart_item = CartItemMapper.get_by_user_id(
        session=session, product_id=data.product_id, user_id=auth_user["user_id"]
    )
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    cart_item.quantity = data.quantity
    session.commit()
    session.refresh(cart_item)
    return cart_item


@router.delete("/{product_id}")
async def delete(
    product_id: int,
    session: Session = Depends(get_db_session),
    auth_user: dict = Depends(IsAuthenticated()),
):
    """
    Remove a product from the authenticated user's shopping cart.

    This function deletes a product from the user's cart if the product exists.

    Args:
        product_id (int): The ID of the product to remove.
        session (Session): The database session to interact with the database.
        auth_user (dict): The authenticated user's details, extracted from the token.

    Dependencies:
        IsAuthenticated: Ensures only authenticated users can access this endpoint.

    Returns:
        status.HTTP_204_NO_CONTENT: HTTP status code indicating successful deletion.

    Raises:
        HTTPException: If the specified cart item does not exist.
    """
    cart_item = CartItemMapper.get_by_user_id(
        session=session, product_id=product_id, user_id=auth_user["user_id"]
    )
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    CartItemMapper.delete(session=session, pk_id=cart_item.id)
    return status.HTTP_204_NO_CONTENT
