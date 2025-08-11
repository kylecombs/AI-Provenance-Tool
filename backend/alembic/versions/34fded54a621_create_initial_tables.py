"""Create initial tables

Revision ID: 34fded54a621
Revises: 
Create Date: 2025-08-11 13:36:28.757421

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '34fded54a621'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create artworks table
    op.create_table('artworks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('format_type', sa.String(), nullable=True),
        sa.Column('dimensions', sa.String(), nullable=True),
        sa.Column('image_url', sa.Text(), nullable=True),
        sa.Column('vector_embedding', sa.ARRAY(sa.Float()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_artworks_id'), 'artworks', ['id'], unique=False)
    op.create_index(op.f('ix_artworks_title'), 'artworks', ['title'], unique=False)
    
    # Create exhibitions table
    op.create_table('exhibitions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('venue', sa.String(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_exhibitions_id'), 'exhibitions', ['id'], unique=False)
    op.create_index(op.f('ix_exhibitions_name'), 'exhibitions', ['name'], unique=False)
    
    # Create installation_photos table
    op.create_table('installation_photos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('exhibition_id', sa.Integer(), nullable=False),
        sa.Column('photo_url', sa.String(), nullable=False),
        sa.Column('processed_status', sa.Enum('pending', 'processing', 'completed', 'failed', name='processedstatus'), nullable=True),
        sa.ForeignKeyConstraint(['exhibition_id'], ['exhibitions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_installation_photos_exhibition_id'), 'installation_photos', ['exhibition_id'], unique=False)
    op.create_index(op.f('ix_installation_photos_id'), 'installation_photos', ['id'], unique=False)
    op.create_index(op.f('ix_installation_photos_processed_status'), 'installation_photos', ['processed_status'], unique=False)
    
    # Create detections table
    op.create_table('detections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('installation_photo_id', sa.Integer(), nullable=False),
        sa.Column('artwork_id', sa.Integer(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('bounding_box', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['artwork_id'], ['artworks.id'], ),
        sa.ForeignKeyConstraint(['installation_photo_id'], ['installation_photos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_detections_artwork_id'), 'detections', ['artwork_id'], unique=False)
    op.create_index(op.f('ix_detections_confidence_score'), 'detections', ['confidence_score'], unique=False)
    op.create_index(op.f('ix_detections_id'), 'detections', ['id'], unique=False)
    op.create_index(op.f('ix_detections_installation_photo_id'), 'detections', ['installation_photo_id'], unique=False)
    
    # Create provenance_records table
    op.create_table('provenance_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('artwork_id', sa.Integer(), nullable=False),
        sa.Column('exhibition_id', sa.Integer(), nullable=False),
        sa.Column('detection_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['artwork_id'], ['artworks.id'], ),
        sa.ForeignKeyConstraint(['detection_id'], ['detections.id'], ),
        sa.ForeignKeyConstraint(['exhibition_id'], ['exhibitions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_provenance_records_artwork_id'), 'provenance_records', ['artwork_id'], unique=False)
    op.create_index(op.f('ix_provenance_records_created_at'), 'provenance_records', ['created_at'], unique=False)
    op.create_index(op.f('ix_provenance_records_detection_id'), 'provenance_records', ['detection_id'], unique=False)
    op.create_index(op.f('ix_provenance_records_exhibition_id'), 'provenance_records', ['exhibition_id'], unique=False)
    op.create_index(op.f('ix_provenance_records_id'), 'provenance_records', ['id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order due to foreign key constraints
    op.drop_index(op.f('ix_provenance_records_id'), table_name='provenance_records')
    op.drop_index(op.f('ix_provenance_records_exhibition_id'), table_name='provenance_records')
    op.drop_index(op.f('ix_provenance_records_detection_id'), table_name='provenance_records')
    op.drop_index(op.f('ix_provenance_records_created_at'), table_name='provenance_records')
    op.drop_index(op.f('ix_provenance_records_artwork_id'), table_name='provenance_records')
    op.drop_table('provenance_records')
    
    op.drop_index(op.f('ix_detections_installation_photo_id'), table_name='detections')
    op.drop_index(op.f('ix_detections_id'), table_name='detections')
    op.drop_index(op.f('ix_detections_confidence_score'), table_name='detections')
    op.drop_index(op.f('ix_detections_artwork_id'), table_name='detections')
    op.drop_table('detections')
    
    op.drop_index(op.f('ix_installation_photos_processed_status'), table_name='installation_photos')
    op.drop_index(op.f('ix_installation_photos_id'), table_name='installation_photos')
    op.drop_index(op.f('ix_installation_photos_exhibition_id'), table_name='installation_photos')
    op.drop_table('installation_photos')
    
    op.drop_index(op.f('ix_exhibitions_name'), table_name='exhibitions')
    op.drop_index(op.f('ix_exhibitions_id'), table_name='exhibitions')
    op.drop_table('exhibitions')
    
    op.drop_index(op.f('ix_artworks_title'), table_name='artworks')
    op.drop_index(op.f('ix_artworks_id'), table_name='artworks')
    op.drop_table('artworks')
