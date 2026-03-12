"""initial schema

Revision ID: 1a1ac490ea2c
Revises:
Create Date: 2026-03-11 19:13:28.072361

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '1a1ac490ea2c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('company', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('verification_token', sa.String(length=255), nullable=True),
        sa.Column('verification_token_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    op.create_table(
        'oauth_applications',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('client_id', sa.String(length=64), nullable=False),
        sa.Column('client_secret_hash', sa.String(length=255), nullable=False),
        sa.Column('application_type', sa.Enum('web', 'spa', 'native', 'machine_to_machine', name='applicationtype'), nullable=False),
        sa.Column('redirect_uris', sa.JSON(), nullable=True),
        sa.Column('post_logout_redirect_uris', sa.JSON(), nullable=True),
        sa.Column('allowed_scopes', sa.JSON(), nullable=True),
        sa.Column('grant_types', sa.JSON(), nullable=True),
        sa.Column('token_endpoint_auth_method', sa.String(length=64), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_oauth_applications_client_id'), 'oauth_applications', ['client_id'], unique=True)
    op.create_index(op.f('ix_oauth_applications_user_id'), 'oauth_applications', ['user_id'], unique=False)

    op.create_table(
        'authorization_codes',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('code', sa.String(length=128), nullable=False),
        sa.Column('client_id', sa.String(length=64), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('redirect_uri', sa.String(length=2048), nullable=False),
        sa.Column('scope', sa.String(length=512), nullable=False),
        sa.Column('nonce', sa.String(length=512), nullable=True),
        sa.Column('code_challenge', sa.String(length=512), nullable=True),
        sa.Column('code_challenge_method', sa.String(length=16), nullable=True),
        sa.Column('state', sa.String(length=512), nullable=True),
        sa.Column('is_used', sa.Boolean(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_authorization_codes_code'), 'authorization_codes', ['code'], unique=True)
    op.create_index(op.f('ix_authorization_codes_client_id'), 'authorization_codes', ['client_id'], unique=False)

    op.create_table(
        'oidc_refresh_tokens',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('token_hash', sa.String(length=255), nullable=False),
        sa.Column('client_id', sa.String(length=64), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('scope', sa.String(length=512), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_oidc_refresh_tokens_token_hash'), 'oidc_refresh_tokens', ['token_hash'], unique=True)
    op.create_index(op.f('ix_oidc_refresh_tokens_client_id'), 'oidc_refresh_tokens', ['client_id'], unique=False)

    op.create_table(
        'auth_challenges',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('challenge_nonce', sa.String(length=128), nullable=False),
        sa.Column('purpose_id', sa.String(length=64), nullable=False),
        sa.Column('client_id', sa.String(length=64), nullable=False),
        sa.Column('redirect_uri', sa.String(length=2048), nullable=False),
        sa.Column('scope', sa.String(length=512), nullable=False),
        sa.Column('state', sa.String(length=512), nullable=True),
        sa.Column('nonce', sa.String(length=512), nullable=True),
        sa.Column('code_challenge', sa.String(length=512), nullable=True),
        sa.Column('code_challenge_method', sa.String(length=16), nullable=True),
        sa.Column('response_type', sa.String(length=16), nullable=False),
        sa.Column('login_hint', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=16), nullable=False),
        sa.Column('redirect_url', sa.String(length=4096), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_auth_challenges_challenge_nonce'), 'auth_challenges', ['challenge_nonce'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_auth_challenges_challenge_nonce'), table_name='auth_challenges')
    op.drop_table('auth_challenges')
    op.drop_index(op.f('ix_oidc_refresh_tokens_client_id'), table_name='oidc_refresh_tokens')
    op.drop_index(op.f('ix_oidc_refresh_tokens_token_hash'), table_name='oidc_refresh_tokens')
    op.drop_table('oidc_refresh_tokens')
    op.drop_index(op.f('ix_authorization_codes_client_id'), table_name='authorization_codes')
    op.drop_index(op.f('ix_authorization_codes_code'), table_name='authorization_codes')
    op.drop_table('authorization_codes')
    op.drop_index(op.f('ix_oauth_applications_user_id'), table_name='oauth_applications')
    op.drop_index(op.f('ix_oauth_applications_client_id'), table_name='oauth_applications')
    op.drop_table('oauth_applications')
    sa.Enum('web', 'spa', 'native', 'machine_to_machine', name='applicationtype').drop(op.get_bind())
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
