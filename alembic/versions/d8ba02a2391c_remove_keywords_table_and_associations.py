"""Remove keywords table and associations

Revision ID: d8ba02a2391c
Revises: 94d19a4d6895
Create Date: 2025-04-09 23:38:38.919942

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8ba02a2391c'
down_revision: Union[str, None] = '94d19a4d6895'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Удаляем индекс для таблицы keywords
    op.drop_index('ix_keywords_id', table_name='keywords')
    
    # Удаляем внешние ключи в таблице film_keyword, которые ссылаются на keywords
    op.drop_constraint('film_keyword_keyword_id_fkey', 'film_keyword', type_='foreignkey')
    
    # Удаляем таблицу film_keyword
    op.drop_table('film_keyword')
    
    # Удаляем таблицу keywords
    op.drop_table('keywords')

def downgrade() -> None:
    """Downgrade schema."""
    # Восстанавливаем таблицу film_keyword
    op.create_table('film_keyword',
        sa.Column('film_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('keyword_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['film_id'], ['films.id'], name='film_keyword_film_id_fkey'),
        sa.ForeignKeyConstraint(['keyword_id'], ['keywords.id'], name='film_keyword_keyword_id_fkey'),
        sa.PrimaryKeyConstraint('film_id', 'keyword_id', name='film_keyword_pkey')
    )
    
    # Восстанавливаем таблицу keywords
    op.create_table('keywords',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint('id', name='keywords_pkey'),
        sa.UniqueConstraint('name', name='keywords_name_key')
    )
    
    # Восстанавливаем индекс для таблицы keywords
    op.create_index('ix_keywords_id', 'keywords', ['id'], unique=False)
