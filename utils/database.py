import aiosqlite
import json
from typing import List, Optional
from utils.models import UserSettings


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    settings TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            await db.execute('''
                CREATE TABLE IF NOT EXISTS seen_items (
                    item_id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            await db.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    item_id INTEGER,
                    message TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            await db.commit()
    
    async def save_user_settings(self, user_id: int, settings: UserSettings):
        data = {
            'categories': settings.categories,
            'min_price': settings.min_price,
            'max_price': settings.max_price,
            'game_versions': settings.game_versions or [],
            'regions': settings.regions or [],
            'origins': settings.origins or [],
            'min_level': settings.min_level,
            'max_level': settings.max_level,
            'order_by': settings.order_by,
            'show': settings.show,
            'nsb': settings.nsb,
            'sb': settings.sb,
            'email_login_data': settings.email_login_data,
            'pve_access': settings.pve_access,
            'notifications_enabled': settings.notifications_enabled,
            'max_discount_threshold': settings.max_discount_threshold
        }
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO users (user_id, settings, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, json.dumps(data)))
            await db.commit()
    
    async def get_user_settings(self, user_id: int) -> Optional[UserSettings]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('SELECT settings FROM users WHERE user_id = ?', (user_id,))
            row = await cursor.fetchone()
            
            if not row:
                return None
            
            data = json.loads(row[0])
            return UserSettings(
                user_id=user_id,
                categories=data.get('categories', []),
                min_price=data.get('min_price'),
                max_price=data.get('max_price'),
                game_versions=data.get('game_versions', []),
                regions=data.get('regions', []),
                origins=data.get('origins', []),
                min_level=data.get('min_level'),
                max_level=data.get('max_level'),
                order_by=data.get('order_by', 'price_to_up'),
                show=data.get('show', 'active'),
                nsb=data.get('nsb'),
                sb=data.get('sb'),
                email_login_data=data.get('email_login_data'),
                pve_access=data.get('pve_access'),
                notifications_enabled=data.get('notifications_enabled', True),
                max_discount_threshold=data.get('max_discount_threshold', 20)
            )
    
    async def get_all_users(self) -> List[int]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('SELECT user_id FROM users')
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
    
    async def mark_item_seen(self, user_id: int, item_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('INSERT OR IGNORE INTO seen_items (item_id, user_id) VALUES (?, ?)', (item_id, user_id))
            await db.commit()
    
    async def is_item_seen(self, user_id: int, item_id: int) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('SELECT 1 FROM seen_items WHERE item_id = ? AND user_id = ?', (item_id, user_id))
            return await cursor.fetchone() is not None
    
    async def save_notification(self, user_id: int, item_id: int, message: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('INSERT INTO notifications (user_id, item_id, message) VALUES (?, ?, ?)', (user_id, item_id, message))
            await db.commit()
    
    async def cleanup_old_seen_items(self, days: int = 7):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(f"DELETE FROM seen_items WHERE seen_at < datetime('now', '-{days} days')")
            await db.commit()
