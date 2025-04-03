"""update voice_logs schema

Revision ID: update_voice_logs
Revises: 
Create Date: 2025-04-03 11:47:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'update_voice_logs'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Rename the old table to a backup
    op.rename_table('voice_logs', 'voice_logs_old')
    
    # Create new table with updated schema
    op.create_table('voice_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('timestamp', sa.String(), nullable=True),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('language', sa.String(), nullable=True),
        sa.Column('error_type', sa.String(), nullable=True),
        sa.Column('raw_input', sa.Text(), nullable=True),
        sa.Column('recognized_text', sa.Text(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=True),
        sa.Column('device_info', sa.Text(), nullable=True),
        sa.Column('context', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Migrate data that matches between the tables
    op.execute('''
    INSERT INTO voice_logs (id, timestamp, session_id, language, recognized_text)
    SELECT id, timestamp, session_id, language, text
    FROM voice_logs_old
    ''')
    
    # Set success flag appropriately
    op.execute('''
    UPDATE voice_logs SET success = true
    WHERE recognized_text IS NOT NULL
    ''')
    
    # Don't drop the old table yet in case we need to recover data


def downgrade():
    # Drop the new table
    op.drop_table('voice_logs')
    
    # Rename the backup table back to the original name
    op.rename_table('voice_logs_old', 'voice_logs')