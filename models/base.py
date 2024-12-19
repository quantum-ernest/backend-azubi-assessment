from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy import select, insert, delete
from datetime import datetime


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    @classmethod
    def get_all(cls, session: Session):
        return session.scalars(select(cls).order_by(cls.id.desc())).all()

    @classmethod
    def get_by_id(cls, session: Session, pk_id):
        return session.scalars(select(cls).where(cls.id == pk_id)).first()

    @classmethod
    def create(cls, session: Session, **kwargs):
        data = kwargs.get("data")
        record = session.scalars(insert(cls).returning(cls), data).first()
        session.commit()
        return record

    @classmethod
    def delete(cls, session: Session, pk_id):
        session.execute(delete(cls).where(cls.id == pk_id))
        session.commit()
        return True
