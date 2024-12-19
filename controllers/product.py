import os

from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, Form, Query
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from core import get_db_session
from models import ProductMapper, ProductImageMapper
from schemas import ProductSchemaOut
from typing import List, Optional

from services import IsAuthenticated, IsAdmin
from utils import save_file

router = APIRouter(prefix="/products", tags=["PRODUCT"])


@router.get(
    "", response_model=List[ProductSchemaOut], dependencies=[Depends(IsAuthenticated())]
)
async def get_all(
    name_filter: Optional[str] = None,
    category_filter: Optional[str] = None,
    max_price_filter: Optional[float] = Query(
        None, description="Takes precedence over equal and min filter"
    ),
    equal_to_price_filter: Optional[float] = Query(
        None, description="Takes precedence over min filter"
    ),
    min_price_filter: Optional[float] = None,
    session: Session = Depends(get_db_session),
):
    """
    Retrieve a list of products with optional filtering.

    This function allows users to fetch products based on optional filters such as name, category, and price.
    The function ensures that price filters are applied according to their precedence (max price takes priority over equal or min price).

    Args:
        name_filter (Optional[str], optional): Filter products by name.
        category_filter (Optional[str], optional): Filter products by category.
        max_price_filter (Optional[float], optional): Filter products with a price less than or equal to the specified value. Takes precedence over other price filters.
        equal_to_price_filter (Optional[float], optional): Filter products with a price equal to the specified value. Takes precedence over min price filter.
        min_price_filter (Optional[float], optional): Filter products with a price greater than or equal to the specified value.
        session (Session, optional): The database session to interact with the database.

    Dependencies:
        IsAuthenticated: A dependency that checks if the user is authenticated.

    Returns:
        List[ProductSchemaOut]: A list of products filtered by the provided criteria.
    """
    return ProductMapper.get_filtered_products(
        session=session,
        name_filter=name_filter,
        category_filter=category_filter,
        max_price_filter=max_price_filter,
        equal_to_price_filter=equal_to_price_filter,
        min_price_filter=min_price_filter,
    )


@router.get(
    "/{id}", response_model=ProductSchemaOut, dependencies=[Depends(IsAuthenticated())]
)
async def get(
    id: int,
    session: Session = Depends(get_db_session),
):
    """
    Retrieve a specific product by its ID.

    This function fetches a product from the database using its unique identifier.
    If the product is not found, it raises a 404 HTTP exception.

    Args:
        id (int): The unique identifier of the product.
        session (Session): The database session to interact with the database.

    Dependencies:
        IsAuthenticated: A dependency that checks if the user is authenticated.

    Raises:
        HTTPException: Raised if the product with the given ID is not found.

    Returns:
        ProductSchemaOut: The product data corresponding to the provided ID.
    """
    product = ProductMapper.get_by_id(session=session, pk_id=id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    return product


@router.post("", response_model=ProductSchemaOut, dependencies=[Depends(IsAdmin())])
async def create(
    name: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    description: str = Form(None),
    thumbnail: UploadFile | None = None,
    mobile: UploadFile | None = None,
    tablet: UploadFile | None = None,
    desktop: UploadFile | None = None,
    session: Session = Depends(get_db_session),
):
    """
    Create a new product in the system.

    This function allows an admin user to create a new product with its details and associated images.
    Uploaded files for the product images are saved, and their references are stored in the database.

    Args:
        name (str): The name of the product.
        price (float): The price of the product.
        category (str): The category to which the product belongs.
        description (str, optional): A brief description of the product.
        thumbnail (UploadFile, optional): Thumbnail image file for the product.
        mobile (UploadFile, optional): Mobile version image file for the product.
        tablet (UploadFile, optional): Tablet version image file for the product.
        desktop (UploadFile, optional): Desktop version image file for the product.
        session (Session): The database session to interact with the database.

    Dependencies:
        IsAdmin: A dependency that ensures only admin users can access this endpoint.

    Returns:
        ProductSchemaOut: The created product data, including the associated images.
    """
    images_obj = {
        "thumbnail": save_file(thumbnail),
        "mobile": save_file(mobile),
        "tablet": save_file(tablet),
        "desktop": save_file(desktop),
    }
    images = ProductImageMapper.create(session=session, data=images_obj)
    product_obj = {
        "name": name,
        "price": price,
        "category": category,
        "description": description,
        "image_id": images.id,
    }
    return ProductMapper.create(session=session, data=product_obj)


@router.put("/{id}", response_model=ProductSchemaOut, dependencies=[Depends(IsAdmin())])
async def update(
    id: int,
    name: str = Form(None),
    price: float = Form(None),
    category: str = Form(None),
    description: str = Form(None),
    thumbnail: UploadFile | None = None,
    mobile: UploadFile | None = None,
    tablet: UploadFile | None = None,
    desktop: UploadFile | None = None,
    session: Session = Depends(get_db_session),
):
    """
    Update an existing product's details and associated images.

    This function allows an admin user to update the details of an existing product, including its name,
    price, category, description, and associated images. Updated image files are saved and their references
    updated in the database.

    Args:
        id (int): The ID of the product to update.
        name (str, optional): The new name of the product.
        price (float, optional): The new price of the product.
        category (str, optional): The new category of the product.
        description (str, optional): The new description of the product.
        thumbnail (UploadFile, optional): The new thumbnail image file for the product.
        mobile (UploadFile, optional): The new mobile version image file for the product.
        tablet (UploadFile, optional): The new tablet version image file for the product.
        desktop (UploadFile, optional): The new desktop version image file for the product.
        session (Session): The database session to interact with the database.

    Dependencies:
        IsAdmin: A dependency that ensures only admin users can access this endpoint.

    Returns:
        ProductSchemaOut: The updated product data, including the associated images.

    Raises:
        HTTPException: If the product with the given ID is not found.
    """
    product = ProductMapper.get_by_id(session=session, pk_id=id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    images = ProductImageMapper.get_by_id(session=session, pk_id=product.image_id)
    images.thumbnail = save_file(thumbnail)
    images.mobile = save_file(mobile)
    images.tablet = save_file(tablet)
    images.desktop = save_file(desktop)
    product.name = name if name else product.name
    product.price = price if price else product.price
    product.category = category if category else product.category
    product.description = description if description else product.description
    session.commit()
    session.refresh(images)
    session.refresh(product)
    return product


@router.get("/images/{filename}", dependencies=[Depends(IsAuthenticated())])
async def read_image(filename: str):
    """
    Retrieve an image file by its filename.

    This function allows authenticated users to retrieve image files stored in the `assets/images` directory.
    The filename is provided as a path parameter. If the file does not exist, a 404 HTTP exception is raised.

    Args:
        filename (str): The name of the image file to retrieve.

    Dependencies:
        IsAuthenticated: A dependency that ensures only authenticated users can access this endpoint.

    Returns:
        FileResponse: The requested image file.

    Raises:
        HTTPException: If the file with the given filename is not found.
    """
    file_path = f"assets/images/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )
    return FileResponse(file_path)


@router.delete("/{product_id}", dependencies=[Depends(IsAdmin())])
async def delete(
    product_id: int,
    session: Session = Depends(get_db_session),
):
    """
    Delete a product by its ID.

    This function allows an admin user to delete a product by its ID. If the product does not exist, a 404
    HTTP exception is raised.

    Args:
        product_id (int): The ID of the product to delete.
        session (Session): The database session to interact with the database.

    Dependencies:
        IsAdmin: A dependency that ensures only admin users can access this endpoint.

    Returns:
        int: HTTP 204 status code indicating that the product has been successfully deleted.

    Raises:
        HTTPException: If the product with the given ID is not found.
    """
    product = ProductMapper.get_by_id(session=session, pk_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    ProductMapper.delete(session=session, pk_id=product.id)
    return status.HTTP_204_NO_CONTENT
