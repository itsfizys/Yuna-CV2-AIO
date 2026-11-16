"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
import aiosqlite
import asyncio
import os

class AdminLockDB:
    def __init__(self, db_path="db/adminlock.db"):
        self.db_path = db_path
        self._lock = asyncio.Lock()

    async def init_db(self):
        """Initialize the adminlock database and create the table if it doesn't exist"""
        async with self._lock:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS adminlock (
                        id INTEGER PRIMARY KEY,
                        locked INTEGER DEFAULT 0
                    )
                ''')
                
                # Check if there's already a record, if not create one
                cursor = await db.execute('SELECT COUNT(*) FROM adminlock')
                count = await cursor.fetchone()
                if count[0] == 0:
                    await db.execute('INSERT INTO adminlock (locked) VALUES (0)')
                
                await db.commit()

    async def is_locked(self):
        """Check if adminlock is currently active"""
        async with self._lock:
            try:
                async with aiosqlite.connect(self.db_path) as db:
                    cursor = await db.execute('SELECT locked FROM adminlock WHERE id = 1')
                    result = await cursor.fetchone()
                    return bool(result[0]) if result else False
            except Exception:
                # If table doesn't exist or any error, assume not locked
                return False

    async def set_lock(self, locked: bool):
        """Set the adminlock state"""
        async with self._lock:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('UPDATE adminlock SET locked = ? WHERE id = 1', (int(locked),))
                await db.commit()

    async def toggle_lock(self):
        """Toggle the adminlock state and return the new state"""
        current_state = await self.is_locked()
        new_state = not current_state
        await self.set_lock(new_state)
        return new_state

# Global instance
adminlock_db = AdminLockDB()