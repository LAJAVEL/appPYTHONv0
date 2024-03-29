"""Ajout is_deleted et deleted_content_preview à Post

Revision ID: 453d598d7549
Revises: 
Create Date: 2024-03-14 11:49:17.465286

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '453d598d7549'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_deleted', sa.Boolean(), nullable=False))
        batch_op.add_column(sa.Column('deleted_content_preview', sa.String(length=255), nullable=False))

        op.add_column('post', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.false()))
        op.add_column('post', sa.Column('deleted_content_preview', sa.String(length=255), nullable=False, server_default=''))


    # ### end Alembic commands ###
        



def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_column('deleted_content_preview')
        batch_op.drop_column('is_deleted')

    # ### end Alembic commands ###
