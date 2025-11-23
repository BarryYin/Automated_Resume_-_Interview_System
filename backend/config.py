"""
配置文件 - 管理系统配置项
"""
import os
import json
from pathlib import Path


class Config:
    """系统配置类"""
    
    def __init__(self):
        self.config_file = Path(__file__).parent / "config.json"
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        # 默认配置
        default_config = {
            "llm": {
                "api_key": "sk-b20dbc29a6ab4ada8b4711d8b817f7cb",
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "model": "qwen-plus",
                "temperature": 0.7,
                "max_tokens": 2000
            },
            "database": {
                "path": "recruitment.db"
            },
            "email": {
                "smtp_server": "smtp.example.com",
                "smtp_port": 587,
                "sender_email": "",
                "sender_password": ""
            },
            "jwt": {
                "secret_key": "your-secret-key-here",
                "expire_days": 7
            }
        }
        
        # 如果配置文件存在，加载并合并
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 合并配置（用户配置覆盖默认配置）
                    self._merge_config(default_config, user_config)
            except Exception as e:
                print(f"加载配置文件失败: {e}，使用默认配置")
        else:
            # 创建默认配置文件
            self.save_config(default_config)
            print(f"已创建默认配置文件: {self.config_file}")
        
        # 支持从环境变量覆盖配置
        if os.getenv('LLM_API_KEY'):
            default_config['llm']['api_key'] = os.getenv('LLM_API_KEY')
        if os.getenv('LLM_BASE_URL'):
            default_config['llm']['base_url'] = os.getenv('LLM_BASE_URL')
        
        return default_config
    
    def _merge_config(self, default, user):
        """递归合并配置"""
        for key, value in user.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_config(default[key], value)
            else:
                default[key] = value
    
    def save_config(self, config=None):
        """保存配置到文件"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            print(f"配置已保存到: {self.config_file}")
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def get(self, key_path, default=None):
        """
        获取配置项
        例如: config.get('llm.api_key')
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path, value):
        """
        设置配置项
        例如: config.set('llm.api_key', 'new-key')
        """
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
        self.save_config()


# 全局配置实例
config = Config()
