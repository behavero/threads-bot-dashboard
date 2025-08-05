"""
Database connection and configuration for Supabase PostgreSQL
"""

import os
import asyncio
import logging
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
import asyncpg
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = "postgresql://postgres:jZGhekR4AO!0IJQsMYAG@db.perwbmtwutwzsvlirwik.supabase.co:5432/postgres"
ASYNC_DATABASE_URL = "postgresql+asyncpg://postgres:jZGhekR4AO!0IJQsMYAG@db.perwbmtwutwzsvlirwik.supabase.co:5432/postgres"

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self):
        self.engine = None
        self.async_engine = None
        self.session_factory = None
        self._connection_pool = None
        
    async def initialize(self):
        """Initialize database connections"""
        try:
            # Create async engine
            self.async_engine = create_async_engine(
                ASYNC_DATABASE_URL,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=300,
                pool_size=10,
                max_overflow=20
            )
            
            # Create sync engine for Flask
            self.engine = create_engine(
                DATABASE_URL,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=300,
                pool_size=10,
                max_overflow=20
            )
            
            # Create session factory
            self.session_factory = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False
            )
            
            # Test connection
            await self.test_connection()
            logger.info("✅ Database connection established successfully")
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    async def test_connection(self):
        """Test database connection"""
        try:
            async with self.async_engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection test successful")
        except Exception as e:
            logger.error(f"❌ Database connection test failed: {e}")
            raise
    
    async def create_tables(self):
        """Create database tables if they don't exist"""
        try:
            async with self.async_engine.begin() as conn:
                # Create captions table
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS captions (
                        id SERIAL PRIMARY KEY,
                        text TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                """))
                
                # Create images table
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS images (
                        id SERIAL PRIMARY KEY,
                        filename VARCHAR(255) NOT NULL,
                        file_path TEXT NOT NULL,
                        file_size BIGINT,
                        mime_type VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_used TIMESTAMP,
                        use_count INTEGER DEFAULT 0,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                """))
                
                # Create accounts table
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS accounts (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(255) UNIQUE NOT NULL,
                        email VARCHAR(255) NOT NULL,
                        password TEXT NOT NULL,
                        enabled BOOLEAN DEFAULT TRUE,
                        description TEXT,
                        posting_schedule JSONB,
                        posting_config JSONB,
                        fingerprint_config JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Create posting_history table
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS posting_history (
                        id SERIAL PRIMARY KEY,
                        account_id INTEGER REFERENCES accounts(id),
                        caption_id INTEGER REFERENCES captions(id),
                        image_id INTEGER REFERENCES images(id),
                        posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        success BOOLEAN DEFAULT TRUE,
                        error_message TEXT,
                        user_agent TEXT
                    )
                """))
                
            logger.info("✅ Database tables created successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to create tables: {e}")
            raise
    
    @asynccontextmanager
    async def get_async_connection(self):
        """Get async database connection"""
        if not self.async_engine:
            raise RuntimeError("Database not initialized")
        
        async with self.async_engine.begin() as conn:
            yield conn
    
    def get_sync_session(self):
        """Get sync database session for Flask"""
        if not self.session_factory:
            raise RuntimeError("Database not initialized")
        
        return self.session_factory()
    
    async def close(self):
        """Close database connections"""
        if self.async_engine:
            await self.async_engine.dispose()
        if self.engine:
            self.engine.dispose()
        logger.info("✅ Database connections closed")

# Global database manager instance
db_manager = DatabaseManager()

async def init_database():
    """Initialize database connection and tables"""
    await db_manager.initialize()
    await db_manager.create_tables()

def get_sync_session():
    """Get sync session for Flask"""
    return db_manager.get_sync_session()

async def get_async_connection():
    """Get async connection context manager"""
    return db_manager.get_async_connection()

async def close_database():
    """Close database connections"""
    await db_manager.close() 