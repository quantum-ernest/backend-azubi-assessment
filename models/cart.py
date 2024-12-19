from sqlalchemy import ForeignKey, select, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship, Session
from models import Base


class CartItemMapper(Base):
    __tablename__ = "cart_item"
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id", ondelete="SET NULL")
    )
    quantity: Mapped[int] = mapped_column(default=1)

    user_rel: Mapped["UserMapper"] = relationship(back_populates="shopping_cart_rel")
    product_rel: Mapped["ProductMapper"] = relationship(
        back_populates="shopping_cart_rel"
    )

    __table_args__ = (UniqueConstraint("product_id", "user_id"),)

    @classmethod
    def get_all_by_user_id(cls, session: Session, user_id: int):
        return session.scalars(select(cls).filter_by(user_id=user_id)).all()

    @classmethod
    def get_by_user_id(cls, session: Session, user_id: int, product_id: int):
        return session.scalars(
            select(cls).filter_by(user_id=user_id, product_id=product_id)
        ).first()
