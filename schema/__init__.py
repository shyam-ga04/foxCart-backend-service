from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Enum, Table,JSON
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()


# ---------- ENUMS ----------
class UserRole(enum.Enum):
    VENDOR = "vendor"
    CUSTOMER = "customer"

class OrderStatus(enum.Enum):
    PENDING = "pending"
    SHIPPED = "shipped"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


# ---------- USERS ----------
class AppUser(Base):
    __tablename__ = "app_users"

    id = Column(String, primary_key=True)  # UUID from Supabase auth.users
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER)
    vendor = relationship("Vendor", back_populates="owner", uselist=False)
    orders = relationship("Order", back_populates="customer")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ---------- VENDOR SHOP TYPES ----------
class ShopType(Base):
    __tablename__ = "shop_types"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # e.g., Pharmacy, Electronics
    description = Column(Text, nullable=True)
    vendors = relationship(
        "Vendor",
        secondary="vendor_shop_types",
        back_populates="shop_types"
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


vendor_shop_types = Table(
    "vendor_shop_types",
    Base.metadata,
    Column("vendor_id", Integer, ForeignKey("vendors.id", ondelete="CASCADE"), primary_key=True),
    Column("shop_type_id", Integer, ForeignKey("shop_types.id", ondelete="CASCADE"), primary_key=True),
)


# ---------- VENDORS ----------
class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(150), nullable=False)
    slug = Column(String(150), unique=True, nullable=False)
    logo = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    active = Column(Boolean, default=True)
    owner_id = Column(String, ForeignKey("app_users.id"), unique=True)
    owner = relationship("AppUser", back_populates="vendor")

    products = relationship("Product", back_populates="vendor")
    orders = relationship("Order", back_populates="vendor")
    shop_types = relationship(
        "ShopType",
        secondary="vendor_shop_types",
        back_populates="vendors"
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ---------- PRODUCT CATEGORIES (hierarchy supported) ----------
class ProductCategory(Base):
    __tablename__ = "product_categories"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("product_categories.id"), nullable=True)
    parent = relationship("ProductCategory", remote_side=[id], back_populates="subcategories")
    subcategories = relationship("ProductCategory", back_populates="parent")
    products = relationship("Product", back_populates="category")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ---------- PRODUCTS ----------
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    image_url = Column(String(255), nullable=True)
    active = Column(Boolean, default=True)
    product_metadata = Column(JSON, nullable=True)  # custom attributes
    vendor_id = Column(Integer, ForeignKey("vendors.id", ondelete="CASCADE"))
    vendor = relationship("Vendor", back_populates="products")
    category_id = Column(Integer, ForeignKey("product_categories.id", ondelete="SET NULL"))
    category = relationship("ProductCategory", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    vector = relationship("ProductVector", back_populates="product", uselist=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ---------- PRODUCT VECTORS ----------
class ProductVector(Base):
    __tablename__ = "product_vectors"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), unique=True)
    embedding = Column(Text, nullable=False)  # In Supabase: VECTOR(dims)
    product = relationship("Product", back_populates="vector")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ---------- ORDERS ----------
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    subtotal_amount = Column(Float, nullable=False)
    discount_percentage = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    tax_percentage = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    invoice_amount = Column(Float, nullable=False)
    customer_id = Column(String, ForeignKey("app_users.id"))
    customer = relationship("AppUser", back_populates="orders")
    vendor_id = Column(Integer, ForeignKey("vendors.id", ondelete="CASCADE"))
    vendor = relationship("Vendor", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    payment = relationship("Payment", back_populates="order", uselist=False)
    tracking_events = relationship("OrderTracking", back_populates="order")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ---------- ORDER ITEMS ----------
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    discount_percentage = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    tax_percentage = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total_price = Column(Float, nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"))
    order = relationship("Order", back_populates="items")
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"))
    product = relationship("Product", back_populates="order_items")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ---------- PAYMENTS ----------
class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    amount = Column(Float, nullable=False)
    method = Column(String(50), nullable=False)
    status = Column(String(50), default="pending")
    transaction_id = Column(String(100), unique=True, nullable=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), unique=True)
    order = relationship("Order", back_populates="payment")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ---------- ORDER TRACKING ----------
class OrderTracking(Base):
    __tablename__ = "order_tracking"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"))
    status = Column(String(50), nullable=False)   # pending, shipped, etc.
    location = Column(String(255), nullable=True) # optional
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    order = relationship("Order", back_populates="tracking_events")
