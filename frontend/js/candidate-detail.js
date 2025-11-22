// 候选人详情页面管理
class CandidateDetail {
    constructor() {
        this.candidateId = null;
        this.candidateData = null;
        this.evaluationData = {
            knowledge: null,
            skill: null,
            ability: null,
            personality: null,
            motivation: null,
            value: null
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
            // 优先从后端API加载最新的候选人信息
            const apiResponse = await fetch('http://localhost:8000/api/candidates');
            
            if (apiResponse.ok) {
                const candidates = await apiResponse.json();
                this.candidateData = candidates.find(c => c.id == this.candidateId);
                
                if (this.candidateData) {
                    console.log('从API加载候选人数据:', this.candidateData);
                    
                    // 从候选人数据中提取评分信息
                    this.extractScoresFromCandidate();

                    this.renderCandidateInfo();
                    this.renderEvaluation();
                    
                    // 尝试从后端加载更详细的评分数据
                    await this.loadEvaluationFromAPI();
                    
                    // 加载面试对话记录
                    await this.loadInterviewRecords();
                    
                    // 加载AI生成的反馈
                    await this.loadAIFeedback();
                    return;
                }
            }
            
            // 如果API失败，尝试从本地JSON文件加载
            console.log('API加载失败，尝试从本地文件加载');
            const response = await fetch('data/real_data.json');
            const data = await response.json();
            
            this.candidateData = data.candidates.find(c => c.id == this.candidateId);
            
            if (!this.candidateData) {
                alert('候选人信息未找到');
                this.goBack();
                return;
            }

            // 从候选人数据中提取评分信息
            this.extractScoresFromCandidate();

            this.renderCandidateInfo();
            this.renderEvaluation();
            
            // 尝试从后端加载更详细的评分数据
            await this.loadEvaluationFromAPI();
            
            // 加载面试对话记录
            await this.loadInterviewRecords();
            
            // 加载AI生成的反馈
            await this.loadAIFeedback();
            
        } catch (error) {
            console.error('加载候选人数据失败:', error);
            this.loadMockData();
        }
    }

    async loadAIFeedback(regenerate = false) {
        console.log('开始加载AI反馈', regenerate ? '(重新生成)' : '(使用缓存)');
        try {
            const url = `http://localhost:8000/api/candidates/${this.candidateId}/ai-feedback${regenerate ? '?regenerate=true' : ''}`;
            console.log('请求URL:', url);
            
            const response = await fetch(url);
            console.log('响应状态:', response.status);
            
            if (response.ok) {
                const feedback = await response.json();
                console.log('AI反馈数据:', feedback);
                this.renderFeedback(feedback);
            } else {
                const error = await response.text();
                console.error('加载AI反馈失败:', response.status, error);
                this.renderFeedbackError('加载失败，请稍后重试');
            }
        } catch (error) {
            console.error('加载AI反馈失败:', error);
            this.renderFeedbackError('网络错误，请检查连接');
        }
    }

    renderFeedbackError(message) {
        const strengthsList = document.getElementById('strengthsList');
        const improvementsList = document.getElementById('improvementsList');
        
        if (strengthsList) {
            strengthsList.innerHTML = `<li style="color: #dc3545;">${message}</li>`;
        }
        if (improvementsList) {
            improvementsList.innerHTML = `<li style="color: #dc3545;">${message}</li>`;
        }
    }

    renderFeedback(feedback) {
        console.log('开始渲染反馈');
        console.log('反馈数据:', feedback);
        
        // 渲染优势亮点
        const strengthsList = document.getElementById('strengthsList');
        console.log('找到strengthsList元素:', strengthsList);
        
        if (strengthsList) {
            if (feedback.strengths && feedback.strengths.length > 0) {
                console.log('渲染优势亮点:', feedback.strengths.length, '条');
                strengthsList.innerHTML = feedback.strengths.map(item => `<li>${item}</li>`).join('');
            } else {
                console.log('没有优势亮点数据');
                strengthsList.innerHTML = '<li>暂无数据</li>';
            }
        } else {
            console.error('未找到strengthsList元素');
        }

        // 渲染待改进项
        const improvementsList = document.getElementById('improvementsList');
        console.log('找到improvementsList元素:', improvementsList);
        
        if (improvementsList) {
            if (feedback.improvements && feedback.improvements.length > 0) {
                console.log('渲染待改进项:', feedback.improvements.length, '条');
                improvementsList.innerHTML = feedback.improvements.map(item => `<li>${item}</li>`).join('');
            } else {
                console.log('没有待改进项数据');
                improvementsList.innerHTML = '<li>暂无数据</li>';
            }
        } else {
            console.error('未找到improvementsList元素');
        }

        // 显示缓存信息
        if (feedback.cached && feedback.generated_at) {
            const feedbackInfo = document.getElementById('feedbackInfo');
            const generatedTime = document.getElementById('generatedTime');
            if (feedbackInfo && generatedTime) {
                generatedTime.textContent = new Date(feedback.generated_at).toLocaleString('zh-CN');
                feedbackInfo.style.display = 'block';
            }
        }
    }

    extractScoresFromCandidate() {
        // 从候选人数据中提取评分
        if (this.candidateData.knowledge_score !== null && this.candidateData.knowledge_score !== undefined) {
            this.evaluationData.knowledge = this.candidateData.knowledge_score;
        }
        if (this.candidateData.skill_score !== null && this.candidateData.skill_score !== undefined) {
            this.evaluationData.skill = this.candidateData.skill_score;
        }
        if (this.candidateData.ability_score !== null && this.candidateData.ability_score !== undefined) {
            this.evaluationData.ability = this.candidateData.ability_score;
        }
        if (this.candidateData.personality_score !== null && this.candidateData.personality_score !== undefined) {
            this.evaluationData.personality = this.candidateData.personality_score;
        }
        if (this.candidateData.motivation_score !== null && this.candidateData.motivation_score !== undefined) {
            this.evaluationData.motivation = this.candidateData.motivation_score;
        }
        if (this.candidateData.value_score !== null && this.candidateData.value_score !== undefined) {
            this.evaluationData.value = this.candidateData.value_score;
        }
    }

    async loadEvaluationFromAPI() {
        try {
            const response = await fetch(`http://localhost:8000/api/candidates/${this.candidateId}/evaluation`);
            
            if (response.ok) {
                const evaluation = await response.json();
                console.log('从API加载的评分数据:', evaluation);
                
                // 更新评分数据
                if (evaluation.knowledge) this.evaluationData.knowledge = evaluation.knowledge;
                if (evaluation.skill) this.evaluationData.skill = evaluation.skill;
                if (evaluation.ability) this.evaluationData.ability = evaluation.ability;
                if (evaluation.personality) this.evaluationData.personality = evaluation.personality;
                if (evaluation.motivation) this.evaluationData.motivation = evaluation.motivation;
                if (evaluation.value) this.evaluationData.value = evaluation.value;
                
                // 重新渲染评分
                this.renderEvaluation();
            } else {
                console.log('该候选人暂无详细评分数据，使用基础数据');
            }
        } catch (error) {
            console.error('加载评分数据失败:', error);
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
                
                // 从面试记录中计算评分
                this.calculateScoresFromInterviews(data);
                
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

    calculateScoresFromInterviews(interviewData) {
        console.log('开始计算面试评分');
        
        if (!interviewData.sessions || interviewData.sessions.length === 0) {
            console.log('没有面试会话数据');
            return;
        }

        // 维度映射
        const dimensionMap = {
            'Knowledge': 'knowledge',
            'Skill': 'skill',
            'Ability': 'ability',
            'Personality': 'personality',
            'Motivation': 'motivation',
            'Value': 'value'
        };

        // 收集所有维度的分数
        const allDimensionScores = {
            knowledge: [],
            skill: [],
            ability: [],
            personality: [],
            motivation: [],
            value: []
        };

        // 遍历所有会话，收集分数
        interviewData.sessions.forEach(session => {
            if (session.qa_pairs && session.qa_pairs.length > 0) {
                session.qa_pairs.forEach(qa => {
                    const dimensionKey = dimensionMap[qa.dimension];
                    if (dimensionKey && qa.score !== null && qa.score !== undefined) {
                        allDimensionScores[dimensionKey].push(qa.score);
                    }
                });
            }
        });

        // 计算每个维度的平均分
        let hasScores = false;
        Object.keys(allDimensionScores).forEach(dimension => {
            const scores = allDimensionScores[dimension];
            if (scores.length > 0) {
                // 计算平均分
                const avgScore = scores.reduce((sum, score) => sum + score, 0) / scores.length;
                this.evaluationData[dimension] = Math.round(avgScore);
                hasScores = true;
                console.log(`${dimension}: ${scores.join(', ')} → 平均: ${avgScore.toFixed(1)}`);
            } else {
                // 没有分数的维度保持为null
                console.log(`${dimension}: 无评分数据`);
            }
        });

        // 如果有新的评分数据，重新渲染
        if (hasScores) {
            console.log('更新评分显示');
            this.renderEvaluation();
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
        
        // 加载AI生成的反馈
        await this.loadAIFeedback();
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
        
        let allScores = [];
        
        dimensions.forEach(dimension => {
            const score = this.evaluationData[dimension];
            const scoreElement = document.getElementById(`${dimension}Score`);
            const progressElement = document.getElementById(`${dimension}Progress`);
            
            if (score !== null && score !== undefined && !isNaN(score) && score > 0) {
                // 有有效分数
                scoreElement.textContent = `${Math.round(score)} 分`;
                progressElement.style.width = `${score}%`;
                allScores.push(score);
            } else {
                // 没有分数，算0分
                scoreElement.textContent = '0 分';
                scoreElement.style.color = '#999';
                progressElement.style.width = '0%';
                allScores.push(0);
            }
        });

        // 计算总分（所有6个维度的平均分，包括0分）
        const totalScore = Math.round(
            allScores.reduce((sum, score) => sum + score, 0) / 6
        );
        
        const totalScoreElement = document.getElementById('totalScore');
        totalScoreElement.textContent = `${totalScore} 分`;

        // 更新评估摘要
        this.updateEvaluationSummary(totalScore, allScores);
    }

    updateEvaluationSummary(totalScore, allScores) {
        const summaryElement = document.getElementById('evaluationSummary');
        
        // 检查是否所有分数都是0
        const hasAnyScore = allScores.some(score => score > 0);
        
        if (!hasAnyScore) {
            summaryElement.textContent = '该候选人尚未完成AI面试评估。';
            return;
        }

        let summary = '';
        const dimensionNames = {
            knowledge: '专业知识',
            skill: '专业技能',
            ability: '综合能力',
            personality: '个性特质',
            motivation: '求职动机',
            value: '价值观'
        };

        // 找出得分最高和最低的维度（排除0分）
        let highestDim = null;
        let lowestDim = null;
        let highestScore = -1;
        let lowestScore = 101;

        Object.keys(this.evaluationData).forEach(dim => {
            const score = this.evaluationData[dim];
            if (score !== null && score !== undefined && !isNaN(score) && score > 0) {
                if (score > highestScore) {
                    highestScore = score;
                    highestDim = dim;
                }
                if (score < lowestScore) {
                    lowestScore = score;
                    lowestDim = dim;
                }
            }
        });

        // 统计未回答的维度数量
        const unansweredCount = allScores.filter(score => score === 0).length;

        // 根据总分生成评价
        if (totalScore >= 80) {
            summary = `候选人表现优秀，综合得分${totalScore}分。`;
        } else if (totalScore >= 70) {
            summary = `候选人表现良好，综合得分${totalScore}分。`;
        } else if (totalScore >= 60) {
            summary = `候选人表现中等，综合得分${totalScore}分。`;
        } else if (totalScore >= 40) {
            summary = `候选人表现一般，综合得分${totalScore}分。`;
        } else {
            summary = `候选人表现有待提升，综合得分${totalScore}分。`;
        }

        // 添加优势和改进建议
        if (highestDim) {
            summary += `在${dimensionNames[highestDim]}方面表现突出（${highestScore}分）`;
        }
        
        if (unansweredCount > 0) {
            summary += `，但有${unansweredCount}个维度未回答（计0分）`;
        } else if (lowestDim && lowestScore < 60) {
            summary += `，${dimensionNames[lowestDim]}方面需要加强（${lowestScore}分）`;
        }
        
        summary += '。';

        summaryElement.textContent = summary;
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
        window.regenerateFeedback = () => this.regenerateFeedback();
    }

    async regenerateFeedback() {
        if (!confirm('确定要重新生成AI反馈吗？这将覆盖现有内容。')) {
            return;
        }

        // 显示加载状态
        const strengthsList = document.getElementById('strengthsList');
        const improvementsList = document.getElementById('improvementsList');
        if (strengthsList) strengthsList.innerHTML = '<li class="loading-item">正在重新生成...</li>';
        if (improvementsList) improvementsList.innerHTML = '<li class="loading-item">正在重新生成...</li>';

        // 重新加载（强制生成）
        await this.loadAIFeedback(true);
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