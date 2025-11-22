// 候选人详情页面管理
class CandidateDetail {
    constructor() {
        this.candidateId = null;
        this.candidateData = null;
        this.evaluationData = {
            knowledge: 85,
            skill: 88,
            ability: 82,
            personality: 86,
            motivation: 84,
            value: 87
        };
        this.init();
    }

    init() {
        // 从URL参数获取候选人ID
        const urlParams = new URLSearchParams(window.location.search);
        this.candidateId = urlParams.get('id');
        
        if (!this.candidateId) {
            alert('候选人ID未找到');
            this.goBack();
            return;
        }

        this.loadCandidateData();
        this.setupEventListeners();
    }

    async loadCandidateData() {
        try {
            // 从真实数据加载候选人信息
            const response = await fetch('data/real_data.json');
            const data = await response.json();
            
            this.candidateData = data.candidates.find(c => c.id == this.candidateId);
            
            if (!this.candidateData) {
                alert('候选人信息未找到');
                this.goBack();
                return;
            }

            this.renderCandidateInfo();
            this.renderEvaluation();
            
            // 加载面试对话记录
            await this.loadInterviewRecords();
            
        } catch (error) {
            console.error('加载候选人数据失败:', error);
            this.loadMockData();
        }
    }

    async loadInterviewRecords() {
        console.log('开始加载面试记录，候选人ID:', this.candidateId);
        try {
            const url = `http://localhost:8000/api/candidates/${this.candidateId}/interview-records`;
            console.log('请求URL:', url);
            
            const response = await fetch(url);
            console.log('响应状态:', response.status);
            
            if (response.ok) {
                const data = await response.json();
                console.log('面试记录数据:', data);
                this.renderInterviewRecords(data);
            } else {
                console.log('该候选人暂无面试记录，状态码:', response.status);
                this.renderNoInterviewRecords();
            }
        } catch (error) {
            console.error('加载面试记录失败:', error);
            this.renderNoInterviewRecords();
        }
    }

    renderInterviewRecords(data) {
        console.log('开始渲染面试记录');
        const recordContainer = document.querySelector('.interview-record');
        console.log('找到容器:', recordContainer);
        
        if (!data.sessions || data.sessions.length === 0) {
            console.log('没有面试会话数据');
            this.renderNoInterviewRecords();
            return;
        }

        console.log('会话数量:', data.sessions.length);
        let html = '<h2>面试对话记录</h2>';
        
        data.sessions.forEach((session, sessionIndex) => {
            html += `
                <div class="session-container">
                    <div class="session-header">
                        <h3>面试会话 ${sessionIndex + 1}</h3>
                        <div class="session-info">
                            <span class="session-date">面试时间: ${new Date(session.interview_date).toLocaleString('zh-CN')}</span>
                            <span class="session-stats">已回答 ${session.answered_questions}/${session.total_questions} 题</span>
                        </div>
                    </div>
                    ${session.strategy ? `<div class="session-strategy"><strong>面试策略：</strong>${session.strategy}</div>` : ''}
                    <div class="qa-list">
            `;
            
            session.qa_pairs.forEach((qa, index) => {
                const scoreClass = qa.score >= 80 ? 'high' : qa.score >= 60 ? 'medium' : 'low';
                html += `
                    <div class="record-item">
                        <div class="qa-header">
                            <span class="qa-number">问题 ${index + 1}</span>
                            <span class="qa-dimension">${this.getDimensionName(qa.dimension)}</span>
                            <span class="qa-score score-${scoreClass}">${qa.score} 分</span>
                        </div>
                        <div class="question">
                            <strong>面试官：</strong>${qa.question}
                            ${qa.follow_up ? `<div class="follow-up"><em>追问：${qa.follow_up}</em></div>` : ''}
                        </div>
                        <div class="answer">
                            <strong>候选人：</strong>${qa.answer || '未回答'}
                        </div>
                        ${qa.feedback ? `
                            <div class="ai-feedback">
                                <strong>AI评价：</strong>${qa.feedback}
                            </div>
                        ` : ''}
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        });
        
        recordContainer.innerHTML = html;
    }

    renderNoInterviewRecords() {
        const recordContainer = document.querySelector('.interview-record');
        recordContainer.innerHTML = `
            <h2>面试对话记录</h2>
            <div class="no-records">
                <p>该候选人暂无面试对话记录</p>
                <p class="hint">候选人完成AI面试后，对话记录将显示在这里</p>
            </div>
        `;
    }

    getDimensionName(dimension) {
        const names = {
            'Knowledge': '专业知识',
            'Skill': '专业技能',
            'Ability': '综合能力',
            'Personality': '个性特质',
            'Motivation': '求职动机',
            'Value': '价值观'
        };
        return names[dimension] || dimension;
    }

    async loadMockData() {
        // 模拟数据
        this.candidateData = {
            id: this.candidateId,
            name: '张三',
            email: 'zhangsan@example.com',
            phone: '138-0000-0000',
            position: '高级前端工程师',
            status: '已完成',
            submit_time: '2025-01-23',
            resume_folder: 'Python工程师服务器端开发',
            resume_file: '张三.pdf'
        };
        
        this.renderCandidateInfo();
        this.renderEvaluation();
        
        // 加载面试对话记录
        await this.loadInterviewRecords();
    }

    renderCandidateInfo() {
        // 渲染基本信息
        document.getElementById('candidateName').textContent = `${this.candidateData.name} - 候选人详情`;
        document.getElementById('position').textContent = this.candidateData.position;
        document.getElementById('phone').textContent = this.candidateData.phone || this.candidateData.email;
        document.getElementById('status').textContent = this.candidateData.status;
        document.getElementById('submitTime').textContent = this.candidateData.submit_time || this.candidateData.interview_date || '未知';
        
        // 设置状态样式
        const statusElement = document.getElementById('status');
        statusElement.className = `status-badge ${this.getStatusClass(this.candidateData.status)}`;
    }

    renderEvaluation() {
        // 渲染评分
        const dimensions = ['knowledge', 'skill', 'ability', 'personality', 'motivation', 'value'];
        
        dimensions.forEach(dimension => {
            const score = this.evaluationData[dimension];
            document.getElementById(`${dimension}Score`).textContent = `${score} 分`;
            document.getElementById(`${dimension}Progress`).style.width = `${score}%`;
        });

        // 计算总分
        const totalScore = Math.round(
            Object.values(this.evaluationData).reduce((sum, score) => sum + score, 0) / 6
        );
        document.getElementById('totalScore').textContent = `${totalScore} 分`;
    }

    getStatusClass(status) {
        switch(status) {
            case '已完成': return 'completed';
            case '面试中': return 'in-progress';
            case '待面试': return 'pending';
            default: return 'pending';
        }
    }

    setupEventListeners() {
        // 设置各种事件监听器
        window.goBack = () => this.goBack();
        window.viewResume = () => this.viewResume();
        window.sendEmail = () => this.sendEmail();
        window.editDimension = (dimension) => this.editDimension(dimension);
        window.editFeedback = (type) => this.editFeedback(type);
        window.exportReport = () => this.exportReport();
        window.scheduleInterview = () => this.scheduleInterview();
        window.approveCandidate = () => this.approveCandidate();
        window.rejectCandidate = () => this.rejectCandidate();
    }

    goBack() {
        window.history.back();
    }

    viewResume() {
        if (this.candidateData.resume_folder && this.candidateData.resume_file) {
            // 使用PDF查看器
            if (window.pdfViewer) {
                pdfViewer.showPDFModal(this.candidateData.resume_folder, this.candidateData.resume_file);
            } else {
                alert('PDF查看器未加载');
            }
        } else {
            alert('简历文件信息未找到');
        }
    }

    sendEmail() {
        const email = this.candidateData.email;
        const subject = `关于您应聘${this.candidateData.position}职位`;
        const mailtoLink = `mailto:${email}?subject=${encodeURIComponent(subject)}`;
        window.open(mailtoLink);
    }

    editDimension(dimension) {
        const dimensionNames = {
            knowledge: '专业知识 (Knowledge)',
            skill: '专业技能 (Skill)',
            ability: '综合素质与能力 (Ability)',
            personality: '个性特质 (Personality)',
            motivation: '求职动机 (Motivation)',
            value: '价值观 (Value)'
        };

        const currentScore = this.evaluationData[dimension];
        const newScore = prompt(`请输入${dimensionNames[dimension]}的评分 (0-100):`, currentScore);
        
        if (newScore !== null && !isNaN(newScore)) {
            const score = Math.max(0, Math.min(100, parseInt(newScore)));
            this.evaluationData[dimension] = score;
            this.renderEvaluation();
            this.saveEvaluation();
        }
    }

    editFeedback(type) {
        const feedbackTypes = {
            strengths: '优势亮点',
            improvements: '待改进项'
        };

        const currentList = document.getElementById(`${type}List`);
        const items = Array.from(currentList.children).map(li => li.textContent);
        
        const newItems = prompt(
            `请编辑${feedbackTypes[type]} (每行一项):`,
            items.join('\n')
        );

        if (newItems !== null) {
            const itemsArray = newItems.split('\n').filter(item => item.trim());
            currentList.innerHTML = itemsArray.map(item => `<li>${item.trim()}</li>`).join('');
        }
    }

    async saveEvaluation() {
        try {
            // 这里应该调用API保存评分数据
            console.log('保存评分数据:', this.evaluationData);
            
            // 模拟API调用
            const response = await fetch(`http://localhost:8000/api/candidates/${this.candidateId}/evaluation`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    candidate_id: this.candidateId,
                    evaluation: this.evaluationData,
                    total_score: Math.round(
                        Object.values(this.evaluationData).reduce((sum, score) => sum + score, 0) / 6
                    )
                })
            });

            if (response.ok) {
                console.log('评分保存成功');
            }
        } catch (error) {
            console.error('保存评分失败:', error);
        }
    }

    exportReport() {
        // 生成候选人评估报告
        const report = this.generateReport();
        
        const blob = new Blob([report], { type: 'text/plain;charset=utf-8' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `候选人评估报告_${this.candidateData.name}_${new Date().toLocaleDateString('zh-CN')}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }

    generateReport() {
        const totalScore = Math.round(
            Object.values(this.evaluationData).reduce((sum, score) => sum + score, 0) / 6
        );

        return `
候选人评估报告
==========================================

基本信息：
姓名：${this.candidateData.name}
邮箱：${this.candidateData.email}
应聘职位：${this.candidateData.position}
面试状态：${this.candidateData.status}
评估时间：${new Date().toLocaleString('zh-CN')}

评分详情：
总分：${totalScore} 分

各维度评分：
1. 专业知识 (Knowledge)：${this.evaluationData.knowledge} 分
2. 专业技能 (Skill)：${this.evaluationData.skill} 分
3. 综合素质与能力 (Ability)：${this.evaluationData.ability} 分
4. 个性特质 (Personality)：${this.evaluationData.personality} 分
5. 求职动机 (Motivation)：${this.evaluationData.motivation} 分
6. 价值观 (Value)：${this.evaluationData.value} 分

评估总结：
${this.getEvaluationSummary(totalScore)}

报告生成时间：${new Date().toLocaleString('zh-CN')}
==========================================
        `.trim();
    }

    getEvaluationSummary(totalScore) {
        if (totalScore >= 90) {
            return '优秀候选人，强烈推荐录用。各项能力均表现突出，完全符合岗位要求。';
        } else if (totalScore >= 80) {
            return '良好候选人，推荐录用。整体表现良好，基本符合岗位要求。';
        } else if (totalScore >= 70) {
            return '一般候选人，可考虑录用。部分能力需要进一步培养。';
        } else {
            return '不推荐录用。综合能力与岗位要求存在较大差距。';
        }
    }

    scheduleInterview() {
        alert('安排复试功能开发中...');
    }

    approveCandidate() {
        if (confirm(`确定通过候选人 ${this.candidateData.name} 吗？`)) {
            alert('候选人已通过！');
            // 这里应该调用API更新候选人状态
        }
    }

    rejectCandidate() {
        if (confirm(`确定拒绝候选人 ${this.candidateData.name} 吗？`)) {
            const reason = prompt('请输入拒绝原因（可选）:');
            alert('候选人已拒绝！');
            // 这里应该调用API更新候选人状态
        }
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    new CandidateDetail();
});