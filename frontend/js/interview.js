// 面试会话管理
class InterviewSession {
    constructor() {
        this.sessionId = null;
        this.currentQuestion = 1;
        this.totalQuestions = 10;
        this.messages = [];
        this.isWaitingForResponse = false;
        
        this.init();
    }
    
    init() {
        // 从localStorage获取会话信息
        const savedSession = localStorage.getItem('interviewSession');
        if (savedSession) {
            const session = JSON.parse(savedSession);
            this.sessionId = session.sessionId;
            this.candidateName = session.candidateName;
            this.candidateEmail = session.candidateEmail;
            this.startTime = new Date().toISOString();
            
            // 显示候选人姓名
            document.getElementById('candidateName').textContent = this.candidateName;
        } else {
            // 如果没有会话信息，跳转回首页
            window.location.href = 'index.html';
            return;
        }
        
        // 初始化UI
        this.updateProgress();
        this.setupEventListeners();
        
        // 开始第一个问题
        this.startInterview();
    }
    
    setupEventListeners() {
        const chatInput = document.getElementById('chatInput');
        const sendBtn = document.getElementById('sendBtn');
        
        // 发送按钮点击事件
        sendBtn.addEventListener('click', () => this.sendMessage());
        
        // 输入框键盘事件
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // 自动调整输入框高度
        chatInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
    }
    
    async startInterview() {
        // 显示欢迎消息
        this.addMessage('ai', '您好！欢迎参加AI面试。我将根据您的简历和岗位要求进行提问。请放轻松，如实回答即可。');
        
        // 延迟显示第一个问题
        setTimeout(() => {
            this.askNextQuestion();
        }, 2000);
    }
    
    async askNextQuestion() {
        if (this.currentQuestion > this.totalQuestions) {
            this.endInterview();
            return;
        }
        
        // 模拟AI生成问题
        const questions = [
            '请简单介绍一下您自己和您的工作经验。',
            '您为什么对这个职位感兴趣？',
            '请描述一个您在工作中遇到的挑战以及如何解决的。',
            '您认为自己最大的优势是什么？',
            '您如何处理工作压力？',
            '请谈谈您的职业规划。',
            '您在团队合作中通常扮演什么角色？',
            '您如何保持技能的更新？',
            '请描述一次您主动承担额外责任的经历。',
            '您对我们公司有什么了解？'
        ];
        
        const question = questions[this.currentQuestion - 1] || '请谈谈您对这个职位的理解。';
        
        this.addMessage('ai', `问题 ${this.currentQuestion}: ${question}`);
        this.isWaitingForResponse = true;
    }
    
    async sendMessage() {
        const chatInput = document.getElementById('chatInput');
        const message = chatInput.value.trim();
        
        if (!message || this.isWaitingForResponse === false) {
            return;
        }
        
        // 添加用户消息
        this.addMessage('user', message);
        chatInput.value = '';
        chatInput.style.height = 'auto';
        
        // 保存回答
        this.messages.push({
            question: this.currentQuestion,
            answer: message,
            timestamp: new Date().toISOString()
        });
        
        this.isWaitingForResponse = false;
        
        // 显示AI正在分析
        this.showTypingIndicator();
        
        // 模拟AI分析时间
        setTimeout(() => {
            this.hideTypingIndicator();
            this.addMessage('ai', '感谢您的回答。让我们继续下一个问题。');
            
            this.currentQuestion++;
            this.updateProgress();
            
            setTimeout(() => {
                this.askNextQuestion();
            }, 1500);
        }, 2000 + Math.random() * 2000);
    }
    
    addMessage(sender, content) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const timestamp = new Date().toLocaleTimeString('zh-CN', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text">${content}</div>
                <div class="message-time">${timestamp}</div>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    showTypingIndicator() {
        const chatMessages = document.getElementById('chatMessages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message ai-message typing-indicator';
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = `
            <div class="message-content">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    updateProgress() {
        document.getElementById('currentQuestion').textContent = this.currentQuestion;
        const progressFill = document.getElementById('progressFill');
        const percentage = (this.currentQuestion / this.totalQuestions) * 100;
        progressFill.style.width = `${percentage}%`;
    }
    
    async endInterview() {
        this.addMessage('ai', '面试已结束！感谢您的参与。我们会尽快处理您的申请并与您联系。');
        
        // 禁用输入
        document.getElementById('chatInput').disabled = true;
        document.getElementById('sendBtn').disabled = true;
        
        // 保存面试完成数据
        const completeData = {
            candidateName: this.candidateName,
            candidateEmail: this.candidateEmail,
            sessionId: this.sessionId,
            startTime: this.startTime,
            endTime: new Date().toISOString(),
            questionsAnswered: this.currentQuestion - 1,
            totalQuestions: this.totalQuestions
        };
        
        localStorage.setItem('interviewComplete', JSON.stringify(completeData));
        
        // 延迟跳转到完成页面
        setTimeout(() => {
            window.location.href = 'interview-complete.html';
        }, 2000);
    }
}

// 结束面试功能
function endInterview() {
    // 创建自定义确认对话框
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    `;
    
    modal.innerHTML = `
        <div style="
            background: white;
            padding: 32px;
            border-radius: 16px;
            max-width: 400px;
            text-align: center;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        ">
            <h3 style="margin-bottom: 16px; color: #dc3545;">确认结束面试</h3>
            <p style="margin-bottom: 24px; color: #666; line-height: 1.5;">
                确定要结束面试吗？<br>
                结束后将无法继续回答问题。
            </p>
            <div style="display: flex; gap: 12px; justify-content: center;">
                <button id="cancelEnd" style="
                    padding: 12px 24px;
                    border: 2px solid #dee2e6;
                    background: white;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: 500;
                ">继续面试</button>
                <button id="confirmEnd" style="
                    padding: 12px 24px;
                    border: none;
                    background: #dc3545;
                    color: white;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: 500;
                ">确认结束</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // 绑定事件
    document.getElementById('cancelEnd').onclick = () => {
        document.body.removeChild(modal);
    };
    
    document.getElementById('confirmEnd').onclick = () => {
        document.body.removeChild(modal);
        interview.endInterview();
    };
    
    // 点击背景关闭
    modal.onclick = (e) => {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    };
}

// 页面加载完成后初始化
let interview;
document.addEventListener('DOMContentLoaded', function() {
    interview = new InterviewSession();
});

// 添加消息样式到CSS中
const style = document.createElement('style');
style.textContent = `
    .message {
        margin-bottom: 16px;
        display: flex;
    }
    
    .ai-message {
        justify-content: flex-start;
    }
    
    .user-message {
        justify-content: flex-end;
    }
    
    .message-content {
        max-width: 70%;
        padding: 12px 16px;
        border-radius: 12px;
        position: relative;
    }
    
    .ai-message .message-content {
        background: #f0f0f0;
        color: #333;
    }
    
    .user-message .message-content {
        background: #007bff;
        color: white;
    }
    
    .message-text {
        margin-bottom: 4px;
        line-height: 1.4;
    }
    
    .message-time {
        font-size: 11px;
        opacity: 0.7;
    }
    
    .typing-indicator .message-content {
        background: #f0f0f0;
        padding: 16px;
    }
    
    .typing-dots {
        display: flex;
        gap: 4px;
    }
    
    .typing-dots span {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #999;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
    .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes typing {
        0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
        40% { transform: scale(1); opacity: 1; }
    }
`;
document.head.appendChild(style);