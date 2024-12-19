from sqlalchemy import ForeignKey, select
from typing import Optional
from models import Base
from sqlalchemy.orm import Mapped, relationship, mapped_column, Session


class ProductImageMapper(Base):
    __tablename__ = "product_image"
    thumbnail: Mapped[Optional[str]]
    mobile: Mapped[Optional[str]]
    tablet: Mapped[Optional[str]]
    desktop: Mapped[Optional[str]]
    product_rel: Mapped["ProductMapper"] = relationship(back_populates="image")


class ProductMapper(Base):
    __tablename__ = "product"
    name: Mapped[str]
    price: Mapped[float]
    category: Mapped[str]
    description: Mapped[Optional[str]]
    image_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("product_image.id", ondelete="SET NULL")
    )
    image: Mapped["ProductImageMapper"] = relationship(back_populates="product_rel")
    shopping_cart_rel: Mapped["CartItemMapper"] = relationship(
        back_populates="product_rel"
    )

    @classmethod
    def get_filtered_products(
        cls,
        session: Session,
        name_filter,
        category_filter,
        max_price_filter,
        equal_to_price_filter,
        min_price_filter,
    ):
        query = select(cls)
        if name_filter:
            query = query.filter(cls.name == name_filter)
        if category_filter:
            query = query.filter(cls.category == category_filter)
        if max_price_filter:
            query = query.filter(cls.price < max_price_filter)
        elif equal_to_price_filter:
            query = query.filter(cls.price == equal_to_price_filter)
        elif min_price_filter:
            query = query.filter(cls.price < min_price_filter)
        return session.scalars(query.order_by(cls.id.desc())).all()
