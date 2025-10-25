// 面试完成页面功能

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    loadInterviewData();
    startCountdown();
});

// 加载面试数据
function loadInterviewData() {
    // 从localStorage获取面试数据
    const interviewData = localStorage.getItem('interviewComplete');
    
    if (interviewData) {
        const data = JSON.parse(interviewData);
        
        // 显示候选人姓名
        document.getElementById('candidateNameComplete').textContent = data.candidateName || '候选人';
        
        // 显示面试时长
        const duration = calculateDuration(data.startTime, data.endTime);
        document.getElementById('interviewDuration').textContent = duration;
        
        // 显示回答问题数
        document.getElementById('questionsAnswered').textContent = `${data.questionsAnswered || 0} 题`;
        
    } else {
        // 如果没有数据，使用默认值
        document.getElementById('candidateNameComplete').textContent = '候选人';
        document.getElementById('interviewDuration').textContent = '未知';
        document.getElementById('questionsAnswered').textContent = '0 题';
    }
}

// 计算面试时长
function calculateDuration(startTime, endTime) {
    if (!startTime || !endTime) return '未知';
    
    const start = new Date(startTime);
    const end = new Date(endTime);
    const diffMs = end - start;
    
    const minutes = Math.floor(diffMs / 60000);
    const seconds = Math.floor((diffMs % 60000) / 1000);
    
    if (minutes > 0) {
        return `${minutes} 分 ${seconds} 秒`;
    } else {
        return `${seconds} 秒`;
    }
}

// 返回首页
function goHome() {
    // 清除面试相关的localStorage数据
    localStorage.removeItem('interviewSession');
    localStorage.removeItem('interviewComplete');
    
    // 添加按钮点击效果
    const button = event.target;
    button.style.transform = 'scale(0.95)';
    
    setTimeout(() => {
        window.location.href = 'index.html';
    }, 150);
}

// 下载面试报告
function downloadReport() {
    const button = event.target;
    const originalText = button.textContent;
    
    // 显示加载状态
    button.textContent = '生成中...';
    button.disabled = true;
    
    // 模拟报告生成
    setTimeout(() => {
        // 获取面试数据
        const interviewData = localStorage.getItem('interviewComplete');
        const data = interviewData ? JSON.parse(interviewData) : {};
        
        // 创建报告内容
        const reportContent = generateReportContent(data);
        
        // 创建并下载文件
        const blob = new Blob([reportContent], { type: 'text/plain;charset=utf-8' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `面试报告_${data.candidateName || '候选人'}_${new Date().toLocaleDateString('zh-CN')}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        // 恢复按钮状态
        button.textContent = originalText;
        button.disabled = false;
        
        // 显示成功提示
        showNotification('报告下载成功！', 'success');
        
    }, 2000);
}

// 生成报告内容
function generateReportContent(data) {
    const now = new Date();
    const reportDate = now.toLocaleString('zh-CN');
    
    return `
AI面试报告
==========================================

候选人信息：
姓名：${data.candidateName || '未知'}
邮箱：${data.candidateEmail || '未知'}
面试时间：${reportDate}

面试统计：
面试时长：${calculateDuration(data.startTime, data.endTime)}
回答问题数：${data.questionsAnswered || 0} 题
面试状态：已完成

面试概要：
本次AI面试已成功完成。候选人回答了 ${data.questionsAnswered || 0} 个问题，
表现出良好的沟通能力和专业素养。

后续流程：
1. AI系统正在分析回答内容
2. HR团队将在2-3个工作日内审核
3. 结果将通过邮件通知候选人
4. 如需进一步面试，将及时联系

报告生成时间：${reportDate}
==========================================
    `.trim();
}

// 显示通知
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // 样式
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#28a745' : '#007bff'};
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1000;
        animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // 3秒后自动移除
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// 添加动画样式
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// 倒计时功能（可选）
function startCountdown() {
    // 可以添加一个倒计时，比如30秒后自动跳转
    // 这里暂时不实现，根据需要可以添加
}

// 键盘快捷键
document.addEventListener('keydown', function(e) {
    // 按 Enter 键返回首页
    if (e.key === 'Enter') {
        goHome();
    }
    
    // 按 D 键下载报告
    if (e.key.toLowerCase() === 'd' && !e.ctrlKey && !e.altKey) {
        downloadReport();
    }
});