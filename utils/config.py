import os
import json
from typing import Dict, Any


class ConfigManager:
    CONFIG_FILE = "bot_config.json"
    
    @classmethod
    def load_config(cls) -> Dict[str, Any]:
        if os.path.exists(cls.CONFIG_FILE):
            with open(cls.CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    @classmethod
    def save_config(cls, config: Dict[str, Any]) -> None:
        with open(cls.CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    @classmethod
    def setup_config(cls) -> Dict[str, Any]:
        config = {}
        
        print("Настройка Lolz Market Telegram Bot")
        print("=" * 50)
        
        config['bot_token'] = input("Токен Telegram бота: ").strip()
        config['lolz_api_token'] = input("Токен Lolz API: ").strip()
        
        try:
            config['check_interval_minutes'] = int(input("Интервал проверки в минутах (5): ") or "5")
        except ValueError:
            config['check_interval_minutes'] = 5
        
        try:
            config['max_price_threshold'] = int(input("Максимальная цена в рублях (10000): ") or "10000")
        except ValueError:
            config['max_price_threshold'] = 10000
        
        try:
            config['min_discount_percent'] = int(input("Минимальный процент скидки (20): ") or "20")
        except ValueError:
            config['min_discount_percent'] = 20
        
        config['database_path'] = "bot_database.db"
        
        cls.save_config(config)
        print(f"\nКонфигурация сохранена в {cls.CONFIG_FILE}")
        return config
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        config = cls.load_config()
        
        if not config.get('bot_token') or not config.get('lolz_api_token'):
            print("Конфигурация не найдена или неполная.")
            config = cls.setup_config()
        
        return config
