// API基础URL
const API_BASE = 'http://localhost:8000/api';

// 返回首页功能
function goBack() {
    // 返回到首页
    window.location.href = 'index.html';
}

// 表单提交处理
document.getElementById('candidateForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const candidateData = {
        name: formData.get('name'),
        email: formData.get('email'),
        invitation_code: formData.get('invitationCode') || null
    };
    
    try {
        // 显示加载状态
        const submitBtn = e.target.querySelector('.start-btn');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = '正在开始面试...';
        submitBtn.disabled = true;
        
        // 调用API开始面试
        const response = await fetch(`${API_BASE}/interview/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(candidateData)
        });
        
        if (!response.ok) {
            throw new Error('网络请求失败');
        }
        
        const result = await response.json();
        
        // 保存会话信息到localStorage
        localStorage.setItem('interviewSession', JSON.stringify({
            sessionId: result.session_id,
            candidateName: candidateData.name,
            candidateEmail: candidateData.email
        }));
        
        // 跳转到面试页面
        window.location.href = 'interview.html';
        
    } catch (error) {
        console.error('开始面试失败:', error);
        alert('开始面试失败，请检查网络连接或稍后重试');
        
        // 恢复按钮状态
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
});

// 输入验证
document.getElementById('name').addEventListener('input', function(e) {
    const value = e.target.value.trim();
    if (value.length < 2) {
        e.target.setCustomValidity('姓名至少需要2个字符');
    } else {
        e.target.setCustomValidity('');
    }
});

document.getElementById('email').addEventListener('input', function(e) {
    const value = e.target.value.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
        e.target.setCustomValidity('请输入有效的邮箱地址');
    } else {
        e.target.setCustomValidity('');
    }
});

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
    // 检查是否有保存的会话信息
    const savedSession = localStorage.getItem('interviewSession');
    if (savedSession) {
        const session = JSON.parse(savedSession);
        // 可以在这里显示"继续面试"的选项
        console.log('发现已保存的面试会话:', session);
    }
    
    // 焦点设置到第一个输入框
    document.getElementById('name').focus();
});