#!/usr/bin/env python3
"""
Migration script to add topic-agnostic support to the research assistant.

This script:
1. Backs up the existing database
2. Adds the research_domains table
3. Creates default AI/ML domain
4. Links existing topics to the AI/ML domain
"""

import os
import sys
import shutil
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.memory.database import Database
from src.memory.models import ResearchDomain, ResearchTopic, Base
from config import config
from sqlalchemy import text


def backup_database(db_path: str) -> str:
    """
    Create a backup of the database file.

    Args:
        db_path: Path to the database file

    Returns:
        Path to the backup file
    """
    if not os.path.exists(db_path):
        print("⚠️  No existing database found - creating fresh database")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_{timestamp}"

    shutil.copy2(db_path, backup_path)
    print(f"✓ Database backed up to: {backup_path}")

    return backup_path


def migrate_database():
    """Run the migration to add topic-agnostic support"""

    print("\n" + "="*60)
    print("Research Assistant - Topic System Migration")
    print("="*60 + "\n")

    # Extract database path from DATABASE_URL
    db_url = config.DATABASE_URL
    if db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
    else:
        print("⚠️  This migration only supports SQLite databases")
        return False

    # Backup existing database
    backup_path = backup_database(db_path)

    # Initialize database
    print("\n1. Initializing database...")
    db = Database()

    # Check if column already exists
    with db.session_scope() as session:
        try:
            # Try to query the column - if it fails, we need to add it
            session.execute(text("SELECT research_domain_id FROM research_topics LIMIT 1"))
            print("⚠️  Migration already completed - research_domain_id column exists")
            return True
        except Exception:
            # Column doesn't exist, continue with migration
            pass

    # Add research_domain_id column to existing table
    print("\n2. Adding research_domain_id column to research_topics...")
    with db.session_scope() as session:
        try:
            session.execute(text("ALTER TABLE research_topics ADD COLUMN research_domain_id INTEGER"))
            print("✓ Added research_domain_id column")
        except Exception as e:
            print(f"Note: {e}")

    # Create research_domains table if it doesn't exist
    print("\n3. Creating research_domains table...")
    Base.metadata.create_all(bind=db.engine, tables=[ResearchDomain.__table__])
    print("✓ Created research_domains table")

    with db.session_scope() as session:
        # Check if migration already done
        existing_domains = session.query(ResearchDomain).count()

        if existing_domains > 0:
            print("⚠️  Default domains already exist")
        else:
            # Create default AI/ML domain
            print("\n4. Creating default AI/ML research domain...")
            ai_ml_domain = ResearchDomain(
                name="AI/ML",
                description="Artificial Intelligence and Machine Learning development",
                keywords=[
                    "AI libraries",
                    "ML frameworks",
                    "LLM models",
                    "vector databases",
                    "transformers",
                    "neural networks",
                    "deep learning"
                ]
            )
            session.add(ai_ml_domain)
            session.flush()  # Get the ID

            print(f"✓ Created domain: {ai_ml_domain.name} (ID: {ai_ml_domain.id})")

            # Link existing topics to AI/ML domain
            print("\n5. Linking existing topics to AI/ML domain...")
            existing_topics = session.query(ResearchTopic).filter(
                ResearchTopic.research_domain_id == None
            ).all()

            if existing_topics:
                for topic in existing_topics:
                    topic.research_domain_id = ai_ml_domain.id

                print(f"✓ Linked {len(existing_topics)} existing topics to AI/ML domain")
            else:
                print("✓ No existing topics found - starting fresh")

            # Create additional default domains
            print("\n6. Creating additional preset domains...")

            preset_domains = [
                {
                    "name": "cryptocurrency",
                    "description": "Cryptocurrency and blockchain technology",
                    "keywords": [
                        "blockchain",
                        "DeFi",
                        "smart contracts",
                        "crypto protocols",
                        "NFTs",
                        "DAOs",
                        "Web3"
                    ]
                },
                {
                    "name": "web3",
                    "description": "Web3 and decentralized technologies",
                    "keywords": [
                        "decentralized apps",
                        "IPFS",
                        "decentralized storage",
                        "Web3 infrastructure",
                        "dApps"
                    ]
                },
                {
                    "name": "quantum-computing",
                    "description": "Quantum computing and quantum algorithms",
                    "keywords": [
                        "quantum",
                        "qubits",
                        "quantum algorithms",
                        "quantum hardware",
                        "quantum supremacy"
                    ]
                }
            ]

            for domain_data in preset_domains:
                domain = ResearchDomain(**domain_data)
                session.add(domain)
                print(f"✓ Created domain: {domain.name}")

    print("\n" + "="*60)
    print("✓ Migration completed successfully!")
    print("="*60)

    if backup_path:
        print(f"\nBackup saved at: {backup_path}")

    print("\nYou can now use the research assistant with any topic domain.")
    print("Set RESEARCH_TOPIC in your .env file or choose at startup.\n")

    return True


if __name__ == "__main__":
    try:
        success = migrate_database()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
