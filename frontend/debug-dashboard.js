// 简化版的dashboard.js用于调试

let currentTab = 'positions';

// 简化的标签切换功能（不进行API调用）
function switchTab(tabName) {
    console.log('切换到标签:', tabName);
    
    currentTab = tabName;
    
    // 更新导航按钮状态
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.tab === tabName) {
            btn.classList.add('active');
        }
    });
    
    // 显示对应的内容
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    const targetContent = document.getElementById(`${tabName}-content`);
    if (targetContent) {
        targetContent.classList.add('active');
        console.log('成功切换到:', tabName);
    } else {
        console.error('未找到内容元素:', `${tabName}-content`);
    }
    
    // 显示成功消息
    showMessage(`已切换到${getTabDisplayName(tabName)}`, 'success');
}

function getTabDisplayName(tabName) {
    const names = {
        'positions': '岗位管理',
        'candidates': '候选人',
        'analytics': '数据分析'
    };
    return names[tabName] || tabName;
}

function showMessage(message, type = 'info') {
    // 创建消息提示
    const messageEl = document.createElement('div');
    messageEl.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        background: ${type === 'success' ? '#4CAF50' : '#2196F3'};
        color: white;
        border-radius: 4px;
        z-index: 10000;
        font-size: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    `;
    messageEl.textContent = message;
    
    document.body.appendChild(messageEl);
    
    // 自动移除
    setTimeout(() => {
        if (messageEl.parentNode) {
            messageEl.parentNode.removeChild(messageEl);
        }
    }, 3000);
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('调试版Dashboard加载完成');
    
    // 默认显示岗位管理标签
    switchTab('positions');
    
    // 添加调试信息
    const debugInfo = document.createElement('div');
    debugInfo.style.cssText = `
        position: fixed;
        bottom: 20px;
        left: 20px;
        background: #f0f0f0;
        padding: 10px;
        border-radius: 4px;
        font-size: 12px;
        z-index: 10000;
    `;
    debugInfo.innerHTML = `
        <strong>调试模式</strong><br>
        当前标签: <span id="current-tab">${currentTab}</span><br>
        点击按钮测试切换功能
    `;
    document.body.appendChild(debugInfo);
    
    // 监听标签切换
    const originalSwitchTab = window.switchTab;
    window.switchTab = function(tabName) {
        originalSwitchTab(tabName);
        document.getElementById('current-tab').textContent = tabName;
    };
});