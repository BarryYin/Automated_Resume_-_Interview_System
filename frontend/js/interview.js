// 面试会话管理
class InterviewSession {
    constructor() {
        this.sessionId = null;
        this.currentQuestion = 1;
        this.totalQuestions = 10;
        this.messages = [];
        this.isWaitingForResponse = false;
        this.questions = [];
        this.currentQuestionData = null;
        this.evaluations = [];
        
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
        console.log('开始面试流程');
        
        // 显示欢迎消息
        this.addMessage('ai', '您好！欢迎参加AI面试。我正在根据您的简历和岗位要求生成个性化的面试问题，请稍等...');
        
        // 生成面试问题
        await this.generateInterviewQuestions();
        
        console.log('问题生成完成，准备显示第一个问题');
        
        // 延迟显示第一个问题
        setTimeout(() => {
            console.log('开始提问第一个问题');
            this.askNextQuestion();
        }, 2000);
    }

    async generateInterviewQuestions() {
        try {
            const savedSession = localStorage.getItem('interviewSession');
            if (!savedSession) {
                console.error('没有找到保存的会话信息');
                this.addMessage('ai', '会话信息丢失，使用默认问题进行面试。');
                this.loadFallbackQuestions();
                return;
            }
            
            const session = JSON.parse(savedSession);
            console.log('候选人会话信息:', session);
            
            const requestData = {
                name: session.candidateName,
                email: session.candidateEmail,
                invitation_code: session.invitationCode || '1001'
            };
            
            console.log('发送API请求:', requestData);
            
            // 调用API生成问题
            const response = await fetch('http://localhost:8000/api/interview/generate-questions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });
            
            console.log('API响应状态:', response.status);
            
            if (response.ok) {
                const data = await response.json();
                console.log('API响应数据:', data);
                
                this.questions = data.questions;
                this.sessionId = data.session_id;
                this.totalQuestions = this.questions.length;
                
                console.log(`成功获取 ${this.totalQuestions} 个问题`);
                
                // 更新会话信息
                session.llmSessionId = this.sessionId;
                localStorage.setItem('interviewSession', JSON.stringify(session));
                
                this.addMessage('ai', '太好了！我已经为您准备了个性化的面试问题。让我们开始吧！');
            } else {
                const errorText = await response.text();
                console.error('API请求失败:', response.status, errorText);
                throw new Error(`生成问题失败: ${response.status}`);
            }
            
        } catch (error) {
            console.error('生成面试问题失败:', error);
            this.addMessage('ai', '抱歉，生成个性化问题时遇到了问题，我将使用标准问题进行面试。');
            this.loadFallbackQuestions();
        }
    }

    loadFallbackQuestions() {
        // 备用问题
        this.questions = [
            {
                id: 1,
                dimension: "Knowledge",
                question: "请简单介绍一下您自己和您的专业背景。",
                follow_up: "可以详细谈谈您的学习经历"
            },
            {
                id: 2,
                dimension: "Skill",
                question: "请描述一个您最近完成的项目或工作任务。",
                follow_up: "在这个项目中您遇到了什么挑战？"
            },
            {
                id: 3,
                dimension: "Ability",
                question: "您认为自己最大的优势是什么？",
                follow_up: "能举个具体的例子说明吗？"
            },
            {
                id: 4,
                dimension: "Personality",
                question: "请描述一下您的工作风格和性格特点。",
                follow_up: "同事们通常如何评价您？"
            },
            {
                id: 5,
                dimension: "Motivation",
                question: "为什么选择应聘这个职位？",
                follow_up: "您的职业规划是什么？"
            },
            {
                id: 6,
                dimension: "Value",
                question: "您理想的工作环境是什么样的？",
                follow_up: "您如何看待团队合作？"
            },
            {
                id: 7,
                dimension: "Knowledge",
                question: "请谈谈您对行业发展趋势的看法。",
                follow_up: "您是如何保持专业知识更新的？"
            },
            {
                id: 8,
                dimension: "Skill",
                question: "请描述一次您解决复杂问题的经历。",
                follow_up: "您的解决思路是什么？"
            },
            {
                id: 9,
                dimension: "Ability",
                question: "面对压力时，您通常如何应对？",
                follow_up: "能分享一个具体的例子吗？"
            },
            {
                id: 10,
                dimension: "Motivation",
                question: "您希望在新工作中获得什么？",
                follow_up: "您能为公司带来什么价值？"
            }
        ];
    }
    
    async askNextQuestion() {
        console.log(`准备提问第 ${this.currentQuestion} 个问题，总共 ${this.totalQuestions} 个问题`);
        console.log('当前问题数组:', this.questions);
        
        if (this.currentQuestion > this.totalQuestions) {
            console.log('所有问题已完成，结束面试');
            this.endInterview();
            return;
        }
        
        // 获取当前问题
        const questionData = this.questions[this.currentQuestion - 1];
        console.log('当前问题数据:', questionData);
        
        const question = questionData ? questionData.question : '请谈谈您对这个职位的理解。';
        const dimension = questionData ? questionData.dimension : 'Knowledge';
        
        // 显示问题和评估维度
        const dimensionNames = {
            "Knowledge": "专业知识",
            "Skill": "专业技能", 
            "Ability": "综合能力",
            "Personality": "个性特质",
            "Motivation": "求职动机",
            "Value": "价值观"
        };
        
        const dimensionText = dimensionNames[dimension] || dimension;
        const questionMessage = `问题 ${this.currentQuestion} [${dimensionText}]: ${question}`;
        
        console.log('显示问题:', questionMessage);
        this.addMessage('ai', questionMessage);
        this.currentQuestionData = questionData;
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
        const answerData = {
            question: this.currentQuestion,
            questionText: this.currentQuestionData?.question || '',
            answer: message,
            dimension: this.currentQuestionData?.dimension || 'Knowledge',
            timestamp: new Date().toISOString()
        };
        
        this.messages.push(answerData);
        this.isWaitingForResponse = false;
        
        // 显示AI正在分析
        this.showTypingIndicator();
        this.addMessage('ai', '正在分析您的回答...');
        
        // 提交回答给LLM评估
        await this.submitAnswer(answerData);
        
        this.currentQuestion++;
        this.updateProgress();
        
        setTimeout(() => {
            this.askNextQuestion();
        }, 1500);
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

    async submitAnswer(answerData) {
        try {
            const savedSession = localStorage.getItem('interviewSession');
            if (!savedSession) return;
            
            const session = JSON.parse(savedSession);
            const llmSessionId = session.llmSessionId || this.sessionId;
            
            const response = await fetch(`http://localhost:8000/api/interview/${llmSessionId}/answer`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question_id: answerData.question,
                    question: answerData.questionText,
                    answer: answerData.answer,
                    dimension: answerData.dimension
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                const evaluation = result.evaluation;
                
                this.evaluations.push({
                    question: answerData.question,
                    dimension: answerData.dimension,
                    score: evaluation.score,
                    feedback: evaluation.feedback
                });
                
                this.hideTypingIndicator();
                
                // 简单确认，不显示具体评分
                this.addMessage('ai', '感谢您的回答！');
                
                // 如果有追问，显示追问
                if (this.currentQuestionData?.follow_up && Math.random() > 0.3) {
                    setTimeout(() => {
                        this.addMessage('ai', `追问：${this.currentQuestionData.follow_up}`);
                    }, 1000);
                }
                
            } else {
                throw new Error('提交回答失败');
            }
            
        } catch (error) {
            console.error('提交回答失败:', error);
            this.hideTypingIndicator();
            this.addMessage('ai', '感谢您的回答。让我们继续下一个问题。');
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
        
        // 计算各维度平均分
        const dimensionScores = {};
        this.evaluations.forEach(evaluation => {
            if (!dimensionScores[evaluation.dimension]) {
                dimensionScores[evaluation.dimension] = [];
            }
            dimensionScores[evaluation.dimension].push(evaluation.score);
        });
        
        const avgScores = {};
        Object.keys(dimensionScores).forEach(dimension => {
            const scores = dimensionScores[dimension];
            avgScores[dimension] = Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length);
        });
        
        const totalScore = Math.round(
            Object.values(avgScores).reduce((sum, score) => sum + score, 0) / Object.keys(avgScores).length
        );
        
        // 通知后端更新CSV总分
        try {
            await fetch(`http://localhost:8000/api/candidates/${this.candidateName}/finalize-scores`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    total_score: totalScore,
                    dimension_scores: avgScores
                })
            });
        } catch (error) {
            console.error('更新总分失败:', error);
        }
        
        // 保存面试完成数据
        const completeData = {
            candidateName: this.candidateName,
            candidateEmail: this.candidateEmail,
            sessionId: this.sessionId,
            startTime: this.startTime,
            endTime: new Date().toISOString(),
            questionsAnswered: this.currentQuestion - 1,
            totalQuestions: this.totalQuestions,
            evaluations: this.evaluations,
            dimensionScores: avgScores,
            totalScore: totalScore
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