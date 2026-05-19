"""create abastecimentos table

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "abastecimentos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_posto", sa.Integer(), nullable=False),
        sa.Column("data_hora", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "tipo_combustivel",
            sa.Enum("GASOLINA", "ETANOL", "DIESEL", name="tipocombustivel"),
            nullable=False,
        ),
        sa.Column("preco_por_litro", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("volume_abastecido", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("cpf_motorista", sa.String(length=11), nullable=False),
        sa.Column("improper_data", sa.Boolean(), nullable=False, server_default="false"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_abastecimentos_cpf_motorista"), "abastecimentos", ["cpf_motorista"])


def downgrade() -> None:
    op.drop_index(op.f("ix_abastecimentos_cpf_motorista"), table_name="abastecimentos")
    op.drop_table("abastecimentos")
    op.execute("DROP TYPE IF EXISTS tipocombustivel")
