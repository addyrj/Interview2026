"""SQLAlchemy 2.x ORM query example on in-memory SQLite: models, joins, aggregates, N+1."""
from datetime import datetime

from sqlalchemy import ForeignKey, create_engine, func, select
from sqlalchemy.orm import (DeclarativeBase, Mapped, Session, mapped_column,
                            relationship, selectinload)


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(index=True)
    city: Mapped[str]
    orders: Mapped[list["Order"]] = relationship(back_populates="customer")


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    amount: Mapped[int]  # rupees
    status: Mapped[str] = mapped_column(default="paid")
    customer: Mapped[Customer] = relationship(back_populates="orders")


def seed(s: Session) -> None:
    a, b, c = Customer(name="Asha", city="Pune"), Customer(name="Ravi", city="Delhi"), Customer(name="Zoya", city="Pune")
    s.add_all([a, b, c])
    s.add_all([Order(customer=a, amount=500), Order(customer=a, amount=1500),
               Order(customer=b, amount=700, status="refunded"), Order(customer=b, amount=300)])
    s.commit()


def main() -> None:
    engine = create_engine("sqlite://")  # in-memory
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        seed(s)

        # 1. filter + order + limit
        stmt = select(Order).where(Order.amount > 400, Order.status == "paid").order_by(Order.amount.desc()).limit(5)
        print([o.amount for o in s.scalars(stmt)])

        # 2. join + group by + having
        stmt = (select(Customer.name, func.count(Order.id), func.sum(Order.amount))
                .join(Order).group_by(Customer.id).having(func.sum(Order.amount) > 500)
                .order_by(func.sum(Order.amount).desc()))
        print(s.execute(stmt).all())

        # 3. outer join: customers with no orders
        stmt = select(Customer.name).outerjoin(Order).where(Order.id.is_(None))
        print(s.scalars(stmt).all())

        # 4. eager loading avoids N+1
        stmt = select(Customer).options(selectinload(Customer.orders)).order_by(Customer.id)
        print({c.name: len(c.orders) for c in s.scalars(stmt)})

        # 5. update + delete via ORM
        order = s.get(Order, 3)
        order.status = "paid"
        s.commit()
        print(s.scalar(select(func.sum(Order.amount)).where(Order.status == "paid")))

        # 6. subquery: customers whose total is above average order total
        totals = select(Order.customer_id, func.sum(Order.amount).label("t")).group_by(Order.customer_id).subquery()
        avg_t = select(func.avg(totals.c.t)).scalar_subquery()
        stmt = select(Customer.name).join(totals, totals.c.customer_id == Customer.id).where(totals.c.t > avg_t)
        print(s.scalars(stmt).all())

        # 7. count queries to prove N+1 vs eager
        queries: list[str] = []
        from sqlalchemy import event
        event.listen(engine, "before_cursor_execute", lambda *a: queries.append(a[2]))
        for c in s.scalars(select(Customer)):  # lazy load per customer
            _ = c.orders
        lazy = len(queries)
        queries.clear()
        s.expire_all()
        for c in s.scalars(select(Customer).options(selectinload(Customer.orders))):
            _ = c.orders
        print("lazy queries:", lazy, "eager queries:", len(queries))
        assert lazy == 4 and len(queries) == 2
    print("all ok")


if __name__ == "__main__":
    main()
