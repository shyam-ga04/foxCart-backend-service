from sqlalchemy import (
   Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Table, Text,event,DDL,text
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import enum
import uuid

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

class GstRate(Base):
    __tablename__ = "gst_rates"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=uuid.uuid4, index=True)
    description = Column(String(255))
    hsn_code = Column(String(10), unique=True, nullable=False)  # Ex: "8471" for laptops
    rate = Column(Float, nullable=False)  # GST percentage (e.g., 18.0)

    created_at = Column(DateTime, server_default=datetime.utcnow)
    updated_at = Column(DateTime, server_default=datetime.utcnow, server_onupdate=datetime.utcnow)



# ---------- USERS ----------
class Users(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True,index=True)  # user-provided UUID (uid)
    email = Column(String(255), unique=True)
    fcm_token = Column(String(255))
    full_name = Column(String(150))
    profile_pic = Column(String(255))
    role = Column(Enum(UserRole), server_default=UserRole.CUSTOMER)

    created_at = Column(DateTime, server_default=datetime.utcnow)
    updated_at = Column(DateTime, server_default=datetime.utcnow, server_onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    # relationships
    contacts = relationship("ContactDetail", back_populates="user", cascade="all, delete-orphan")
    locations = relationship("LocationDetail", back_populates="user", cascade="all, delete-orphan")
    cart = relationship("Cart", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Orders", back_populates="customer")
    vendor = relationship("Vendors", back_populates="owner", uselist=False)


# ---------- VENDOR SHOP TYPES ----------
class ShopType(Base):
    __tablename__ = "shop_types"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"), index=True)
    description = Column(Text)
    name = Column(String(100), unique=True, nullable=False)

    created_at = Column(DateTime, server_default=datetime.utcnow)
    updated_at = Column(DateTime, server_default=datetime.utcnow, server_onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    # relationships
    vendors = relationship("Vendors", secondary="vendor_shop_types", back_populates="shop_types")



vendor_shop_types = Table(
    "vendor_shop_types",
    Base.metadata,
    Column("vendor_id", UUID(as_uuid=True), ForeignKey("vendors.id", ondelete="CASCADE"), primary_key=True),
    Column("shop_type_id", UUID(as_uuid=True), ForeignKey("shop_types.id", ondelete="CASCADE"), primary_key=True),
)


# ---------- VENDORS ----------
class Vendors(Base):
    __tablename__ = "vendors"

    id = Column(UUID(as_uuid=True), primary_key=True,server_default=text("gen_random_uuid()"))  # user-provided UUID (uid)
    active = Column(Boolean, server_default=True) 
    description = Column(Text)
    gst_number = Column(String(50))
    brand_logo = Column(String(255))
    shop_name = Column(String(150), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, index=True)
    slug = Column(String(150), unique=True, nullable=False)
    website = Column(String(255))

    created_at = Column(DateTime, server_default=datetime.utcnow)
    updated_at = Column(DateTime, server_default=datetime.utcnow, server_onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    # relationships
    contacts = relationship("ContactDetail", back_populates="vendor", cascade="all, delete-orphan")
    locations = relationship("LocationDetail", back_populates="vendor", cascade="all, delete-orphan")
    orders = relationship("Orders", back_populates="vendor")
    owner = relationship("Users", back_populates="vendor")
    products = relationship("Products", back_populates="vendor")
    shop_types = relationship("ShopType", secondary="vendor_shop_types", back_populates="vendors")


# ---------- CONTACT DETAILS ----------
class ContactDetail(Base):
    __tablename__ = "contact_details"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"), index=True)
    contact_type = Column(String(50), nullable=False)
    is_primary = Column(Boolean, server_default=False)
    phone_number = Column(String(255), nullable=False)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id", ondelete="CASCADE"), index=True)

    created_at = Column(DateTime, server_default=datetime.utcnow)
    updated_at = Column(DateTime, server_default=datetime.utcnow, server_onupdate=datetime.utcnow)
        
    # relationships
    user = relationship("Users", back_populates="contacts")
    vendor = relationship("Vendors", back_populates="contacts")


# ---------- LOCATION DETAILS ----------
class LocationDetail(Base):
    __tablename__ = "location_details"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"), index=True)
    address_line1 = Column(String(255), nullable=False)
    address_line2 = Column(String(255))
    city = Column(String(100))
    country = Column(String(100))
    label = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    postal_code = Column(String(20))
    state = Column(String(100))

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id", ondelete="CASCADE"), index=True)

    created_at = Column(DateTime, server_default=datetime.utcnow)
    updated_at = Column(DateTime, server_default=datetime.utcnow, server_onupdate=datetime.utcnow)

    # relationships
    user = relationship("Users", back_populates="locations")
    vendor = relationship("Vendors", back_populates="locations")
    
# ---------- SHOPPING CARTS ----------
class Cart(Base):
    __tablename__ = "carts"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, server_default=datetime.utcnow)
    updated_at = Column(DateTime, server_default=datetime.utcnow, server_onupdate=datetime.utcnow)

    # Relationships
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    user = relationship("Users", back_populates="carts")

# ---------- CART ITEMS ----------
class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    cart_id = Column(UUID(as_uuid=True), ForeignKey("carts.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, server_default=1)
    created_at = Column(DateTime, server_default=datetime.utcnow)
    updated_at = Column(DateTime, server_default=datetime.utcnow, server_onupdate=datetime.utcnow)

    # Relationships
    cart = relationship("Cart", back_populates="items")
    product = relationship("Products")


# ---------- PRODUCT CATEGORIES ----------
class ProductCategory(Base):
    __tablename__ = "product_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"), index=True)
    description = Column(Text)
    name = Column(String(100), unique=True, nullable=False)

    created_at = Column(DateTime, server_default=datetime.utcnow)
    updated_at = Column(DateTime, server_default=datetime.utcnow, server_onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    # relationships
    parent = relationship("ProductCategory", remote_side=[id], back_populates="subcategories")
    subcategories = relationship("ProductCategory", back_populates="parent")
    products = relationship("Products", back_populates="category")


# ---------- PRODUCTS ----------
class Products(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"), index=True)
    active = Column(Boolean, server_default=True)
    base_price = Column(Float, nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("product_categories.id", ondelete="SET NULL"), index=True)
    description = Column(Text)
    gst_rate_id = Column(UUID(as_uuid=True), ForeignKey("gst_rates.id"), nullable=False)
    image_url = Column(String(255))
    name = Column(String(200), nullable=False)
    product_metadata = Column(JSON)
    stock = Column(Integer, server_default=0)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id", ondelete="CASCADE"), index=True)

    created_at = Column(DateTime, server_default=datetime.utcnow)
    updated_at = Column(DateTime, server_default=datetime.utcnow, server_onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    # relationships
    vendor = relationship("Vendors", back_populates="products")
    category = relationship("ProductCategory", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    vector = relationship("ProductVector", back_populates="product", uselist=False)

# ---------- PRODUCT VECTORS ----------
class ProductVector(Base):
    __tablename__ = "product_vectors"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"), index=True)
    embedding = Column(Text, nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), unique=True, index=True)

    created_at = Column(DateTime, server_default=datetime.utcnow)
    updated_at = Column(DateTime, server_default=datetime.utcnow, server_onupdate=datetime.utcnow)
    
    product = relationship("Products", back_populates="vector")

# ---------- ORDERS ----------
class Orders(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"), index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id", ondelete="CASCADE"), index=True)
    status = Column(Enum(OrderStatus), server_default=OrderStatus.PENDING)
    subtotal_amount = Column(Float, nullable=False)  # Before tax
    discount_amount = Column(Float, server_default=0.0)
    invoice_amount = Column(Float, nullable=False)  # subtotal - discount + tax
    final_amount = Column(Float, nullable=False)  # Amount paid (after refunds, etc.)
    
    # GST Snapshot
    gst_rate = Column(Float, nullable=False, server_default=0.0)  # Avg or applied GST %
    cgst_amount = Column(Float, server_default=0.0)
    sgst_amount = Column(Float, server_default=0.0)
    igst_amount = Column(Float, server_default=0.0)
    total_tax_amount = Column(Float, server_default=0.0)

    created_at = Column(DateTime, server_default=datetime.utcnow)
    updated_at = Column(DateTime, server_default=datetime.utcnow, server_onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    vendor = relationship("Vendors", back_populates="orders")
    customer = relationship("Users", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    tracking_events = relationship("OrderTracking", back_populates="order", cascade="all, delete-orphan")
    refund_requests = relationship("OrderRefundRequests", back_populates="order", cascade="all, delete-orphan")

# ---------- ORDER ITEMS ----------
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"), index=True)
    discount_amount = Column(Float, server_default=0.0)
    discount_percentage = Column(Float, server_default=0.0)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    invoice_amount = Column(Float, nullable=False)
    
    # GST Snapshot
    gst_rate = Column(Float, nullable=False, server_default=0.0)  # Avg or applied GST %
    cgst_amount = Column(Float, server_default=0.0)
    sgst_amount = Column(Float, server_default=0.0)
    igst_amount = Column(Float, server_default=0.0)
    total_tax_amount = Column(Float, server_default=0.0)
    
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"), index=True)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)

    created_at = Column(DateTime, server_default=datetime.utcnow)
    updated_at = Column(DateTime, server_default=datetime.utcnow, server_onupdate=datetime.utcnow)
    
    order = relationship("Orders", back_populates="items")
    product = relationship("Products", back_populates="order_items")

# ---------- PAYMENTS ----------
class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"), index=True)
    amount = Column(Float, nullable=False)
    method = Column(String(50), nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    status = Column(String(50), server_default="pending")
    transaction_id = Column(String(100), unique=True)

    created_at = Column(DateTime, server_default=datetime.utcnow)
    updated_at = Column(DateTime, server_default=datetime.utcnow, server_onupdate=datetime.utcnow)

    order = relationship("Orders", back_populates="payments")

# ---------- ORDER TRACKING ----------
class OrderTracking(Base):
    __tablename__ = "order_tracking"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"), index=True)
    location_id = Column(UUID(as_uuid=True), ForeignKey("location_details.id"), nullable=False, index=True)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    note = Column(Text)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    status = Column(String(50), nullable=False)

    created_at = Column(DateTime, server_default=datetime.utcnow,)
    updated_at = Column(DateTime, server_default=datetime.utcnow, server_onupdate=datetime.utcnow)
    
    order = relationship("Orders", back_populates="tracking_events")

class RefundStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REFUNDED = "refunded"

class OrderRefundRequests(Base):
    __tablename__ = "order_refund_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"), index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    processed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    reason = Column(Text, nullable=True)
    refund_amount = Column(Float, nullable=True)
    status = Column(Enum(RefundStatus), server_default=RefundStatus.PENDING, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    created_at = Column(DateTime, server_default=datetime.utcnow)
    updated_at = Column(DateTime, server_default=datetime.utcnow, server_onupdate=datetime.utcnow)

    # Relationships
    order = relationship("Orders", back_populates="refund_requests")
    user = relationship("Users", foreign_keys=[user_id])
    processor = relationship("Users", foreign_keys=[processed_by])
    

# ---------- RLS POLICIES ----------
def add_rls_policies(target, connection, **kw):
    policies = [
        # USERS
        """
        ALTER TABLE users ENABLE ROW LEVEL SECURITY;
        
        CREATE POLICY "Users can view their own profile"
        ON users FOR SELECT USING (id = auth.uid());
        
        CREATE POLICY "Users can modify their own profile"
        ON users FOR UPDATE USING (id = auth.uid());
        
        CREATE POLICY "Users can delete their own profile"
        ON users FOR DELETE USING (id = auth.uid());
        """,
        # SHOP_TYPES
        """
        ALTER TABLE shop_types ENABLE ROW LEVEL SECURITY;
        
        CREATE POLICY "Anyone can view shop types"
        ON shop_types FOR SELECT
        USING (true);
        """
        # VENDORS
        """
        ALTER TABLE vendors ENABLE ROW LEVEL SECURITY;
        
        CREATE POLICY "Users can view their own profile"
        ON vendors FOR SELECT USING (owner_id = auth.uid());
        
        CREATE POLICY "Users can modify their own profile"
        ON vendors FOR UPDATE USING (owner_id = auth.uid());
        
        CREATE POLICY "Users can delete their own profile"
        ON vendors FOR DELETE USING (owner_id = auth.uid());
        """,
        # CONTACT_DETAILS
        """
        ALTER TABLE contact_details ENABLE ROW LEVEL SECURITY;
        
        CREATE POLICY "Users can view and manage their contacts"
        ON contact_details FOR ALL
        USING (user_id = auth.uid() OR vendor_id IN (SELECT id FROM vendors WHERE owner_id = auth.uid()))
        WITH CHECK (user_id = auth.uid() OR vendor_id IN (SELECT id FROM vendors WHERE owner_id = auth.uid()));
        """
        # LOCATION_DETAILS
        """
        ALTER TABLE location_details ENABLE ROW LEVEL SECURITY;
        
        CREATE POLICY "Users can view and manage their locations "
        ON location_details FOR ALL
        USING (user_id = auth.uid() OR vendor_id IN (SELECT id FROM vendors WHERE owner_id = auth.uid()))
        WITH CHECK (user_id = auth.uid() OR vendor_id IN (SELECT id FROM vendors WHERE owner_id = auth.uid()));
        """
        # PRODUCTS
        """
        ALTER TABLE products ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "Vendors manage their products"
        ON products FOR ALL USING (vendor_id IN (SELECT id FROM vendors WHERE owner_id = auth.uid()));
        
        CREATE POLICY "Anyone can view active products"
        ON products FOR SELECT USING (active = true);
        """,
        # PRODUCT CATEGORIES
        """
        ALTER TABLE product_categories ENABLE ROW LEVEL SECURITY;
        
        CREATE POLICY "Anyone can view categories"
        ON product_categories FOR SELECT
        USING (true);
        """
        # PRODUCT VECTORS
        """
        ALTER TABLE product_vectors ENABLE ROW LEVEL SECURITY;
        
        CREATE POLICY "Anyone can view vectors for active products"
        ON product_vectors FOR SELECT
        USING (product_id IN (SELECT id FROM products WHERE active = true));
        
        CREATE POLICY "Vendors manage their product vectors"
        ON product_vectors FOR ALL
        USING (product_id IN (SELECT id FROM products WHERE vendor_id IN (SELECT id FROM vendors WHERE owner_id = auth.uid())))
        WITH CHECK (product_id IN (SELECT id FROM products WHERE vendor_id IN (SELECT id FROM vendors WHERE owner_id = auth.uid())));
        """
        # ORDERS
        """
        ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
        
        CREATE POLICY "Customers see their orders"
        ON orders FOR SELECT
        USING (customer_id = auth.uid());
        
        CREATE POLICY "Customers can create orders"
        ON orders FOR INSERT
        WITH CHECK (customer_id = auth.uid());
        
        CREATE POLICY "Vendors see their shop orders"
        ON orders FOR SELECT
        USING (vendor_id IN (SELECT id FROM vendors WHERE owner_id = auth.uid()));
        
        CREATE POLICY "Vendors Modify their shop orders"
        ON orders FOR UPDATE
        USING (vendor_id IN (SELECT id FROM vendors WHERE owner_id = auth.uid()));
        """
        # ORDER_ITEM
        """
        ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "Order owners can view and modify items"
        ON order_items FOR ALL
        USING (order_id IN (SELECT id FROM orders WHERE customer_id = auth.uid()
        OR vendor_id IN (SELECT id FROM vendors WHERE owner_id = auth.uid())));
        """
        # PAYMENTS
        """
        ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
        
        CREATE POLICY "Order owners can view payments"
        ON payments FOR SELECT
        USING (order_id IN (SELECT id FROM orders WHERE customer_id = auth.uid()
        OR vendor_id IN (SELECT id FROM vendors WHERE owner_id = auth.uid())));

        CREATE POLICY "Customers can create payments for their orders"
        ON payments FOR INSERT
        WITH CHECK (order_id IN (SELECT id FROM orders WHERE customer_id = auth.uid()));
        
        CREATE POLICY "Order owners can modify payments"
        ON payments FOR UPDATE
        USING (order_id IN (SELECT id FROM orders WHERE customer_id = auth.uid()
        OR vendor_id IN (SELECT id FROM vendors WHERE owner_id = auth.uid())));
        """
        # ORDER_TRACKING
        """
        ALTER TABLE order_tracking ENABLE ROW LEVEL SECURITY;
        
        CREATE POLICY "Customers see tracking for their orders"
        ON order_tracking FOR SELECT
        USING (order_id IN (SELECT id FROM orders WHERE customer_id = auth.uid()));

        CREATE POLICY "Vendors update tracking for their orders"
        ON order_tracking FOR ALL
        USING (order_id IN (SELECT id FROM orders WHERE vendor_id IN (SELECT id FROM vendors WHERE owner_id = auth.uid())))
        WITH CHECK (order_id IN (SELECT id FROM orders WHERE vendor_id IN (SELECT id FROM vendors WHERE owner_id = auth.uid())));
        """
        # ORDER_REFUND_REQUESTS
        """
        ALTER TABLE order_refund_requests ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "Users can create refund requests"
        ON order_refund_requests
        FOR INSERT
        WITH CHECK (user_id = auth.uid());

        CREATE POLICY "Users can view their refund requests"
        ON order_refund_requests
        FOR SELECT
        USING (user_id = auth.uid());

        CREATE POLICY "Vendors can view refund requests for their orders"
        ON order_refund_requests
        FOR SELECT
        USING (
        EXISTS (
            SELECT 1
            FROM orders o
            JOIN vendors v ON v.id = o.vendor_id
            WHERE o.id = order_refund_requests.order_id
            AND v.owner_id = auth.uid()
        )
        );

        CREATE POLICY "Vendors can update refund requests for their orders"
        ON order_refund_requests
        FOR UPDATE
        USING (
        EXISTS (
            SELECT 1
            FROM orders o
            JOIN vendors v ON v.id = o.vendor_id
            WHERE o.id = order_refund_requests.order_id
            AND v.owner_id = auth.uid()
        )
        );
        """
        # CARTS
        """
        ALTER TABLE carts ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "Users can view and modify their own cart"
        ON carts FOR ALL USING (user_id = auth.uid());
        """,
        # CART_ITEMS
        """
        ALTER TABLE cart_items ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "Users can view and modify their cart items"
        ON cart_items FOR ALL
        USING (EXISTS (SELECT 1 FROM carts WHERE carts.id = cart_items.cart_id AND carts.user_id = auth.uid()));
        """,
        # GST_RATES
        """
        ALTER TABLE gst_rates ENABLE ROW LEVEL SECURITY;
        
        CREATE POLICY "Anyone can view GST Rates"
        ON gst_rates FOR SELECT
        USING (true);
        """
    ]
    for sql in policies:
        connection.execute(DDL(sql))


# Attach the RLS policy creation after tables are created
event.listen(Base.metadata, "after_create", add_rls_policies)
