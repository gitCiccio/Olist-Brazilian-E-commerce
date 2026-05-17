from sqlalchemy import (
    Column, String, Float, Integer, DateTime, SmallInteger,
    ForeignKey, Text, Numeric
)

from sqlalchemy.orm import relationship, DeclarativeBase

class Base(DeclarativeBase):
    pass

class CategoryTranslation(Base):
    __tablename__ = 'category_translation'
    product_category_name = Column(String(100), primary_key=True)
    product_category_name_english = Column(String(100), nullable=True)
    product = relationship("Product", back_populates="category")

class Geolocation(Base):
    __tablename__ = 'geolocation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    geolocation_zip_code_prefix = Column(String(10), nullable=False, index=True)
    geolocation_lat = Column(Float, nullable=True)
    geolocation_lng = Column(Float, nullable=True)
    geolocation_city = Column(String(100), nullable=True)
    geolocation_state = Column(String(2), nullable=True)

class Customer(Base):
    __tablename__ = "customers"
    customer_id               = Column(String(50), primary_key=True)
    customer_unique_id        = Column(String(50), nullable=False, index=True)
    customer_zip_code_prefix  = Column(String(10), nullable=True)
    customer_city             = Column(String(100), nullable=True)
    customer_state            = Column(String(2), nullable=True)
    orders = relationship("Order", back_populates="customer")

class Seller(Base):
    __tablename__ = "sellers"
    seller_id               = Column(String(50), primary_key=True)
    seller_zip_code_prefix  = Column(String(10), nullable=True)
    seller_city             = Column(String(100), nullable=True)
    seller_state            = Column(String(2), nullable=True)
    order_items = relationship("OrderItem", back_populates="seller")

class Product(Base):
    __tablename__ = "products"
    product_id                  = Column(String(50), primary_key=True)
    product_category_name       = Column(String(100), ForeignKey("category_translation.product_category_name"), nullable=True)
    product_name_length         = Column(Integer, nullable=True)
    product_description_length  = Column(Integer, nullable=True)
    product_photos_qty          = Column(Integer, nullable=True)
    product_weight_g            = Column(Float, nullable=True)
    product_length_cm           = Column(Float, nullable=True)
    product_height_cm           = Column(Float, nullable=True)
    product_width_cm            = Column(Float, nullable=True)
    category    = relationship("CategoryTranslation", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")

class Order(Base):
    __tablename__ = "orders"
    order_id                      = Column(String(50), primary_key=True)
    customer_id                   = Column(String(50), ForeignKey("customers.customer_id"), nullable=False, index=True)
    order_status                  = Column(String(30), nullable=True)
    order_purchase_timestamp      = Column(DateTime, nullable=True)
    order_approved_at             = Column(DateTime, nullable=True)
    order_delivered_carrier_date  = Column(DateTime, nullable=True)
    order_delivered_customer_date = Column(DateTime, nullable=True)
    order_estimated_delivery_date = Column(DateTime, nullable=True)
    customer    = relationship("Customer", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")
    payments    = relationship("OrderPayment", back_populates="order")
    reviews     = relationship("OrderReview", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    order_id            = Column(String(50), ForeignKey("orders.order_id"), primary_key=True)
    order_item_id       = Column(Integer, primary_key=True)
    product_id          = Column(String(50), ForeignKey("products.product_id"), nullable=False, index=True)
    seller_id           = Column(String(50), ForeignKey("sellers.seller_id"), nullable=False, index=True)
    shipping_limit_date = Column(DateTime, nullable=True)
    price               = Column(Numeric(10, 2), nullable=True)
    freight_value       = Column(Numeric(10, 2), nullable=True)
    order   = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")
    seller  = relationship("Seller", back_populates="order_items")


class OrderPayment(Base):
    __tablename__ = "order_payments"
    order_id             = Column(String(50), ForeignKey("orders.order_id"), primary_key=True)
    payment_sequential   = Column(Integer, primary_key=True)
    payment_type         = Column(String(30), nullable=True)
    payment_installments = Column(Integer, nullable=True)
    payment_value        = Column(Numeric(10, 2), nullable=True)
    order = relationship("Order", back_populates="payments")


class OrderReview(Base):
    __tablename__ = "order_reviews"
    review_id               = Column(String(50), primary_key=True)
    order_id                = Column(String(50), ForeignKey("orders.order_id"), nullable=False, index=True)
    review_score            = Column(SmallInteger, nullable=True)
    review_comment_title    = Column(String(255), nullable=True)
    review_comment_message  = Column(Text, nullable=True)
    review_creation_date    = Column(DateTime, nullable=True)
    review_answer_timestamp = Column(DateTime, nullable=True)
    order = relationship("Order", back_populates="reviews")