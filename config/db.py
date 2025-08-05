"""
Database connection and configuration for Supabase
"""

import os
import asyncio
import logging
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from supabase import create_client, Client
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = "https://perwbmtwutwzsvlirwik.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBlcndibXR3dXR3enN2bGlyd2lrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0MDU1ODIsImV4cCI6MjA2OTk4MTU4Mn0.ACJ6v7w4brocGyhC3hlsWI_huE3-3kSdQjLSCijw56o"

# Direct PostgreSQL connection (fallback)
DATABASE_URL = "postgresql://postgres:jZGhekR4AO!0IJQsMYAG@db.perwbmtwutwzsvlirwik.supabase.co:5432/postgres"
ASYNC_DATABASE_URL = "postgresql+asyncpg://postgres:jZGhekR4AO!0IJQsMYAG@db.perwbmtwutwzsvlirwik.supabase.co:5432/postgres"

class SupabaseManager:
    """Manages Supabase client and operations"""
    
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.engine = None
        self.async_engine = None
        self.session_factory = None
        
    async def initialize(self):
        """Initialize Supabase client and database connections"""
        try:
            # Initialize Supabase client
            self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            logger.info("✅ Supabase client initialized successfully")
            
            # Test Supabase connection
            await self.test_supabase_connection()
            
            # Initialize direct PostgreSQL connections as fallback
            await self._initialize_postgres_connections()
            
            # Create tables if they don't exist
            await self.create_tables()
            
        except Exception as e:
            logger.error(f"❌ Supabase initialization failed: {e}")
            # Fallback to direct PostgreSQL
            await self._initialize_postgres_connections()
            await self.create_tables()
    
    async def test_supabase_connection(self):
        """Test Supabase connection"""
        try:
            # Test with a simple query
            response = self.supabase.table('captions').select('id').limit(1).execute()
            logger.info("✅ Supabase connection test successful")
        except Exception as e:
            logger.error(f"❌ Supabase connection test failed: {e}")
            raise
    
    async def _initialize_postgres_connections(self):
        """Initialize direct PostgreSQL connections as fallback"""
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
            
            logger.info("✅ PostgreSQL fallback connections initialized")
            
        except Exception as e:
            logger.error(f"❌ PostgreSQL fallback initialization failed: {e}")
            raise
    
    async def create_tables(self):
        """Create database tables if they don't exist"""
        try:
            # Try to create tables using direct PostgreSQL connection
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
    
    def get_supabase_client(self) -> Client:
        """Get Supabase client"""
        if not self.supabase:
            raise RuntimeError("Supabase not initialized")
        
        return self.supabase
    
    async def close(self):
        """Close database connections"""
        if self.async_engine:
            await self.async_engine.dispose()
        if self.engine:
            self.engine.dispose()
        logger.info("✅ Database connections closed")

# Global database manager instance
db_manager = SupabaseManager()

async def init_database():
    """Initialize database connection and tables"""
    await db_manager.initialize()

def get_sync_session():
    """Get sync session for Flask"""
    return db_manager.get_sync_session()

async def get_async_connection():
    """Get async connection context manager"""
    return db_manager.get_async_connection()

def get_supabase_client():
    """Get Supabase client"""
    return db_manager.get_supabase_client()

async def close_database():
    """Close database connections"""
    await db_manager.close() 