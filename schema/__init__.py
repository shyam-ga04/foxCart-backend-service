from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, text,event,DDL
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()

# ---------- BASE MIXIN ----------
class BaseMixin:
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"), index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, server_default=text("true"))

# ---------- ENUM TABLES ----------
class UserRoles(Base):
    __tablename__ = "enum_user_roles"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"), index=True)
    name = Column(String(50), unique=True, nullable=False)  # e.g. "customer", "vendor", "delivery_boy", "admin"
    description = Column(String(255))


class OrderStatuses(Base):
    __tablename__ = "enum_order_status"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"), index=True)
    name = Column(String(50), unique=True, nullable=False)  # e.g. "pending", "preparing", "delivered"
    description = Column(String(255))


class RefundStatuses(Base):
    __tablename__ = "enum_refund_status"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"), index=True)
    name = Column(String(50), unique=True, nullable=False)  # e.g. "pending", "approved", "rejected"
    description = Column(String(255))

# ---------- USERS ----------
class Users(Base, BaseMixin):
    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(150))
    profile_pic = Column(String(255))
    phone_number = Column(String(50))
    role_id = Column(String(500), ForeignKey("enum_user_roles.name", ondelete="SET NULL"), index=True)
    fcm_token = Column(String(255))

    # Vendor-specific
    business_name = Column(String(255))
    gst_number = Column(String(50))
    license_number = Column(String(100))
    vendor_description = Column(Text)
    vendor_website = Column(Text)
    shop_open_time = Column(String(20))
    shop_close_time = Column(String(20))
    avg_preparation_time = Column(Integer)
    min_order_value = Column(Float, server_default=text("0.0"))
    is_verified_vendor = Column(Boolean, server_default=text("false"))
    rating = Column(Float, server_default=text("0.0"))
    total_orders_completed = Column(Integer, server_default=text("0"))
    vendor_status = Column(String(50), server_default="active")

    # Relationships
    role = relationship("UserRoles")
    contacts_locations = relationship("UserContactLocation", back_populates="user", cascade="all, delete-orphan")
    products = relationship("Products", back_populates="vendor", foreign_keys="Products.vendor_id")
    orders = relationship("Orders", back_populates="customer", foreign_keys="Orders.customer_id")
    deliveries = relationship("Orders", back_populates="delivery_agent", foreign_keys="Orders.delivery_agent_id")
    delivery_assignments = relationship("DeliveryAssignment", back_populates="delivery_boy", foreign_keys="DeliveryAssignment.delivery_boy_id")
    vendor_assignments = relationship("DeliveryAssignment", back_populates="vendor", foreign_keys="DeliveryAssignment.vendor_id")

# ---------- CONTACT + LOCATION ----------
class UserContactLocation(Base, BaseMixin):
    __tablename__ = "user_contact_locations"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    label = Column(String(100))
    is_default = Column(Boolean, server_default=text("false"))
    phone_number = Column(String(50))
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)

    user = relationship("Users", back_populates="contacts_locations")

# ---------- GST RATES ----------
class GstRate(Base, BaseMixin):
    __tablename__ = "gst_rates"

    description = Column(String(255))
    hsn_code = Column(String(10), unique=True, nullable=False)
    rate = Column(Float, nullable=False)

# ---------- PRODUCT CATEGORIES ----------
class ProductCategory(Base, BaseMixin):
    __tablename__ = "product_categories"

    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("product_categories.id"), nullable=True)

    parent = relationship("ProductCategory", remote_side="ProductCategory.id", back_populates="subcategories")
    subcategories = relationship("ProductCategory", back_populates="parent")
    products = relationship("Products", back_populates="category")

# ---------- PRODUCTS ----------
class Products(Base, BaseMixin):
    __tablename__ = "products"

    vendor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("product_categories.id", ondelete="SET NULL"), index=True)
    gst_rate_id = Column(UUID(as_uuid=True), ForeignKey("gst_rates.id"), nullable=False)

    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    image_url = Column(String(255))
    base_price = Column(Float, nullable=False)
    stock = Column(Integer, server_default=text("0"))
    product_metadata = Column(JSON)

    vendor = relationship("Users", back_populates="products", foreign_keys=[vendor_id])
    category = relationship("ProductCategory", back_populates="products")
    gst = relationship("GstRate")
    order_items = relationship("OrderItem", back_populates="product")
    

# ---------- PRODUCT REVIEWS ----------
class ProductReview(Base, BaseMixin):
    __tablename__ = "product_reviews"
    
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    rating = Column(Integer)
    comment = Column(Text)


# ---------- DELIVERY BOY LIST ----------
class DeliveryBoyList(Base, BaseMixin):
    __tablename__ = "delivery_boy_list"

    vendor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    full_name = Column(Text, nullable=False)
    phone_number = Column(String(50), nullable=False)
    vehicle_number = Column(String(50))
    available_for_delivery = Column(Boolean, server_default=text("true"))

    vendor = relationship("Users", back_populates="vendor_assignments", foreign_keys=[vendor_id])

# ---------- DELIVERY BOY ↔ VENDOR ----------
class DeliveryAssignment(Base, BaseMixin):
    __tablename__ = "delivery_assignments"

    vendor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    delivery_boy_id = Column(UUID(as_uuid=True), ForeignKey("delivery_boy_list.id", ondelete="CASCADE"), index=True)
    full_name = Column(Text, nullable=False)
    phone_number = Column(String(50), nullable=False)
    vehicle_number = Column(String(50))
    current_latitude = Column(Float)
    current_longitude = Column(Float)

    vendor = relationship("Users", back_populates="vendor_assignments", foreign_keys=[vendor_id])
    delivery_boy = relationship("DeliveryBoyList", back_populates="vendor")

# ---------- ORDERS ----------
class Orders(Base, BaseMixin):
    __tablename__ = "orders"

    customer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    delivery_agent_id = Column(UUID(as_uuid=True), ForeignKey("delivery_boy_list.id", ondelete="SET NULL"), index=True)
    status_id = Column(UUID(as_uuid=True), ForeignKey("enum_order_status.id", ondelete="SET NULL"), index=True)

    subtotal_amount = Column(Float, nullable=False)
    discount_amount = Column(Float, server_default=text("0.0"))
    final_amount = Column(Float, nullable=False)
    platform = Column(String(50))
    gst_rate = Column(Float, nullable=False, server_default=text("0.0"))
    cgst_amount = Column(Float, server_default=text("0.0"))
    sgst_amount = Column(Float, server_default=text("0.0"))
    total_tax_amount = Column(Float, server_default=text("0.0"))

    customer = relationship("Users", back_populates="orders", foreign_keys=[customer_id])
    vendor = relationship("Users", foreign_keys=[vendor_id])
    delivery_agent = relationship("DeliveryBoyList", foreign_keys=[delivery_agent_id])
    status = relationship("OrderStatuses")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    tracking_events = relationship("OrderTracking", back_populates="order", cascade="all, delete-orphan")
    refund_requests = relationship("OrderRefundRequests", back_populates="order", cascade="all, delete-orphan")

# ---------- ORDER ITEMS ----------
class OrderItem(Base, BaseMixin):
    __tablename__ = "order_items"

    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"), index=True)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    discount_amount = Column(Float, server_default=text("0.0"))
    gst_rate = Column(Float, nullable=False, server_default=text("0.0"))
    total_tax_amount = Column(Float, server_default=text("0.0"))

    order = relationship("Orders", back_populates="items")
    product = relationship("Products", back_populates="order_items")

# ---------- PAYMENTS ----------
class Payment(Base, BaseMixin):
    __tablename__ = "payments"

    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    amount = Column(Float, nullable=False)
    method = Column(String(50), nullable=False)
    status = Column(String(50), server_default="pending")
    payment_order_id = Column(String(255), unique=True)
    payment_id = Column(String(255), unique=True)
    gateway_name = Column(String(255))

    order = relationship("Orders", back_populates="payments")

# ---------- ORDER TRACKING ----------
class OrderTracking(Base, BaseMixin):
    __tablename__ = "order_tracking"

    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    status_id = Column(UUID(as_uuid=True), ForeignKey("enum_order_status.id", ondelete="SET NULL"))
    note = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    eta_minutes = Column(Integer)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    delivery_agent_id = Column(UUID(as_uuid=True), ForeignKey("delivery_boy_list.id"), nullable=True)

    order = relationship("Orders", back_populates="tracking_events")
    status = relationship("OrderStatuses")
    delivery_agent = relationship("DeliveryBoyList", foreign_keys=[delivery_agent_id])

# ---------- REFUND REQUESTS ----------
class OrderRefundRequests(Base, BaseMixin):
    __tablename__ = "order_refund_requests"

    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    processed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reason = Column(Text)
    refund_amount = Column(Float)
    status_id = Column(UUID(as_uuid=True), ForeignKey("enum_refund_status.id", ondelete="SET NULL"))

    order = relationship("Orders", back_populates="refund_requests")
    status = relationship("RefundStatuses")
    
    
# ---------- RLS POLICIES ----------
def add_rls_policies(target, connection, **kw):
    policies = [

        # USERS
        """
        ALTER TABLE users ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "Users can view their own profile"
        ON users FOR SELECT USING (id = auth.uid());

        CREATE POLICY "Users can update their own profile"
        ON users FOR UPDATE USING (id = auth.uid());

        CREATE POLICY "Users can delete their own profile"
        ON users FOR DELETE USING (id = auth.uid());
        """,

        # USER_CONTACT_LOCATIONS
        """
        ALTER TABLE user_contact_locations ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "Users manage their own contact locations"
        ON user_contact_locations FOR ALL
        USING (user_id = auth.uid())
        WITH CHECK (user_id = auth.uid());
        """,

        # PRODUCT_CATEGORIES
        """
        ALTER TABLE product_categories ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "Anyone can view product categories"
        ON product_categories FOR SELECT
        USING (true);
        """,

        # GST_RATES
        """
        ALTER TABLE gst_rates ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "Anyone can view GST rates"
        ON gst_rates FOR SELECT
        USING (true);
        """,

        # PRODUCTS
        """
        ALTER TABLE products ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "Vendors manage their products"
        ON products FOR ALL
        USING (vendor_id = auth.uid())
        WITH CHECK (vendor_id = auth.uid());

        CREATE POLICY "Anyone can view active products"
        ON products FOR SELECT
        USING (active = true);
        """,

        # DELIVERY_BOY_LIST
        """
        ALTER TABLE delivery_boy_list ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "Vendors manage their delivery boy list"
        ON delivery_boy_list FOR ALL
        USING (vendor_id = auth.uid())
        WITH CHECK (vendor_id = auth.uid());
        """,

        # DELIVERY_ASSIGNMENTS
        """
        ALTER TABLE delivery_assignments ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "Vendors manage their delivery assignments"
        ON delivery_assignments FOR ALL
        USING (vendor_id = auth.uid())
        WITH CHECK (vendor_id = auth.uid());

        CREATE POLICY "Delivery boy can view assigned deliveries"
        ON delivery_assignments FOR SELECT
        USING (delivery_boy_id IN (
            SELECT id FROM delivery_boy_list WHERE vendor_id = auth.uid()
        ));
        """,

        # ORDERS
        """
        ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "Customers view their own orders"
        ON orders FOR SELECT
        USING (customer_id = auth.uid());

        CREATE POLICY "Vendors view orders for their shop"
        ON orders FOR SELECT
        USING (vendor_id = auth.uid());

        CREATE POLICY "Delivery agents view their assigned orders"
        ON orders FOR SELECT
        USING (delivery_agent_id IN (
            SELECT id FROM delivery_boy_list WHERE vendor_id = auth.uid()
        ));

        CREATE POLICY "Customers can create orders"
        ON orders FOR INSERT
        WITH CHECK (customer_id = auth.uid());

        CREATE POLICY "Vendors update their orders"
        ON orders FOR UPDATE
        USING (vendor_id = auth.uid())
        WITH CHECK (vendor_id = auth.uid());
        """,

        # ORDER_ITEMS
        """
        ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "Order owners manage their order items"
        ON order_items FOR ALL
        USING (order_id IN (
            SELECT id FROM orders WHERE customer_id = auth.uid()
            OR vendor_id = auth.uid()
        ));
        """,

        # PAYMENTS
        """
        ALTER TABLE payments ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "Order owners view payments"
        ON payments FOR SELECT
        USING (order_id IN (
            SELECT id FROM orders WHERE customer_id = auth.uid()
            OR vendor_id = auth.uid()
        ));

        CREATE POLICY "Customers create payments for their orders"
        ON payments FOR INSERT
        WITH CHECK (order_id IN (
            SELECT id FROM orders WHERE customer_id = auth.uid()
        ));
        """,

        # ORDER_TRACKING
        """
        ALTER TABLE order_tracking ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "Customers view tracking for their orders"
        ON order_tracking FOR SELECT
        USING (order_id IN (
            SELECT id FROM orders WHERE customer_id = auth.uid()
        ));

        CREATE POLICY "Vendors update tracking for their orders"
        ON order_tracking FOR ALL
        USING (order_id IN (
            SELECT id FROM orders WHERE vendor_id = auth.uid()
        ))
        WITH CHECK (order_id IN (
            SELECT id FROM orders WHERE vendor_id = auth.uid()
        ));

        CREATE POLICY "Delivery boys update their assigned tracking"
        ON order_tracking FOR UPDATE
        USING (delivery_agent_id IN (
            SELECT id FROM delivery_boy_list WHERE vendor_id = auth.uid()
        ));
        """,

        # ORDER_REFUND_REQUESTS
        """
        ALTER TABLE order_refund_requests ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "Users can create refund requests"
        ON order_refund_requests FOR INSERT
        WITH CHECK (user_id = auth.uid());

        CREATE POLICY "Users can view their refund requests"
        ON order_refund_requests FOR SELECT
        USING (user_id = auth.uid());

        CREATE POLICY "Vendors view refund requests related to their orders"
        ON order_refund_requests FOR SELECT
        USING (
            EXISTS (
                SELECT 1 FROM orders o
                WHERE o.id = order_refund_requests.order_id
                AND o.vendor_id = auth.uid()
            )
        );

        CREATE POLICY "Vendors update refund requests for their orders"
        ON order_refund_requests FOR UPDATE
        USING (
            EXISTS (
                SELECT 1 FROM orders o
                WHERE o.id = order_refund_requests.order_id
                AND o.vendor_id = auth.uid()
            )
        );
        """,
    ]

    for sql in policies:
        connection.execute(DDL(sql))


# Attach the RLS policy creation after tables are created
event.listen(Base.metadata, "after_create", add_rls_policies)
