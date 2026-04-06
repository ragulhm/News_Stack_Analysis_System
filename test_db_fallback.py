import asyncio
import logging
from database.db import db_protocol

async def test_auth():
    logging.basicConfig(level=logging.INFO)
    print("--- Testing Database Connection ---")
    await db_protocol.connect()
    
    print(f"Is Offline: {db_protocol.is_offline}")
    print(f"Users Node: {type(db_protocol.users)}")
    
    print("\n--- Testing Registration ---")
    try:
        user_doc = {
            "username": "test_user_unique",
            "email": "test@example.com",
            "hashed_password": "hashed_string_here",
            "is_active": True
        }
        print("Inserting user...")
        await db_protocol.users.insert_one(user_doc)
        print("Insert successful")
        
        print("\n--- Testing Find ---")
        found = await db_protocol.users.find_one({"username": "test_user_unique"})
        print(f"Found User: {found}")
        
    except Exception as e:
        print(f"ERROR DURING TEST: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_auth())
