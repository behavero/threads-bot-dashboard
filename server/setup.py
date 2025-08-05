#!/usr/bin/env python3
"""
Enhanced Threads Bot Backend
A Python application for automated Threads posting
"""

from setuptools import setup, find_packages

setup(
    name="enhanced-threads-bot-backend",
    version="1.0.0",
    description="Enhanced Threads Bot Backend - Python Application",
    author="Enhanced Threads Bot Team",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "python-dotenv==1.0.0",
        "aiohttp==3.8.0",
        "requests==2.28.0",
        "instagrapi==2.0.0",
        "pydantic==2.0.0",
        "python-dateutil==2.8.0",
        "colorlog==6.7.0",
        "Pillow==9.0.0",
        "pyyaml==6.0",
        "typing-extensions==4.0.0",
        "cryptography==41.0.0",
        "fake-useragent==1.4.0",
        "python-decouple==3.8",
        "schedule==1.2.0",
        "APScheduler==3.10.0",
        "supabase==2.3.4",
        "asyncpg==0.29.0",
        "psycopg2-binary==2.9.9",
        "sqlalchemy==2.0.23",
        "alembic==1.12.1",
        "Flask==2.3.3",
        "Flask-CORS==4.0.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
) 