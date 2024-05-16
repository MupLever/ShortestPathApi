"""add role to user

Revision ID: 99b0fb384e31
Revises: ec448936565c
Create Date: 2024-05-14 20:28:34.624891

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "99b0fb384e31"
down_revision: Union[str, None] = "ec448936565c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, "executors", ["passport"])
    op.create_unique_constraint(None, "executors", ["phone_number"])
    op.create_unique_constraint(None, "orders", ["number"])
    op.create_unique_constraint(None, "orders", ["phone_number"])

    roles_type_enum = postgresql.ENUM(
        "admin", "dispatcher", name="role", create_type=False
    )
    roles_type_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "users",
        sa.Column("role", roles_type_enum, server_default="dispatcher", nullable=False),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "role")
    op.drop_constraint(None, "orders", type_="unique")
    op.drop_constraint(None, "orders", type_="unique")
    op.drop_constraint(None, "executors", type_="unique")
    op.drop_constraint(None, "executors", type_="unique")
    # ### end Alembic commands ###
