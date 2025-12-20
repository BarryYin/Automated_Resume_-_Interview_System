// 管理员登录页面JavaScript

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeAdminLogin();
});

function initializeAdminLogin() {
    // 绑定登录表单提交事件
    const loginForm = document.getElementById('adminLoginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleAdminLogin);
    }
    
    // 绑定注册表单提交事件
    const registerForm = document.getElementById('adminRegisterForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleAdminRegister);
    }
    
    // 检查是否已经登录
    checkAdminLoginStatus();
}

// 处理管理员登录
async function handleAdminLogin(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const loginData = {
        email: formData.get('email'),
        password: formData.get('password'),
        user_type: 'admin' // 标识为管理员登录
    };
    
    try {
        showLoading('正在验证管理员身份...');
        
        const response = await fetch(buildApiUrl('/api/auth/login'), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(loginData)
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            // 验证用户类型是否为管理员
            if (result.user && result.user.user_type === 'admin') {
                // 保存登录信息
                localStorage.setItem('adminToken', result.token);
                localStorage.setItem('adminUser', JSON.stringify(result.user));
                
                // 记住我功能
                const rememberMe = document.getElementById('rememberMe').checked;
                if (rememberMe) {
                    localStorage.setItem('rememberAdmin', 'true');
                } else {
                    sessionStorage.setItem('adminToken', result.token);
                }
                
                showSuccess('登录成功！正在跳转到管理后台...');
                
                // 跳转到管理后台
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1500);
            } else {
                showError('该账号不是管理员账号，请使用管理员权限的账号登录');
            }
        } else {
            showError(result.message || '登录失败，请检查邮箱和密码');
        }
    } catch (error) {
        console.error('Admin login error:', error);
        showError('网络连接失败，请稍后重试');
    } finally {
        hideLoading();
    }
}

// 处理管理员注册
async function handleAdminRegister(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const password = formData.get('password');
    const confirmPassword = formData.get('confirmPassword');
    
    // 验证密码
    if (password !== confirmPassword) {
        showError('两次输入的密码不一致');
        return;
    }
    
    if (password.length < 6) {
        showError('密码长度至少为6位');
        return;
    }
    
    const registerData = {
        name: formData.get('name'),
        email: formData.get('email'),
        password: password,
        user_type: 'admin' // 标识为管理员注册
    };
    
    try {
        showLoading('正在创建管理员账号...');
        
        const response = await fetch(buildApiUrl('/api/auth/register'), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(registerData)
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            showSuccess('管理员账号创建成功！请登录');
            showLoginForm();
            
            // 自动填充邮箱
            document.getElementById('adminEmail').value = registerData.email;
        } else {
            showError(result.message || '注册失败，请稍后重试');
        }
    } catch (error) {
        console.error('Admin register error:', error);
        showError('网络连接失败，请稍后重试');
    } finally {
        hideLoading();
    }
}

// 显示登录表单
function showLoginForm() {
    document.getElementById('adminLoginForm').classList.remove('hidden');
    document.getElementById('adminRegisterForm').classList.add('hidden');
    document.querySelector('.login-header h1').textContent = '管理员登录';
    document.querySelector('.login-header .subtitle').textContent = '请使用管理员账号登录系统';
}

// 显示注册表单
function showRegisterForm() {
    document.getElementById('adminLoginForm').classList.add('hidden');
    document.getElementById('adminRegisterForm').classList.remove('hidden');
    document.querySelector('.login-header h1').textContent = '注册管理员';
    document.querySelector('.login-header .subtitle').textContent = '创建新的管理员账号';
}

// 显示忘记密码
function showForgotPassword() {
    showMessage('请联系系统管理员重置密码', 'info');
}

// 检查管理员登录状态
function checkAdminLoginStatus() {
    const token = localStorage.getItem('adminToken') || sessionStorage.getItem('adminToken');
    const user = localStorage.getItem('adminUser');
    
    if (token && user) {
        try {
            const userData = JSON.parse(user);
            if (userData.user_type === 'admin') {
                // 已经登录，跳转到管理后台
                window.location.href = 'dashboard.html';
                return;
            }
        } catch (error) {
            console.error('Parse user data error:', error);
        }
    }
}

// 返回首页
function goHome() {
    window.location.href = 'index.html';
}

// 工具函数
function showLoading(message = '加载中...') {
    // 创建或显示加载提示
    let loadingEl = document.getElementById('loadingMessage');
    if (!loadingEl) {
        loadingEl = document.createElement('div');
        loadingEl.id = 'loadingMessage';
        loadingEl.className = 'message loading';
        document.body.appendChild(loadingEl);
    }
    loadingEl.textContent = message;
    loadingEl.style.display = 'block';
}

function hideLoading() {
    const loadingEl = document.getElementById('loadingMessage');
    if (loadingEl) {
        loadingEl.style.display = 'none';
    }
}

function showSuccess(message) {
    showMessage(message, 'success');
}

function showError(message) {
    showMessage(message, 'error');
}

function showMessage(message, type = 'info') {
    // 创建消息提示
    const messageEl = document.createElement('div');
    messageEl.className = `message ${type}`;
    messageEl.textContent = message;
    
    // 添加到页面
    document.body.appendChild(messageEl);
    
    // 显示动画
    setTimeout(() => {
        messageEl.classList.add('show');
    }, 100);
    
    // 自动隐藏
    setTimeout(() => {
        messageEl.classList.remove('show');
        setTimeout(() => {
            if (messageEl.parentNode) {
                messageEl.parentNode.removeChild(messageEl);
            }
        }, 300);
    }, 3000);
}