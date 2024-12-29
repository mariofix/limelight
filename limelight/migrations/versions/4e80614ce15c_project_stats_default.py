"""Project Stats default

Revision ID: 4e80614ce15c
Revises: dbf7334c7184
Create Date: 2024-12-28 01:29:14.986889

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4e80614ce15c"
down_revision = "dbf7334c7184"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("limelight_project_stats", schema=None) as batch_op:
        batch_op.alter_column("issues_open", existing_type=sa.INTEGER(), nullable=True)
        batch_op.alter_column("issues_closed", existing_type=sa.INTEGER(), nullable=True)
        batch_op.alter_column("stars", existing_type=sa.INTEGER(), nullable=True)
        batch_op.alter_column("forks", existing_type=sa.INTEGER(), nullable=True)
        batch_op.alter_column("network", existing_type=sa.INTEGER(), nullable=True)
        batch_op.alter_column("watchers", existing_type=sa.INTEGER(), nullable=True)
        batch_op.alter_column("subscribers", existing_type=sa.INTEGER(), nullable=True)
        batch_op.alter_column("downloads_d", existing_type=sa.INTEGER(), nullable=True)
        batch_op.alter_column("downloads_w", existing_type=sa.INTEGER(), nullable=True)
        batch_op.alter_column("downloads_m", existing_type=sa.INTEGER(), nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("limelight_project_stats", schema=None) as batch_op:
        batch_op.alter_column("downloads_m", existing_type=sa.INTEGER(), nullable=False)
        batch_op.alter_column("downloads_w", existing_type=sa.INTEGER(), nullable=False)
        batch_op.alter_column("downloads_d", existing_type=sa.INTEGER(), nullable=False)
        batch_op.alter_column("subscribers", existing_type=sa.INTEGER(), nullable=False)
        batch_op.alter_column("watchers", existing_type=sa.INTEGER(), nullable=False)
        batch_op.alter_column("network", existing_type=sa.INTEGER(), nullable=False)
        batch_op.alter_column("forks", existing_type=sa.INTEGER(), nullable=False)
        batch_op.alter_column("stars", existing_type=sa.INTEGER(), nullable=False)
        batch_op.alter_column("issues_closed", existing_type=sa.INTEGER(), nullable=False)
        batch_op.alter_column("issues_open", existing_type=sa.INTEGER(), nullable=False)

    # ### end Alembic commands ###
