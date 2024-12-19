from pydantic import EmailStr
from sqlalchemy.orm import Mapped, mapped_column, Session, relationship
from sqlalchemy import select, ForeignKey, UniqueConstraint
from models import Base


class UserMapper(Base):
    __tablename__ = "user"
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    password: Mapped[str]
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"))
    role_rel: Mapped["RoleMapper"] = relationship(back_populates="user_rel")
    shopping_cart_rel: Mapped["CartItemMapper"] = relationship(
        back_populates="user_rel"
    )

    __table_args__ = (UniqueConstraint("email", "name", name="unique_email_name"),)

    @classmethod
    def get_by_email(cls, session: Session, email: EmailStr):
        return session.scalars(select(cls).where(cls.email == email)).first()

    @classmethod
    def update_password(cls, session: Session, user, password: str):
        user.password = password
        session.commit()
        session.refresh(user)
        return user
