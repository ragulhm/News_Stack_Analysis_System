import json
import os
import asyncio
import logging
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import settings

class LocalNodeFallback:
    """Fallback Identity Node that stores users in a local JSON file."""
    def __init__(self, filepath: str = "database/local_identity.json"):
        self.filepath = filepath
        db_dir = os.path.dirname(self.filepath)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            
        if not os.path.exists(self.filepath) or os.path.getsize(self.filepath) == 0:
            with open(self.filepath, 'w') as f:
                json.dump([], f)

    def _read(self) -> list:
        try:
            with open(self.filepath, 'r') as f:
                content = f.read().strip()
                return json.loads(content) if content else []
        except:
            return []

    def _write(self, data: list):
        try:
            def custom_serializer(obj):
                if isinstance(obj, bytes): return obj.decode('utf-8', errors='ignore')
                return str(obj)
            with open(self.filepath, 'w') as f:
                json.dump(data, f, indent=4, default=custom_serializer)
        except Exception as e:
            logging.error(f"LOCAL_NODE_WRITE_ERROR: {str(e)}")

    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Proper local search logic."""
        await asyncio.sleep(0.01)
        data = self._read()
        for user in data:
            if all(user.get(k) == v for k, v in query.items()):
                return user
        return None

    async def insert_one(self, user_doc: Dict[str, Any]):
        """Proper local insert logic."""
        await asyncio.sleep(0.01)
        data = self._read()
        # Prevent duplicates in local storage manually
        for u in data:
            if u.get("username") == user_doc.get("username"):
                raise Exception("Duplicate Identity detected in Local Node.")
                
        data.append(user_doc)
        self._write(data)
        class MockResult:
            def __init__(self, id_val): self.inserted_id = id_val
        return MockResult(user_doc.get("username", "local_id"))

class DatabaseProtocol:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        # Instant availability
        self.users = LocalNodeFallback()
        self.is_offline = True

    async def connect(self):
        """Establish Neural Link with robust fallback."""
        mongo_uri = settings.MONGODB_URI
        if not mongo_uri or "PASSWORD_HERE" in mongo_uri or not mongo_uri.startswith("mongodb"):
            logging.warning("INSTITUTIONAL_MATRIX: Valid Cloud URI not detected. Remaining in Local Mode.")
            return

        try:
            self.client = AsyncIOMotorClient(
                mongo_uri, 
                serverSelectionTimeoutMS=1500,
                connectTimeoutMS=1500
            )
            await self.client.admin.command('ping')
            db = self.client[settings.DB_NAME]
            self.users = db[settings.COLLECTION_USERS]
            self.is_offline = False
            logging.info("INSTITUTIONAL_MATRIX: Neural Link established to database cluster.")
        except Exception as e:
            self._activate_fallback(str(e))

    def _activate_fallback(self, reason: str):
        logging.error(f"INSTITUTIONAL_MATRIX_ERROR: Link failure: {reason}")
        # Keep existing LocalNodeFallback if already initialized
        if not isinstance(self.users, LocalNodeFallback):
            self.users = LocalNodeFallback()
        self.is_offline = True

    async def disconnect(self):
        if self.client:
            self.client.close()

# Global Protocol Instance
db_protocol = DatabaseProtocol()
