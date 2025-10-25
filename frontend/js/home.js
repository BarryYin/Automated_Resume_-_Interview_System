// 首页导航功能

// 进入HR管理端
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