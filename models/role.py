from sqlalchemy.orm import mapped_column, Mapped, relationship, Session
from sqlalchemy import select, UniqueConstraint
from models import Base
from models.user import UserMapper


class RoleMapper(Base):
    __tablename__ = "role"
    name: Mapped[str] = mapped_column(unique=True)
    user_rel: Mapped["UserMapper"] = relationship(back_populates="role_rel")

    __table_args__ = (UniqueConstraint("name", name="unique_name"),)

    @classmethod
    def get_role_by_name(cls, session: Session, name: str):
        return session.scalars(select(cls).where(cls.name == name)).first()
