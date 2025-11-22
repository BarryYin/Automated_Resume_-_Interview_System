// 首页导航功能

// 处理管理员访问逻辑
function handleAdminAccess() {
    console.log('=== handleAdminAccess 函数被调用 ===');
    alert('handleAdminAccess函数被调用，正在检查登录状态...');
    
    // 检查是否已经登录
    const token = localStorage.getItem('adminToken') || sessionStorage.getItem('adminToken');
    const user = localStorage.getItem('adminUser');
    
    console.log('Token:', token ? '存在' : '不存在');
    console.log('User:', user ? '存在' : '不存在');
    
    if (token && user) {
        try {
            const userData = JSON.parse(user);
            if (userData.user_type === 'admin') {
                console.log('管理员已登录，直接跳转到管理后台');
                alert('检测到管理员登录状态，跳转到管理后台');
                // 已经登录，直接跳转到管理后台
                window.location.href = 'dashboard.html';
                return;
            }
        } catch (error) {
            console.error('解析用户数据失败:', error);
            // 数据损坏，清除并跳转到登录页面
            localStorage.removeItem('adminToken');
            localStorage.removeItem('adminUser');
            sessionStorage.removeItem('adminToken');
        }
    }
    
    console.log('管理员未登录，跳转到登录页面');
    alert('未检测到登录状态，跳转到登录页面');
    // 未登录，跳转到登录页面
    window.location.href = 'admin-login-simple.html';
}

// 关闭管理员登录弹窗
function closeAdminLoginModal() {
    const modal = document.getElementById('adminLoginModal');
    modal.classList.remove('show');
}

// 显示登录表单
function showLoginModal() {
    document.getElementById('adminLoginForm').classList.remove('hidden');
    document.getElementById('adminRegisterForm').classList.add('hidden');
    document.querySelector('.modal-header h2').textContent = '管理员登录';
}

// 显示注册表单
function showRegisterModal() {
    document.getElementById('adminLoginForm').classList.add('hidden');
    document.getElementById('adminRegisterForm').classList.remove('hidden');
    document.querySelector('.modal-header h2').textContent = '注册管理员';
}

// 进入管理员登录（保留原函数）
function goToAdminLogin() {
    showAdminLoginModal();
}

// 进入HR管理端（保留原函数，供其他地方调用）
function goToHR() {
    // 添加点击动画效果
    const button = event.target;
    button.style.transform = 'scale(0.95)';
    
    setTimeout(() => {
        button.style.transform = 'scale(1)';
        // 跳转到HR管理控制台
        window.location.href = 'dashboard.html';
    }, 150);
}

// 进入候选人面试
function goToInterview() {
    // 添加点击动画效果
    const button = event.target;
    button.style.transform = 'scale(0.95)';
    
    setTimeout(() => {
        button.style.transform = 'scale(1)';
        // 跳转到候选人登录页面
        window.location.href = 'candidate-login.html';
    }, 150);
}

// 页面加载动画
document.addEventListener('DOMContentLoaded', function() {
    // 添加页面加载动画
    const cards = document.querySelectorAll('.card');
    const header = document.querySelector('.header');
    
    // 头部淡入动画
    header.style.opacity = '0';
    header.style.transform = 'translateY(-30px)';
    
    setTimeout(() => {
        header.style.transition = 'all 0.8s ease';
        header.style.opacity = '1';
        header.style.transform = 'translateY(0)';
    }, 200);
    
    // 卡片依次出现动画
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(50px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.8s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 400 + index * 200);
    });
});

// 添加键盘快捷键支持
document.addEventListener('keydown', function(e) {
    // 按 H 键快速进入HR管理端
    if (e.key.toLowerCase() === 'h' && !e.ctrlKey && !e.altKey) {
        goToHR();
    }
    
    // 按 I 键快速进入面试
    if (e.key.toLowerCase() === 'i' && !e.ctrlKey && !e.altKey) {
        goToInterview();
    }
});

// 添加鼠标跟踪效果（可选的炫酷效果）
document.addEventListener('mousemove', function(e) {
    const cards = document.querySelectorAll('.card');
    
    cards.forEach(card => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const rotateX = (y - centerY) / 10;
        const rotateY = (centerX - x) / 10;
        
        if (x >= 0 && x <= rect.width && y >= 0 && y <= rect.height) {
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(10px)`;
        } else {
            card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0px)';
        }
    });
});

// 重置卡片变换效果
document.addEventListener('mouseleave', function() {
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0px)';
    });
});

// 页面加载完成后初始化登录功能
document.addEventListener('DOMContentLoaded', function() {
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
});

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
        
        const response = await fetch('http://localhost:8000/api/auth/login', {
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
                
                // 关闭弹窗并跳转到管理后台
                setTimeout(() => {
                    closeAdminLoginModal();
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
        
        const response = await fetch('http://localhost:8000/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(registerData)
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            showSuccess('管理员账号创建成功！请登录');
            showLoginModal();
            
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

// 检查管理员登录状态
function checkAdminLoginStatus() {
    const token = localStorage.getItem('adminToken') || sessionStorage.getItem('adminToken');
    const user = localStorage.getItem('adminUser');
    
    if (token && user) {
        try {
            const userData = JSON.parse(user);
            if (userData.user_type === 'admin') {
                // 已经登录，可以直接跳转到管理后台
                // 这里不自动跳转，让用户选择
                return true;
            }
        } catch (error) {
            console.error('Parse user data error:', error);
        }
    }
    return false;
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
    loadingEl.classList.add('show');
}

function hideLoading() {
    const loadingEl = document.getElementById('loadingMessage');
    if (loadingEl) {
        loadingEl.classList.remove('show');
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