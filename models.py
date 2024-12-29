from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, Boolean
from database import Base
from sqlalchemy import Enum as SQLAlchemyEnum
from enum import Enum
from datetime import datetime
from sqlalchemy.orm import relationship


class Vendor(Base):
    __tablename__ = "vendors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    phone_number = Column(String)
    address = Column(String)
    type = Column(String)

    products = relationship("Product", back_populates="vendor")

    def __repr__(self):
        return f"<Vendor(name={self.name}, email={self.email})>"


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String,unique=True, nullable=False, index=True)
    description = Column(String)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    category = Column(String)
    vender_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)

    vendor = relationship("Vendor", back_populates="products")

    def __repr__(self):
        return f"<Product(name={self.name}, price={self.price}, vendor_id={self.vender_id})>"

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    phone_number = Column(String)

    orders = relationship("Order", back_populates="client")

    def __repr__(self):
        return f"<Client(name={self.name}, email={self.email})>"


class OrderStatusEnum(str, Enum):
    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    status = Column(SQLAlchemyEnum(OrderStatusEnum), nullable=False, index=True, default=OrderStatusEnum.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float, nullable=False)

    client = relationship("Client", back_populates="orders")
    shipments = relationship("Shipment", back_populates="order")
    invoices = relationship("Invoice", back_populates="order")

    def __repr__(self):
        return f"<Order(client_id={self.client_id}, status={self.status}, total_amount={self.total_amount})>"


class ExpensecategoryEnum(str, Enum):
    SHIPPING = "shipping"
    SUPPLIES = "supplies"
    MATERIALS = "materials"
    OTHER = "other"


class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(SQLAlchemyEnum(ExpensecategoryEnum), nullable=False, index=True)
    amount = Column(Float)
    description = Column(Text)
    date = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Expense(category={self.category}, amount={self.amount})>"
    

class ShipmentStatusEnum(str, Enum):
    PENDING = "pending"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    RETURNED = "returned"


class Shipment(Base):
    __tablename__ = "shipments"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    tracking_number = Column(String(100))
    status = Column(SQLAlchemyEnum(ShipmentStatusEnum), nullable=False, index=True, default=ShipmentStatusEnum.PENDING)
    estimated_delivery_date = Column(DateTime)

    order = relationship("Order", back_populates="shipments")

    def __repr__(self):
        return f"<Shipment(order_id={self.order_id}, tracking_number={self.tracking_number})>"


class InvoiceStatusEnum(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    amount = Column(Float)
    status = Column(SQLAlchemyEnum(InvoiceStatusEnum), nullable=False, index=True, default=InvoiceStatusEnum.PENDING)
    due_date = Column(DateTime)

    order = relationship("Order", back_populates="invoices")

    def __repr__(self):
        return f"<Invoice(order_id={self.order_id}, amount={self.amount})>"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<User(username={self.username})>"


class OrderProduct(Base):
    __tablename__ = "order_product"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    price = Column(Float, nullable=False)

    order = relationship("Order", backref="order_product")
    product = relationship("Product", backref="order_product")