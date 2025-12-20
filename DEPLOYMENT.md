# 部署说明文档

## 前后端地址配置

本项目已经将所有硬编码的API地址统一管理到配置文件中，部署时只需要修改一个文件即可。

### 配置文件位置

```
frontend/js/config.js
```

### 本地开发环境

本地开发时，系统会自动检测localhost并使用 `http://localhost:8000` 作为后端API地址。

无需任何配置即可直接使用。

### 生产环境部署

部署到服务器时，需要修改 `frontend/js/config.js` 文件中的 `getApiBaseUrl()` 函数。

#### 方案1：使用相对路径（推荐）

如果前后端部署在同一个域名下，使用Nginx等反向代理：

```javascript
function getApiBaseUrl() {
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://localhost:8000';
    }
    
    // 生产环境使用相对路径
    return '';  // 空字符串表示使用相对路径
}
```

对应的Nginx配置示例：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 前端静态文件
    location / {
        root /path/to/frontend;
        index home.html;
        try_files $uri $uri/ /home.html;
    }
    
    # 后端API代理
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

#### 方案2：使用当前域名的特定端口

如果后端运行在特定端口（如8000）：

```javascript
function getApiBaseUrl() {
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://localhost:8000';
    }
    
    // 使用当前域名的8000端口
    return `${window.location.protocol}//${window.location.hostname}:8000`;
}
```

#### 方案3：使用完全自定义的域名

如果后端部署在独立的域名或子域名：

```javascript
function getApiBaseUrl() {
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://localhost:8000';
    }
    
    // 使用自定义的API域名
    return 'https://api.your-domain.com';
}
```

### 部署步骤

1. **修改配置文件**
   ```bash
   vim frontend/js/config.js
   ```
   根据你的部署方案修改 `getApiBaseUrl()` 函数

2. **上传前端文件**
   ```bash
   scp -r frontend/* user@server:/path/to/frontend/
   ```

3. **启动后端服务**
   ```bash
   cd backend
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

4. **配置Nginx（如果使用方案1）**
   ```bash
   sudo vim /etc/nginx/sites-available/your-site
   sudo nginx -t
   sudo systemctl reload nginx
   ```

5. **测试访问**
   - 访问前端页面
   - 检查浏览器控制台是否有错误
   - 测试登录、候选人列表等功能

### 验证部署

打开浏览器控制台（F12），执行以下命令验证配置：

```javascript
console.log('API Base URL:', getApiBaseUrl());
console.log('Test API URL:', buildApiUrl('/api/candidates'));
```

### 常见问题

#### 1. CORS跨域问题

如果前后端部署在不同域名，需要在后端配置CORS：

```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # 修改为实际的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 2. API调用404错误

检查：
- 后端服务是否正常运行
- API路径是否正确
- Nginx配置是否正确（如果使用反向代理）

#### 3. 静态文件加载失败

确保：
- 前端文件路径正确
- Nginx配置的root路径正确
- 文件权限正确（644）

### 安全建议

1. **使用HTTPS**
   ```nginx
   server {
       listen 443 ssl;
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       # ... 其他配置
   }
   ```

2. **配置防火墙**
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

3. **使用环境变量管理敏感信息**
   - 不要在代码中硬编码API密钥
   - 使用环境变量或配置文件管理

### 监控和日志

1. **后端日志**
   ```bash
   # 使用systemd管理后端服务
   sudo journalctl -u your-backend-service -f
   ```

2. **Nginx日志**
   ```bash
   tail -f /var/log/nginx/access.log
   tail -f /var/log/nginx/error.log
   ```

3. **前端错误监控**
   - 在浏览器控制台查看JavaScript错误
   - 使用Sentry等工具进行错误追踪

## 联系支持

如有问题，请查看项目文档或提交Issue。