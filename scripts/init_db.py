#!/usr/bin/env python3
"""Initialize database with tables and seed data."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import engine, Base
from app import models

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Database initialized!")
