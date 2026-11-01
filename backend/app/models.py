from datetime import datetime, timezone

from sqlalchemy import (JSON, BigInteger, Boolean, DateTime, Float, ForeignKey, Integer,
                        String, Text, UniqueConstraint)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)  # naive UTC everywhere


PERMISSIONS = ["products", "orders", "customers", "promotions", "settings", "statistics"]

STATUSES = ["new", "awaiting_payment", "paid", "ordered_china", "china_warehouse",
            "in_transit", "in_uz", "delivered", "cancelled"]
STATUS_UZ = {
    "new": "Yangi", "awaiting_payment": "To'lov kutilmoqda", "paid": "To'langan",
    "ordered_china": "Xitoyda buyurtma berildi", "china_warehouse": "Xitoy omborida",
    "in_transit": "Yo'lda", "in_uz": "O'zbekistonda", "delivered": "Yetkazildi",
    "cancelled": "Bekor qilindi",
}
STATUS_RU = {
    "new": "Новый", "awaiting_payment": "Ожидает оплаты", "paid": "Оплачен",
    "ordered_china": "Заказан в Китае", "china_warehouse": "На складе в Китае",
    "in_transit": "В пути", "in_uz": "В Узбекистане", "delivered": "Доставлен",
    "cancelled": "Отменён",
}


class Setting(Base):
    __tablename__ = "settings"
    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(Text, default="")


class AdminAccount(Base):
    __tablename__ = "admin_accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120))
    tg_username: Mapped[str] = mapped_column(String(64), default="")
    login: Mapped[str] = mapped_column(String(64), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(16), default="admin")  # owner | admin
    permissions: Mapped[list] = mapped_column(JSON, default=list)
    avatar: Mapped[str] = mapped_column(String(255), default="")
    accepts_orders: Mapped[bool] = mapped_column(Boolean, default=False)
    blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    session_version: Mapped[int] = mapped_column(Integer, default=1)
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    tg_chat_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    link_token: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    link_token_expires: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class AdminAudit(Base):
    __tablename__ = "admin_audit"
    id: Mapped[int] = mapped_column(primary_key=True)
    admin_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    admin_name: Mapped[str] = mapped_column(String(120), default="")
    action: Mapped[str] = mapped_column(String(64))
    entity: Mapped[str] = mapped_column(String(64), default="")
    entity_id: Mapped[str] = mapped_column(String(64), default="")
    detail: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now, index=True)


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int | None] = mapped_column(BigInteger, unique=True, nullable=True)
    first_name: Mapped[str] = mapped_column(String(120), default="")
    last_name: Mapped[str] = mapped_column(String(120), default="")
    username: Mapped[str] = mapped_column(String(64), default="")
    phone: Mapped[str] = mapped_column(String(32), default="", index=True)
    language: Mapped[str] = mapped_column(String(2), default="uz")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=now)

    @property
    def display_name(self) -> str:
        return (f"{self.first_name} {self.last_name}").strip() or self.username or f"#{self.id}"


class ShopSession(Base):
    __tablename__ = "shop_sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    cart: Mapped[list] = mapped_column(JSON, default=list)
    utm_source: Mapped[str] = mapped_column(String(64), default="")
    utm_medium: Mapped[str] = mapped_column(String(64), default="")
    utm_campaign: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=now)


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name_uz: Mapped[str] = mapped_column(String(120))
    name_ru: Mapped[str] = mapped_column(String(120), default="")
    sort: Mapped[int] = mapped_column(Integer, default=0)


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    name_uz: Mapped[str] = mapped_column(String(200), default="")
    name_ru: Mapped[str] = mapped_column(String(200), default="")
    desc_uz: Mapped[str] = mapped_column(Text, default="")
    desc_ru: Mapped[str] = mapped_column(Text, default="")
    material: Mapped[str] = mapped_column(String(200), default="")
    size_chart: Mapped[list] = mapped_column(JSON, default=list)  # [{size, chest, waist, length, shoulder}]
    price_yuan: Mapped[float] = mapped_column(Float, default=0)
    weight_kg: Mapped[float] = mapped_column(Float, default=1.0)
    manual_price: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_uzs: Mapped[int] = mapped_column(Integer, default=0)  # cached selling price
    sale_type: Mapped[str] = mapped_column(String(12), default="preorder")  # preorder | stock
    featured: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    draft: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)

    variants: Mapped[list["ProductVariant"]] = relationship(
        back_populates="product", cascade="all, delete-orphan", order_by="ProductVariant.id")
    images: Mapped[list["ProductImage"]] = relationship(
        back_populates="product", cascade="all, delete-orphan", order_by="ProductImage.sort")
    category: Mapped["Category | None"] = relationship()


class ProductVariant(Base):
    __tablename__ = "product_variants"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    size: Mapped[str] = mapped_column(String(32), default="")
    color: Mapped[str] = mapped_column(String(64), default="")
    stock: Mapped[int] = mapped_column(Integer, default=0)
    product: Mapped[Product] = relationship(back_populates="variants")


class ProductImage(Base):
    __tablename__ = "product_images"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    path: Mapped[str] = mapped_column(String(255))  # relative to UPLOAD_DIR
    sort: Mapped[int] = mapped_column(Integer, default=0)
    product: Mapped[Product] = relationship(back_populates="images")


class ImageUpload(Base):
    __tablename__ = "image_uploads"
    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(String(255), unique=True)
    thumb: Mapped[str] = mapped_column(String(255), default="")
    original_name: Mapped[str] = mapped_column(String(255), default="")
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    width: Mapped[int] = mapped_column(Integer, default=0)
    height: Mapped[int] = mapped_column(Integer, default=0)
    admin_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class Promocode(Base):
    __tablename__ = "promocodes"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    percent: Mapped[int] = mapped_column(Integer, default=10)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    usage_limit: Mapped[int] = mapped_column(Integer, default=0)  # 0 = unlimited
    used_count: Mapped[int] = mapped_column(Integer, default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(16), unique=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    status: Mapped[str] = mapped_column(String(24), default="new", index=True)
    name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(String(32), default="")
    tg_username: Mapped[str] = mapped_column(String(64), default="")
    city: Mapped[str] = mapped_column(String(120), default="")
    address: Mapped[str] = mapped_column(Text, default="")
    comment: Mapped[str] = mapped_column(Text, default="")
    delivery: Mapped[str] = mapped_column(String(16), default="courier")  # courier | pickup
    subtotal: Mapped[int] = mapped_column(Integer, default=0)
    discount: Mapped[int] = mapped_column(Integer, default=0)
    total: Mapped[int] = mapped_column(Integer, default=0)
    promo_code: Mapped[str] = mapped_column(String(32), default="")
    paid_amount: Mapped[int] = mapped_column(Integer, default=0)
    tracking: Mapped[str] = mapped_column(String(120), default="")
    internal_note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now, index=True)

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan", order_by="OrderItem.id")
    meta: Mapped["OrderMeta"] = relationship(back_populates="order", uselist=False,
                                             cascade="all, delete-orphan")
    history: Mapped[list["OrderStatusHistory"]] = relationship(
        cascade="all, delete-orphan", order_by="OrderStatusHistory.id")
    customer: Mapped[Customer] = relationship()


class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    product_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    variant_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    name: Mapped[str] = mapped_column(String(200))  # snapshot
    size: Mapped[str] = mapped_column(String(32), default="")
    color: Mapped[str] = mapped_column(String(64), default="")
    price: Mapped[int] = mapped_column(Integer)  # snapshot
    qty: Mapped[int] = mapped_column(Integer, default=1)
    sale_type: Mapped[str] = mapped_column(String(12), default="preorder")
    reserved: Mapped[bool] = mapped_column(Boolean, default=False)
    order: Mapped[Order] = relationship(back_populates="items")


class OrderMeta(Base):
    __tablename__ = "order_meta"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), unique=True)
    assigned_admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("admin_accounts.id"), nullable=True, index=True)
    source: Mapped[str] = mapped_column(String(64), default="")
    medium: Mapped[str] = mapped_column(String(64), default="")
    campaign: Mapped[str] = mapped_column(String(64), default="")
    notification_status: Mapped[str] = mapped_column(String(16), default="pending")
    stock_reserved: Mapped[bool] = mapped_column(Boolean, default=False)
    idempotency_key: Mapped[str] = mapped_column(String(80), unique=True)
    order: Mapped[Order] = relationship(back_populates="meta")
    assigned_admin: Mapped["AdminAccount | None"] = relationship()


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    status: Mapped[str] = mapped_column(String(24))
    by: Mapped[str] = mapped_column(String(120), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class StoreEvent(Base):
    __tablename__ = "store_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(24), index=True)
    customer_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    product_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now, index=True)


class MarketingVisit(Base):
    __tablename__ = "marketing_visits"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source: Mapped[str] = mapped_column(String(64), default="")
    medium: Mapped[str] = mapped_column(String(64), default="")
    campaign: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now, index=True)


class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("customer_id", "product_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))


class RestockSubscription(Base):
    __tablename__ = "restock_subscriptions"
    __table_args__ = (UniqueConstraint("customer_id", "variant_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    variant_id: Mapped[int] = mapped_column(ForeignKey("product_variants.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class Outbox(Base):
    __tablename__ = "outbox"
    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(24), index=True)  # admin_order|low_stock|status|restock|broadcast|direct
    chat_id: Mapped[int] = mapped_column(BigInteger)
    text: Mapped[str] = mapped_column(Text)
    photo: Mapped[str] = mapped_column(String(255), default="")  # path relative to UPLOAD_DIR
    button_text: Mapped[str] = mapped_column(String(64), default="")
    button_url: Mapped[str] = mapped_column(String(500), default="")
    order_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(12), default="pending", index=True)  # pending|sent|failed
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    next_attempt_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    last_error: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
