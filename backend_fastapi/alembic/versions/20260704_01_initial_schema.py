"""initial schema

Revision ID: 20260704_01
Revises: 
Create Date: 2026-07-04
"""

from alembic import op
import sqlalchemy as sa


revision = "20260704_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("role", sa.Enum("CUSTOMER", "STAFF", name="userrole"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "medicines",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("medicine_name", sa.String(length=255), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("manufacturer", sa.String(length=100), nullable=True),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("quantity >= 0", name="check_medicine_quantity_non_negative"),
        sa.CheckConstraint("price >= 0", name="check_medicine_price_non_negative"),
    )
    op.create_index("ix_medicines_medicine_name", "medicines", ["medicine_name"])
    op.create_index("ix_medicines_name_category", "medicines", ["medicine_name", "category"])

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("customer_name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("pincode", sa.String(length=10), nullable=False),
        sa.Column("status", sa.Enum("PENDING", "PROCESSING", "DELIVERED", "CANCELLED", name="orderstatus"), nullable=False),
        sa.Column("total_price", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("delivery_date", sa.Date(), nullable=True),
    )
    op.create_index("ix_orders_user_created", "orders", ["user_id", "created_at"])

    op.create_table(
        "cart_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("medicine_id", sa.Integer(), sa.ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("medicine_id", sa.Integer(), sa.ForeignKey("medicines.id"), nullable=False),
        sa.Column("medicine_name_snapshot", sa.String(length=255), nullable=False),
        sa.Column("unit_price", sa.Float(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("line_total", sa.Float(), nullable=False),
        sa.CheckConstraint("quantity > 0", name="check_order_item_quantity_positive"),
    )

    op.create_table(
        "order_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("method", sa.Enum("COD", "UPI", "CARD", name="paymentmethod"), nullable=False),
        sa.Column("status", sa.Enum("INITIATED", "PAID", "FAILED", "REFUNDED", name="paymentstatus"), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("gateway_reference", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "notification_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), nullable=True),
        sa.Column("channel", sa.String(length=50), nullable=False),
        sa.Column("recipient", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "assistant_threads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("staff_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("mode", sa.String(length=20), nullable=False),
        sa.Column("retention_days", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "assistant_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("thread_id", sa.Integer(), sa.ForeignKey("assistant_threads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("assistant_messages")
    op.drop_table("assistant_threads")
    op.drop_table("notification_logs")
    op.drop_table("payments")
    op.drop_table("order_events")
    op.drop_table("order_items")
    op.drop_table("cart_items")
    op.drop_index("ix_orders_user_created", table_name="orders")
    op.drop_table("orders")
    op.drop_index("ix_medicines_name_category", table_name="medicines")
    op.drop_index("ix_medicines_medicine_name", table_name="medicines")
    op.drop_table("medicines")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
