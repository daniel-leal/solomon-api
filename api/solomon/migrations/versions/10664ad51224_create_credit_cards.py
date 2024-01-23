"""create_credit_cards

Revision ID: 10664ad51224
Revises: c0da4441dcd7
Create Date: 2024-01-21 15:26:08.596915

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "10664ad51224"
down_revision: Union[str, None] = "c0da4441dcd7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "credit_cards",
        sa.Column("user_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("limit", sa.Float(), nullable=False),
        sa.Column("invoice_start_day", sa.Integer(), nullable=False),
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("credit_cards")
    # ### end Alembic commands ###
