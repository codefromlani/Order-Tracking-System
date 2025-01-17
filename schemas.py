from pydantic import BaseModel, EmailStr
from typing import List, Optional
from enum import Enum
from datetime import datetime


class ProductBase(BaseModel):
    name: str
    description: str
    price: float


class ProductCreate(ProductBase):
    stock: int = 0
    category: str
    vendor_id: int
    is_deleted: Optional[bool] = False


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category: Optional[str] = None
    vendor_id: Optional[int] = None


class VendorBase(BaseModel):
    name: str


class ProductResponse(ProductCreate):
    id: int
    vendor: VendorBase

    class Config:
        from_attributes = True


class VendorCreate(VendorBase):
    email: EmailStr
    phone_number: str
    address: str
    type: str
    is_deleted: Optional[bool] = False


class VendorResponse(VendorCreate):
    id: int
    products: List[ProductBase]

    class Config:
        from_attributes = True 


class VendorUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None


class ClientCreate(BaseModel):
    name: str
    email: EmailStr
    phone_number: str
    is_deleted: Optional[bool] = False


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None


class ClientResponse(ClientCreate):
    pass

    class Config:
        from_attributes = True 


class OrderStatusEnum(str, Enum):
    PENDING = "pending"
    APPROVED = "approved" 
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderBase(BaseModel):
    status: OrderStatusEnum
    total_amount: float = 0


class ClientOrderResponse(OrderBase):
    id: int
    products: List[ProductBase]

    class Config:
        from_attributes = True 


class OrderProductCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    client_id: int
    products: List[OrderProductCreate]


class OrderResponse(BaseModel):
    id: int
    client_id: int
    total_amount: float
    status: OrderStatusEnum
    payment_intent: str
    products: List[OrderProductCreate]

    class Config:
        from_attributes = True 


class ActionEnum(str, Enum):
    ADD = "add"
    REMOVE = "remove"
    UPDATE = "update"


class OrderUpdate(OrderProductCreate):
    product_id: Optional[int] = None
    quantity: Optional[int] = None
    action: Optional[ActionEnum]


class OrderUpdateResponse(BaseModel):
    products: Optional[List[OrderUpdate]] = None  # List of product updates (add/remove/change)


class OrderHistory(BaseModel):
    # id: int
    order_id: int
    status: OrderStatusEnum
    changed_at: datetime

    class Config:
        from_attributes = True


class InvoiceStatusEnum(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class InvoiceResponse(BaseModel):
    id: int
    order_id: int
    amount: float
    status: InvoiceStatusEnum
    due_date: datetime


class InvoiceUpdate(BaseModel):
    amount: Optional[float] = None
    status: Optional[InvoiceStatusEnum] = None
    due_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class ExpensecategoryEnum(str, Enum):
    SHIPPING = "shipping"
    SUPPLIES = "supplies"
    MATERIALS = "materials"
    OTHER = "other"


class ExpenseCreate(BaseModel):
    category: ExpensecategoryEnum
    amount: float
    description: str


class ExpenseUpdate(BaseModel):
    category: Optional[ExpensecategoryEnum] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    date: Optional[datetime] = datetime.utcnow()


class ExpenseResponse(ExpenseCreate):
    id: int
    date: datetime

    class Config:
       from_attributes = True


class ShipmentStatusEnum(str, Enum):
    PENDING = "pending"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    RETURNED = "returned"


class ShipmentUpdate(BaseModel):
    status: Optional[ShipmentStatusEnum] = None
    tracking_number: Optional[str] = None
    estimated_delivery_date: Optional[datetime] = None

    class Config:
        from_attributes = True