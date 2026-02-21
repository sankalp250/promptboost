"""Add prompt_history table and project_id to prompt_cache

Revision ID: b1c2d3e4f5a6
Revises: 9aaa849bc8ca
Create Date: 2025-02-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "b1c2d3e4f5a6"
down_revision: Union[str, None] = "9aaa849bc8ca"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add project_id to prompt_cache (nullable for backward compatibility)
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE prompt_cache ADD COLUMN project_id VARCHAR(64);
        EXCEPTION
            WHEN duplicate_column THEN null;
        END $$;
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_prompt_cache_project_id ON prompt_cache(project_id)
    """)
    # Drop old unique constraint on original_prompt if it exists (Postgres)
    op.execute("""
        ALTER TABLE prompt_cache DROP CONSTRAINT IF EXISTS prompt_cache_original_prompt_key
    """)
    # Partial unique: one row per original_prompt when project_id IS NULL
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS ix_prompt_cache_global_original
        ON prompt_cache(original_prompt) WHERE project_id IS NULL
    """)
    # Partial unique: one row per (project_id, original_prompt) when project_id IS NOT NULL
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS ix_prompt_cache_project_original
        ON prompt_cache(project_id, original_prompt) WHERE project_id IS NOT NULL
    """)

    # Create prompt_history table
    op.execute("""
        CREATE TABLE IF NOT EXISTS prompt_history (
            id SERIAL PRIMARY KEY,
            project_id VARCHAR(64) NOT NULL,
            user_id UUID NOT NULL,
            session_id UUID,
            original_prompt TEXT NOT NULL,
            enhanced_prompt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_prompt_history_project_id ON prompt_history(project_id)
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_prompt_history_user_id ON prompt_history(user_id)
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_prompt_history_created_at ON prompt_history(created_at DESC)
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS prompt_history")
    op.execute("DROP INDEX IF EXISTS ix_prompt_cache_project_original")
    op.execute("DROP INDEX IF EXISTS ix_prompt_cache_global_original")
    op.execute("""
        ALTER TABLE prompt_cache ADD CONSTRAINT prompt_cache_original_prompt_key UNIQUE (original_prompt)
    """)
    op.execute("DROP INDEX IF EXISTS ix_prompt_cache_project_id")
    op.execute("ALTER TABLE prompt_cache DROP COLUMN project_id")
