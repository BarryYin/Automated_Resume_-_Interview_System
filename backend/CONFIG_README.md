# 配置说明

## 配置文件

系统使用 `config.json` 文件来管理配置项。首次运行时会自动创建默认配置文件。

### 配置文件位置

```
backend/config.json
```

### 配置文件示例

参考 `config.json.example` 文件：

```json
{
    "llm": {
        "api_key": "your-api-key-here",
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
        "sender_email": "your-email@example.com",
        "sender_password": "your-password"
    },
    "jwt": {
        "secret_key": "your-secret-key-here",
        "expire_days": 7
    }
}
```

## 配置项说明

### LLM配置 (llm)

- **api_key**: 通义千问API密钥
- **base_url**: API基础URL
- **model**: 使用的模型名称（qwen-plus, qwen-max等）
- **temperature**: 生成温度（0-1，越高越随机）
- **max_tokens**: 最大生成token数

### 数据库配置 (database)

- **path**: 数据库文件路径

### 邮件配置 (email)

- **smtp_server**: SMTP服务器地址
- **smtp_port**: SMTP端口
- **sender_email**: 发件人邮箱
- **sender_password**: 邮箱密码或授权码

### JWT配置 (jwt)

- **secret_key**: JWT签名密钥
- **expire_days**: Token过期天数

## 使用环境变量

你也可以使用环境变量来覆盖配置：

```bash
export LLM_API_KEY="your-api-key"
export LLM_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
```

环境变量优先级高于配置文件。

## 首次配置步骤

1. 复制示例配置文件：
   ```bash
   cp config.json.example config.json
   ```

2. 编辑 `config.json`，填入你的API密钥：
   ```json
   {
       "llm": {
           "api_key": "sk-your-actual-api-key-here"
       }
   }
   ```

3. 启动服务：
   ```bash
   python3 main.py
   ```

## 安全提示

⚠️ **重要**: 
- 不要将 `config.json` 提交到版本控制系统
- 已添加到 `.gitignore` 中
- 使用 `config.json.example` 作为模板分享

## 配置文件优先级

1. 环境变量（最高优先级）
2. config.json 用户配置
3. 默认配置（最低优先级）
