#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting SchoolBot application...${NC}"

# Wait for database to be ready (if using external database)
if [ "$DATABASE_URL" ]; then
    echo -e "${YELLOW}📊 Checking database connection...${NC}"
    python -c "
import time
import sqlite3
import sys
import os

db_path = os.getenv('DATABASE_URL', 'sqlite:///data/school.db').replace('sqlite:///', '')
max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        conn = sqlite3.connect(db_path)
        conn.close()
        print('✅ Database connection successful!')
        break
    except Exception as e:
        retry_count += 1
        print(f'⏳ Database connection attempt {retry_count}/{max_retries} failed: {e}')
        if retry_count >= max_retries:
            print('❌ Failed to connect to database after maximum retries')
            sys.exit(1)
        time.sleep(1)
"
fi

# Check if database needs seeding
if [ ! -f "/app/data/school.db" ]; then
    echo -e "${YELLOW}🌱 Database not found. Seeding with sample data...${NC}"
    python scripts/seed_data.py
    echo -e "${GREEN}✅ Database seeded successfully!${NC}"
else
    echo -e "${GREEN}✅ Database already exists${NC}"
fi

# Create data directory if it doesn't exist
mkdir -p /app/data

echo -e "${GREEN}🌟 Starting FastAPI server...${NC}"
echo -e "${YELLOW}📡 Server will be available at http://localhost:8000${NC}"
echo -e "${YELLOW}📚 API documentation at http://localhost:8000/docs${NC}"

# Execute the main command
exec "$@"