// API基础URL - 现在从config.js获取
// const API_BASE = 'http://localhost:8000/api';  // 已移动到config.js

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
        const response = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.INTERVIEW.START), {
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
        
        // 查询候选人ID（通过姓名或邮箱）
        let candidateId = null;
        try {
            const candidatesResponse = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.CANDIDATES.LIST));
            if (candidatesResponse.ok) {
                const candidates = await candidatesResponse.json();
                const candidate = candidates.find(c => 
                    c.name === candidateData.name || c.email === candidateData.email
                );
                if (candidate) {
                    candidateId = candidate.id;
                    console.log('找到候选人ID:', candidateId);
                }
            }
        } catch (error) {
            console.warn('查询候选人ID失败:', error);
        }
        
        // 根据候选人姓名获取岗位信息
        const positionMapping = {
            "田忠": "Python工程师服务器端开发",
            "栾平": "Python工程师服务器端开发",
            "包涵": "C端产品经理-AIGC领域",
            "乔志天": "C端产品经理-AIGC领域",
            "高飞虎": "金融海外投资新媒体内容文案编辑运营",
            "龙小天": "金融海外投资新媒体内容文案编辑运营"
        };
        
        const candidatePosition = positionMapping[candidateData.name] || "未指定岗位";
        
        console.log('候选人姓名:', candidateData.name);
        console.log('候选人ID:', candidateId);
        console.log('匹配到的岗位:', candidatePosition);
        
        // 保存会话信息到localStorage
        const sessionData = {
            sessionId: result.session_id,
            candidateId: candidateId,  // 添加候选人ID
            candidateName: candidateData.name,
            candidateEmail: candidateData.email,
            candidatePosition: candidatePosition,
            invitationCode: candidateData.invitation_code
        };
        
        console.log('准备保存的会话数据:', sessionData);
        localStorage.setItem('interviewSession', JSON.stringify(sessionData));
        
        // 验证保存是否成功
        const savedData = JSON.parse(localStorage.getItem('interviewSession'));
        console.log('保存后读取的会话数据:', savedData);
        
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