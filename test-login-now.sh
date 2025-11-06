#!/bin/bash
# Test actual login and show detailed response

echo "🔐 TESTING LOGIN"
echo "================"
echo ""

echo "1️⃣  Testing login with admin/admin123..."
echo ""

RESPONSE=$(curl -s -X POST "http://localhost/api/v1/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin&password=admin123" \
    -w "\nHTTP_CODE:%{http_code}")

echo "Response:"
echo "$RESPONSE"
echo ""

# Extract HTTP code
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | grep -v "HTTP_CODE")

if echo "$BODY" | grep -q "access_token"; then
    echo "✅ LOGIN SUCCESSFUL!"
    echo ""
    echo "Token:"
    echo "$BODY" | grep -o '"access_token":"[^"]*"'
else
    echo "❌ LOGIN FAILED"
    echo "HTTP Code: $HTTP_CODE"
    echo ""

    # Check what error we got
    if echo "$BODY" | grep -q "Incorrect username or password"; then
        echo "Error: Incorrect username or password"
        echo ""
        echo "This means:"
        echo "- User exists in database ✅"
        echo "- But password doesn't match ❌"
        echo ""
        echo "Let's check the password hash in database..."
        docker compose -f docker-compose.tier-c.yml exec backend sqlite3 /data/easm.db \
            "SELECT username, substr(hashed_password, 1, 50) as hash_preview FROM users WHERE username='admin';" 2>/dev/null
    else
        echo "Unexpected error: $BODY"
    fi
fi

echo ""
echo "2️⃣  Let's verify the user in database..."
docker compose -f docker-compose.tier-c.yml exec backend sqlite3 /data/easm.db \
    "SELECT username, email, is_active, is_superuser, role FROM users WHERE username='admin';" 2>/dev/null

echo ""
echo "3️⃣  Test direct Python authentication..."
cat > /tmp/test_auth.py << 'EOF'
import asyncio
import sys
sys.path.insert(0, '/app')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.user import User
from app.core.security import verify_password

async def test_auth():
    engine = create_async_engine("sqlite+aiosqlite:////data/easm.db")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        stmt = select(User).where(User.username == "admin")
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            print("❌ User not found in database")
            return

        print(f"✅ User found: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Active: {user.is_active}")
        print(f"   Hash starts with: {user.hashed_password[:20]}...")

        # Test password
        if verify_password("admin123", user.hashed_password):
            print("✅ Password 'admin123' is CORRECT!")
        else:
            print("❌ Password 'admin123' does NOT match hash!")
            print("")
            print("Trying to create correct hash...")
            from app.core.security import get_password_hash
            correct_hash = get_password_hash("admin123")
            print(f"Correct hash would be: {correct_hash[:50]}...")

asyncio.run(test_auth())
EOF

echo "Running authentication test inside container..."
docker compose -f docker-compose.tier-c.yml exec backend python /tmp/test_auth.py 2>/dev/null || echo "❌ Test script failed"

echo ""
echo "================"
