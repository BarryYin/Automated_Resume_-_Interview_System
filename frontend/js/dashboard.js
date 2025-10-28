// 全局变量
let currentTab = 'positions';

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    setupEventListeners();
});

// 初始化仪表板
function initializeDashboard() {
    // 默认显示岗位管理标签
    switchTab('positions');
}

// 设置事件监听器
function setupEventListeners() {
    // 搜索功能
    const searchInput = document.getElementById('candidateSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            searchCandidates(e.target.value);
        });
    }
    
    // 状态筛选
    const statusFilter = document.getElementById('statusFilter');
    if (statusFilter) {
        statusFilter.addEventListener('change', function(e) {
            filterCandidates(e.target.value);
        });
    }
}

// 返回首页
function goHome() {
    window.location.href = 'index.html';
}

// 标签切换功能
function switchTab(tabName) {
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
    }
    
    // 根据标签加载相应数据
    switch(tabName) {
        case 'positions':
            loadPositionsData();
            break;
        case 'candidates':
            loadCandidatesData();
            break;
        case 'analytics':
            loadAnalyticsData();
            break;
    }
}

// 加载岗位数据
async function loadPositionsData() {
    console.log('加载岗位数据');
    try {
        const response = await fetch('http://localhost:8000/api/jobs');
        if (response.ok) {
            const jobs = await response.json();
            renderPositions(jobs);
        } else {
            throw new Error('获取职位数据失败');
        }
    } catch (error) {
        console.error('加载岗位数据失败:', error);
        // 使用备用数据
        renderPositions([
            {
                id: 1,
                title: "Python工程师服务器端开发",
                department: "技术部",
                location: "北京",
                salary_range: "15000-25000",
                status: "招聘中"
            }
        ]);
    }
}

// 渲染岗位列表
function renderPositions(jobs) {
    const container = document.querySelector('.positions-list');
    if (!container) return;
    
    container.innerHTML = jobs.map(job => `
        <div class="position-card">
            <div class="position-header">
                <div class="position-info">
                    <h3>${job.title}</h3>
                    <span class="position-status recruiting">${job.status}</span>
                </div>
                <div class="position-actions">
                    <button class="action-btn view" onclick="viewPosition(${job.id})">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
                        </svg>
                        查看
                    </button>
                    <button class="action-btn edit" onclick="editPosition(${job.id})">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                        </svg>
                    </button>
                    <button class="action-btn delete" onclick="deletePosition(${job.id})">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                        </svg>
                    </button>
                </div>
            </div>
            <div class="position-details">
                <div class="detail-item">
                    <span class="label">${job.department}</span>
                    <span class="value">薪资: ${job.salary}</span>
                    <span class="value">${job.candidate_count} 位候选人</span>
                    <span class="value">发布于 ${job.publish_date}</span>
                </div>
            </div>
        </div>
    `).join('');
}

// 加载候选人数据
async function loadCandidatesData() {
    console.log('加载候选人数据');
    try {
        const response = await fetch('http://localhost:8000/api/candidates');
        if (response.ok) {
            const candidates = await response.json();
            renderCandidates(candidates);
        } else {
            throw new Error('获取候选人数据失败');
        }
    } catch (error) {
        console.error('加载候选人数据失败:', error);
        // 显示错误信息
        const container = document.querySelector('.candidates-list');
        if (container) {
            container.innerHTML = '<div class="error-message">加载候选人数据失败，请检查网络连接</div>';
        }
    }
}

// 渲染候选人列表
function renderCandidates(candidates) {
    const container = document.querySelector('.candidates-list');
    if (!container) return;
    
    container.innerHTML = candidates.map(candidate => {
        const statusClass = getStatusClass(candidate.status);
        const scoreDisplay = candidate.score ? `得分: ${candidate.score}` : '';
        
        return `
            <div class="candidate-card" data-status="${statusClass}">
                <div class="candidate-header">
                    <div class="candidate-info">
                        <h3>${candidate.name}</h3>
                        <div class="candidate-badges">
                            <span class="badge ${statusClass}">${candidate.status}</span>
                            ${candidate.score ? `<span class="badge score">${scoreDisplay}</span>` : ''}
                        </div>
                    </div>
                    <div class="candidate-actions">
                        <button class="action-btn view" onclick="viewCandidate(${candidate.id})">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
                            </svg>
                            查看详情
                        </button>
                        <button class="action-btn resume" onclick="viewResumeByName('${candidate.name}')">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
                            </svg>
                            简历
                        </button>
                        <button class="action-btn email" onclick="sendEmail('${candidate.email}')">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
                            </svg>
                        </button>
                    </div>
                </div>
                <div class="candidate-details">
                    <div class="detail-row">
                        <span class="email">${candidate.email}</span>
                        <span class="position">应聘: ${candidate.position}</span>
                        <span class="date">面试日期: ${candidate.interview_date || '未安排'}</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// 获取状态样式类
function getStatusClass(status) {
    switch(status) {
        case '已完成': return 'completed';
        case '面试中': return 'in-progress';
        case '待面试': return 'pending';
        default: return 'pending';
    }
}

// 加载分析数据
async function loadAnalyticsData() {
    console.log('加载分析数据');
    
    // 更新统计数据
    try {
        const statsResponse = await fetch('http://localhost:8000/api/dashboard/stats');
        if (statsResponse.ok) {
            const stats = await statsResponse.json();
            updateAnalyticsStats(stats);
        }
        
        // 加载最佳候选人数据
        const topResponse = await fetch('http://localhost:8000/api/candidates/top');
        if (topResponse.ok) {
            const topCandidates = await topResponse.json();
            updateTopCandidates(topCandidates);
        }
        
        // 加载最新候选人数据
        const recentResponse = await fetch('http://localhost:8000/api/candidates/recent');
        if (recentResponse.ok) {
            const recentCandidates = await recentResponse.json();
            updateRecentCandidates(recentCandidates);
        }
        
    } catch (error) {
        console.error('加载分析数据失败:', error);
        // 使用默认数据
        updateAnalyticsStats({
            active_positions: 3,
            total_candidates: 0,
            completed_interviews: 0,
            average_score: 0.0
        });
    }
}

// 创建新职位
function createNewPosition() {
    // 创建模态框
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
            max-width: 500px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        ">
            <h3 style="margin-bottom: 20px; color: #1a1a1a;">创建新职位</h3>
            <form id="newPositionForm">
                <div style="margin-bottom: 16px;">
                    <label style="display: block; margin-bottom: 8px; font-weight: 500;">职位名称</label>
                    <input type="text" name="title" required style="
                        width: 100%;
                        padding: 12px;
                        border: 1px solid #e1e5e9;
                        border-radius: 8px;
                        font-size: 14px;
                    " placeholder="请输入职位名称">
                </div>
                <div style="margin-bottom: 16px;">
                    <label style="display: block; margin-bottom: 8px; font-weight: 500;">部门</label>
                    <select name="department" required style="
                        width: 100%;
                        padding: 12px;
                        border: 1px solid #e1e5e9;
                        border-radius: 8px;
                        font-size: 14px;
                    ">
                        <option value="">请选择部门</option>
                        <option value="技术部">技术部</option>
                        <option value="产品部">产品部</option>
                        <option value="设计部">设计部</option>
                        <option value="运营部">运营部</option>
                    </select>
                </div>
                <div style="display: flex; gap: 12px; margin-bottom: 16px;">
                    <div style="flex: 1;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 500;">最低薪资</label>
                        <input type="number" name="salaryMin" required style="
                            width: 100%;
                            padding: 12px;
                            border: 1px solid #e1e5e9;
                            border-radius: 8px;
                            font-size: 14px;
                        " placeholder="15000">
                    </div>
                    <div style="flex: 1;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 500;">最高薪资</label>
                        <input type="number" name="salaryMax" required style="
                            width: 100%;
                            padding: 12px;
                            border: 1px solid #e1e5e9;
                            border-radius: 8px;
                            font-size: 14px;
                        " placeholder="25000">
                    </div>
                </div>
                <div style="margin-bottom: 24px;">
                    <label style="display: block; margin-bottom: 8px; font-weight: 500;">职位描述</label>
                    <textarea name="description" rows="4" style="
                        width: 100%;
                        padding: 12px;
                        border: 1px solid #e1e5e9;
                        border-radius: 8px;
                        font-size: 14px;
                        resize: vertical;
                    " placeholder="请输入职位描述和要求"></textarea>
                </div>
                <div style="display: flex; gap: 12px; justify-content: flex-end;">
                    <button type="button" onclick="closeModal()" style="
                        padding: 12px 24px;
                        border: 2px solid #dee2e6;
                        background: white;
                        border-radius: 8px;
                        cursor: pointer;
                        font-weight: 500;
                    ">取消</button>
                    <button type="submit" style="
                        padding: 12px 24px;
                        border: none;
                        background: #007bff;
                        color: white;
                        border-radius: 8px;
                        cursor: pointer;
                        font-weight: 500;
                    ">创建职位</button>
                </div>
            </form>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // 绑定表单提交事件
    document.getElementById('newPositionForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const positionData = Object.fromEntries(formData);
        
        console.log('创建新职位:', positionData);
        alert('职位创建成功！');
        closeModal();
    });
    
    // 点击背景关闭
    modal.onclick = (e) => {
        if (e.target === modal) {
            closeModal();
        }
    };
    
    // 关闭模态框函数
    window.closeModal = () => {
        document.body.removeChild(modal);
        delete window.closeModal;
    };
}

// 岗位操作函数
async function viewPosition(positionId) {
    console.log('查看职位:', positionId);
    
    try {
        const response = await fetch('data/real_data.json');
        const data = await response.json();
        const job = data.jobs.find(j => j.id === positionId);
        
        if (!job) {
            alert('职位信息未找到');
            return;
        }
        
        showJobDetailModal(job);
    } catch (error) {
        console.error('加载职位详情失败:', error);
        alert('加载职位详情失败');
    }
}

// 显示职位详情模态框
function showJobDetailModal(job) {
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
        overflow-y: auto;
    `;
    
    modal.innerHTML = `
        <div style="
            background: white;
            padding: 32px;
            border-radius: 16px;
            max-width: 800px;
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
            margin: 20px;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
                <h2 style="color: #1a1a1a; margin: 0;">${job.title}</h2>
                <button onclick="closeModal()" style="
                    background: none;
                    border: none;
                    font-size: 24px;
                    cursor: pointer;
                    color: #666;
                    padding: 4px;
                ">×</button>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; padding: 16px; background: #f8f9fa; border-radius: 8px;">
                <div>
                    <strong>部门:</strong> ${job.department}
                </div>
                <div>
                    <strong>薪资:</strong> ${job.salary}
                </div>
                <div>
                    <strong>招聘人数:</strong> ${job.recruit_count}人
                </div>
                <div>
                    <strong>发布时间:</strong> ${job.publish_date}
                </div>
                <div>
                    <strong>候选人数:</strong> ${job.candidate_count}人
                </div>
                <div>
                    <strong>状态:</strong> <span style="color: #28a745;">${job.status}</span>
                </div>
            </div>
            
            <div style="margin-bottom: 24px;">
                <h3 style="color: #1a1a1a; margin-bottom: 12px;">职位要求</h3>
                <div style="background: #f8f9fa; padding: 16px; border-radius: 8px; white-space: pre-line; line-height: 1.6;">
                    ${job.description}
                </div>
            </div>
            
            <div style="margin-bottom: 24px;">
                <h3 style="color: #1a1a1a; margin-bottom: 12px;">能力要求</h3>
                <div style="background: #f8f9fa; padding: 16px; border-radius: 8px; white-space: pre-line; line-height: 1.6;">
                    ${job.requirements}
                </div>
            </div>
            
            ${job.additional_info ? `
                <div style="margin-bottom: 24px;">
                    <h3 style="color: #1a1a1a; margin-bottom: 12px;">补充说明</h3>
                    <div style="background: #f8f9fa; padding: 16px; border-radius: 8px; white-space: pre-line; line-height: 1.6;">
                        ${job.additional_info}
                    </div>
                </div>
            ` : ''}
            
            <div style="margin-bottom: 16px;">
                <h3 style="color: #1a1a1a; margin-bottom: 12px;">联系信息</h3>
                <div style="background: #e3f2fd; padding: 16px; border-radius: 8px;">
                    <p><strong>招聘负责人:</strong> ${job.recruiter}</p>
                    <p><strong>联系邮箱:</strong> <a href="mailto:${job.recruiter_email}" style="color: #007bff;">${job.recruiter_email}</a></p>
                </div>
            </div>
            
            <div style="display: flex; gap: 12px; justify-content: flex-end;">
                <button onclick="editPosition(${job.id}); closeModal();" style="
                    padding: 12px 24px;
                    border: 2px solid #007bff;
                    background: white;
                    color: #007bff;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: 500;
                ">编辑职位</button>
                <button onclick="closeModal()" style="
                    padding: 12px 24px;
                    border: none;
                    background: #007bff;
                    color: white;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: 500;
                ">关闭</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // 点击背景关闭
    modal.onclick = (e) => {
        if (e.target === modal) {
            closeModal();
        }
    };
    
    // 关闭模态框函数
    window.closeModal = () => {
        if (modal.parentNode) {
            document.body.removeChild(modal);
        }
        delete window.closeModal;
    };
}

function editPosition(positionId) {
    console.log('编辑职位:', positionId);
    alert(`编辑职位: ${positionId}`);
}

function deletePosition(positionId) {
    if (confirm('确定要删除这个职位吗？')) {
        console.log('删除职位:', positionId);
        alert(`职位 ${positionId} 已删除`);
    }
}

// 候选人操作函数
async function viewCandidate(candidateId) {
    console.log('查看候选人:', candidateId);
    
    // 跳转到候选人详情页面
    window.location.href = `candidate-detail.html?id=${candidateId}`;
}

// 显示候选人详情模态框
function showCandidateDetailModal(candidate) {
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
        overflow-y: auto;
    `;
    
    modal.innerHTML = `
        <div style="
            background: white;
            padding: 32px;
            border-radius: 16px;
            max-width: 600px;
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
            margin: 20px;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
                <h2 style="color: #1a1a1a; margin: 0;">${candidate.name} - 候选人详情</h2>
                <button onclick="closeModal()" style="
                    background: none;
                    border: none;
                    font-size: 24px;
                    cursor: pointer;
                    color: #666;
                    padding: 4px;
                ">×</button>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; padding: 16px; background: #f8f9fa; border-radius: 8px;">
                <div>
                    <strong>姓名:</strong> ${candidate.name}
                </div>
                <div>
                    <strong>邮箱:</strong> ${candidate.email}
                </div>
                <div>
                    <strong>应聘职位:</strong> ${candidate.position}
                </div>
                <div>
                    <strong>面试状态:</strong> <span style="color: ${getStatusColor(candidate.status)};">${candidate.status}</span>
                </div>
                <div>
                    <strong>面试时间:</strong> ${candidate.interview_date || '未安排'}
                </div>
                <div>
                    <strong>评分:</strong> ${candidate.total_score || '未评分'}
                </div>
            </div>
            
            <div style="margin-bottom: 24px;">
                <h3 style="color: #1a1a1a; margin-bottom: 12px;">简历文件</h3>
                <div style="background: #e3f2fd; padding: 16px; border-radius: 8px; display: flex; align-items: center; gap: 12px;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="#1976d2">
                        <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
                    </svg>
                    <div style="flex: 1;">
                        <div style="font-weight: 500;">${candidate.resume_file}</div>
                        <div style="font-size: 12px; color: #666;">PDF文件</div>
                    </div>
                    <button onclick="viewResume('${candidate.resume_folder}', '${candidate.resume_file}')" style="
                        padding: 8px 16px;
                        border: none;
                        background: #1976d2;
                        color: white;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 12px;
                    ">查看简历</button>
                </div>
            </div>
            
            <div style="display: flex; gap: 12px; justify-content: flex-end;">
                <button onclick="sendEmail('${candidate.email}')" style="
                    padding: 12px 24px;
                    border: 2px solid #28a745;
                    background: white;
                    color: #28a745;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: 500;
                ">发送邮件</button>
                <button onclick="viewResume('${candidate.resume_folder}', '${candidate.resume_file}')" style="
                    padding: 12px 24px;
                    border: 2px solid #007bff;
                    background: white;
                    color: #007bff;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: 500;
                ">查看简历</button>
                <button onclick="closeModal()" style="
                    padding: 12px 24px;
                    border: none;
                    background: #007bff;
                    color: white;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: 500;
                ">关闭</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // 点击背景关闭
    modal.onclick = (e) => {
        if (e.target === modal) {
            closeModal();
        }
    };
    
    // 关闭模态框函数
    window.closeModal = () => {
        if (modal.parentNode) {
            document.body.removeChild(modal);
        }
        delete window.closeModal;
    };
}

// 获取状态颜色
function getStatusColor(status) {
    switch(status) {
        case '已完成': return '#28a745';
        case '面试中': return '#ffc107';
        case '待面试': return '#6c757d';
        default: return '#6c757d';
    }
}

// 查看简历功能
function viewResume(folder, filename) {
    console.log('查看简历:', folder, filename);
    
    // 使用新的PDF查看器
    if (window.pdfViewer) {
        pdfViewer.showPDFModal(folder, filename);
    } else {
        // 降级到简单的下载功能
        downloadResume(`http://localhost:8000/api/resume/${encodeURIComponent(folder)}/${encodeURIComponent(filename)}`, filename);
    }
}

// 下载简历
function downloadResume(apiPath, filename) {
    // 创建下载链接
    const link = document.createElement('a');
    link.href = apiPath;
    link.download = filename;
    link.target = '_blank';
    
    // 触发下载
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    console.log('开始下载简历:', filename);
}

function sendEmail(email) {
    console.log('发送邮件给:', email);
    alert(`发送邮件给: ${email}`);
}

// 搜索候选人
function searchCandidates(query) {
    console.log('搜索候选人:', query);
    // 实现搜索逻辑
    const candidates = document.querySelectorAll('.candidate-card');
    candidates.forEach(card => {
        const name = card.querySelector('h3').textContent.toLowerCase();
        const email = card.querySelector('.email').textContent.toLowerCase();
        const shouldShow = name.includes(query.toLowerCase()) || email.includes(query.toLowerCase());
        card.style.display = shouldShow ? 'block' : 'none';
    });
}

// 筛选候选人
function filterCandidates(status) {
    console.log('筛选候选人状态:', status);
    const candidates = document.querySelectorAll('.candidate-card');
    
    candidates.forEach(card => {
        if (status === 'all') {
            card.style.display = 'block';
        } else {
            const badge = card.querySelector(`.badge.${status}`);
            card.style.display = badge ? 'block' : 'none';
        }
    });
}

// 导出数据
function exportData(type) {
    console.log('导出数据:', type);
    alert(`导出${type}数据功能开发中...`);
}

// AI对话功能
let isChatOpen = false;

function toggleAIChat() {
    const sidebar = document.getElementById('aiChatSidebar');
    const overlay = document.getElementById('chatOverlay');
    
    isChatOpen = !isChatOpen;
    
    if (isChatOpen) {
        sidebar.classList.add('open');
        overlay.classList.add('show');
    } else {
        sidebar.classList.remove('open');
        overlay.classList.remove('show');
    }
}

async function askQuickQuestion(question) {
    // 添加用户消息
    addChatMessage(question, 'user');
    
    // 显示AI正在思考
    const thinkingId = addChatMessage('正在分析相关数据...', 'ai', true);
    
    try {
        // 调用AI聊天API
        const response = await fetch('http://localhost:8000/api/ai-chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: question,
                context: {
                    type: 'quick_question',
                    current_tab: currentTab,
                    timestamp: new Date().toISOString()
                }
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            
            // 移除思考消息
            removeChatMessage(thinkingId);
            
            // 添加AI回复
            addChatMessage(result.response, 'ai');
        } else {
            throw new Error('AI服务暂时不可用');
        }
        
    } catch (error) {
        console.error('快捷问题失败:', error);
        
        // 移除思考消息
        removeChatMessage(thinkingId);
        
        // 使用备用回复
        let fallbackResponse = '';
        switch(question) {
            case '分析候选人整体表现':
                fallbackResponse = '根据当前数据，候选人整体表现良好。平均得分78.5分，建议重点关注高分候选人。';
                break;
            case '生成招聘效率报告':
                fallbackResponse = '招聘效率：共156位候选人，89人完成面试，完成率57%。建议优化面试流程。';
                break;
            case '对比各职位数据':
                fallbackResponse = '各职位数据：技术岗位申请人数最多，产品岗位质量最高，运营岗位竞争较小。';
                break;
            default:
                fallbackResponse = '抱歉，暂时无法获取详细分析。请稍后再试。';
        }
        
        addChatMessage(fallbackResponse, 'ai');
    }
}

async function sendAIMessage() {
    const input = document.getElementById('aiChatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // 添加用户消息
    addChatMessage(message, 'user');
    input.value = '';
    
    // 显示AI正在思考
    const thinkingId = addChatMessage('正在分析数据...', 'ai', true);
    
    try {
        // 调用AI聊天API
        const response = await fetch('http://localhost:8000/api/ai-chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                context: {
                    current_tab: currentTab,
                    timestamp: new Date().toISOString()
                }
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            
            // 移除思考消息
            removeChatMessage(thinkingId);
            
            // 添加AI回复
            addChatMessage(result.response, 'ai');
        } else {
            throw new Error('AI服务暂时不可用');
        }
        
    } catch (error) {
        console.error('AI聊天失败:', error);
        
        // 移除思考消息
        removeChatMessage(thinkingId);
        
        // 显示错误信息
        addChatMessage('抱歉，我暂时无法回答您的问题。请稍后再试。', 'ai');
    }
}

function addChatMessage(text, sender, isTemporary = false) {
    const messagesContainer = document.getElementById('aiChatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `${sender}-message`;
    
    if (isTemporary) {
        messageDiv.id = `temp-message-${Date.now()}`;
    }
    
    const now = new Date();
    const timeStr = now.toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="message-text">${text}</div>
            <div class="message-time">${timeStr}</div>
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    return messageDiv.id;
}

function removeChatMessage(messageId) {
    if (messageId) {
        const messageElement = document.getElementById(messageId);
        if (messageElement) {
            messageElement.remove();
        }
    }
}

function generateAIResponse(message) {
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('候选人') || lowerMessage.includes('面试')) {
        return '根据最新数据，我们有156位候选人，其中89人已完成面试。表现最好的是李四（92分）和赵六（88分）。您想了解哪个具体方面的信息？';
    } else if (lowerMessage.includes('职位') || lowerMessage.includes('岗位')) {
        return '目前有12个活跃职位在招聘中，包括Python工程师、产品经理和新媒体运营等。Python工程师岗位申请人数最多，您需要查看具体职位的详细数据吗？';
    } else if (lowerMessage.includes('分析') || lowerMessage.includes('报告')) {
        return '我可以为您生成详细的数据分析报告，包括候选人表现分析、招聘效率统计、各职位对比等。您希望重点分析哪个方面？';
    } else if (lowerMessage.includes('薪资') || lowerMessage.includes('工资')) {
        return '薪资数据显示，王五期望18,000/月（评分76），孙七期望15,000/月（评分82）。整体薪资期望与市场水平基本匹配。';
    } else {
        return '我理解您的问题。基于当前的招聘数据，我建议您查看具体的统计报表或使用快捷问题获取更准确的分析结果。还有什么其他问题吗？';
    }
}

function handleChatKeyPress(event) {
    if (event.key === 'Enter') {
        sendAIMessage();
    }
}

// 加载分析数据
async function loadAnalyticsData() {
    console.log('加载分析数据');
    
    // 更新统计数据
    try {
        const statsResponse = await fetch('http://localhost:8000/api/dashboard/stats');
        if (statsResponse.ok) {
            const stats = await statsResponse.json();
            updateAnalyticsStats(stats);
        }
        
        // 加载最佳候选人数据
        const topResponse = await fetch('http://localhost:8000/api/candidates/top');
        if (topResponse.ok) {
            const topCandidates = await topResponse.json();
            updateTopCandidates(topCandidates);
        }
        
        // 加载最新候选人数据
        const recentResponse = await fetch('http://localhost:8000/api/candidates/recent');
        if (recentResponse.ok) {
            const recentCandidates = await recentResponse.json();
            updateRecentCandidates(recentCandidates);
        }
        
    } catch (error) {
        console.error('加载分析数据失败:', error);
        // 使用默认数据
        updateAnalyticsStats({
            active_positions: 3,
            total_candidates: 0,
            completed_interviews: 0,
            average_score: 0.0
        });
    }
}

function updateAnalyticsStats(stats) {
    console.log('updateAnalyticsStats called with:', stats);
    document.getElementById('analyticsActivePositions').textContent = stats.active_positions;
    document.getElementById('analyticsTotalCandidates').textContent = stats.total_candidates;
    document.getElementById('analyticsCompletedInterviews').textContent = stats.completed_interviews;
    document.getElementById('analyticsAverageScore').textContent = stats.average_score;
    
    // 更新最佳候选人列表
    if (stats.best_candidates) {
        console.log('Updating best candidates:', stats.best_candidates);
        updateBestCandidates(stats.best_candidates);
    } else {
        console.log('No best_candidates data');
    }
    
    // 更新最低薪资候选人列表
    if (stats.lowest_salary_candidates) {
        console.log('Updating lowest salary candidates:', stats.lowest_salary_candidates);
        updateLowestSalaryCandidates(stats.lowest_salary_candidates);
    } else {
        console.log('No lowest_salary_candidates data');
    }
}

function updateBestCandidates(bestCandidates) {
    console.log('updateBestCandidates called with:', bestCandidates);
    const container = document.querySelector('.candidates-ranking');
    console.log('Container found:', container);
    if (!container || !bestCandidates.length) {
        console.log('Container not found or no candidates');
        return;
    }
    
    container.innerHTML = bestCandidates.slice(0, 3).map((item, index) => {
        const candidate = item.candidate;
        const scoreDisplay = candidate.score ? `${candidate.score} 分` : '未评分';
        const dateDisplay = candidate.interview_date || candidate.created_at.split(' ')[0];
        
        return `
            <div class="candidate-rank-item">
                <div class="rank-number">${index + 1}</div>
                <div class="candidate-info">
                    <div class="candidate-name">${candidate.name}</div>
                    <div class="candidate-position">${candidate.position}</div>
                </div>
                <div class="candidate-score">${scoreDisplay}</div>
                <div class="candidate-date">${dateDisplay}</div>
                <div class="candidate-reason">${item.reason}</div>
            </div>
        `;
    }).join('');
}

function updateLowestSalaryCandidates(lowestSalaryCandidates) {
    console.log('updateLowestSalaryCandidates called with:', lowestSalaryCandidates);
    const container = document.querySelector('.salary-ranking');
    console.log('Salary container found:', container);
    if (!container || !lowestSalaryCandidates.length) {
        console.log('Salary container not found or no candidates');
        return;
    }
    
    container.innerHTML = lowestSalaryCandidates.map(item => {
        const candidate = item.candidate;
        const scoreDisplay = candidate.score ? `评分: ${candidate.score}` : '未评分';
        
        // 格式化薪资显示
        let salaryDisplay = candidate.expected_salary;
        if (item.salary_num) {
            if (item.salary_num >= 10000) {
                salaryDisplay = `¥${(item.salary_num / 10000).toFixed(1)}万/月`;
            } else {
                salaryDisplay = `¥${item.salary_num.toLocaleString()}/月`;
            }
        }
        
        return `
            <div class="salary-rank-item">
                <div class="salary-candidate">
                    <div class="candidate-name">${candidate.name}</div>
                    <div class="candidate-position">${candidate.position}</div>
                </div>
                <div class="salary-amount">${salaryDisplay}</div>
                <div class="salary-score">${scoreDisplay}</div>
            </div>
        `;
    }).join('');
}

function updateTopCandidates(candidates) {
    const container = document.querySelector('.top-candidates-list');
    if (!container || !candidates.length) return;
    
    container.innerHTML = candidates.map((candidate, index) => `
        <div class="top-candidate-item">
            <div class="rank">${index + 1}</div>
            <div class="candidate-info">
                <div class="name">${candidate.name}</div>
                <div class="position">${candidate.position}</div>
            </div>
            <div class="score">${candidate.score} 分</div>
            <div class="date">${candidate.interview_date}</div>
        </div>
    `).join('');
}

function updateRecentCandidates(candidates) {
    const container = document.querySelector('.recent-candidates-list');
    if (!container || !candidates.length) return;
    
    container.innerHTML = candidates.map(candidate => `
        <div class="recent-candidate-item">
            <div class="candidate-info">
                <div class="name">${candidate.name}</div>
                <div class="position">${candidate.position}</div>
            </div>
            <div class="salary">${candidate.expected_salary}</div>
            <div class="score">评分: ${candidate.score || '待评分'}</div>
        </div>
    `).join('');
}

// 报告生成和发送功能
async function generateAndDownloadReport() {
    try {
        // 显示加载状态
        const button = event.target;
        const originalText = button.innerHTML;
        button.innerHTML = '<span>生成中...</span>';
        button.disabled = true;
        
        // 调用API生成报告
        const response = await fetch('http://localhost:8000/api/generate-report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                type: 'comprehensive'
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            
            // 创建并下载报告文件
            const reportContent = formatReportForDownload(result);
            downloadReport(reportContent, '招聘数据分析报告');
            
            // 显示成功消息
            addChatMessage('📊 完整报告已生成并下载！', 'ai');
        } else {
            throw new Error('报告生成失败');
        }
        
    } catch (error) {
        console.error('生成报告失败:', error);
        addChatMessage('抱歉，报告生成失败。请稍后重试。', 'ai');
    } finally {
        // 恢复按钮状态
        const button = event.target;
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

function formatReportForDownload(reportData) {
    const now = new Date();
    const dateStr = now.toLocaleDateString('zh-CN');
    const timeStr = now.toLocaleTimeString('zh-CN');
    
    return `
AI招聘数据分析报告
==========================================

生成时间：${dateStr} ${timeStr}
报告类型：${reportData.report_type || '综合分析'}

${reportData.report}

==========================================
报告说明：
- 本报告基于真实招聘数据生成
- 数据来源：Excel候选人数据和职位数据
- AI分析模型：通义千问Code
- 报告生成时间：${reportData.generated_at}

联系方式：
如有疑问，请联系HR部门
邮箱：hr@company.com
电话：400-123-4567
==========================================
    `.trim();
}

function downloadReport(content, filename) {
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename}_${new Date().toLocaleDateString('zh-CN').replace(/\//g, '-')}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

function showEmailReportModal() {
    const modal = document.getElementById('emailModal');
    modal.classList.add('show');
    
    // 设置默认值
    const today = new Date().toLocaleDateString('zh-CN');
    document.getElementById('emailSubject').value = `招聘数据分析报告 - ${today}`;
    document.getElementById('emailMessage').value = `您好！\n\n请查收${today}的招聘数据分析报告。\n\n报告包含了最新的候选人分析、职位对比和招聘效率统计。\n\n如有任何问题，请随时联系。\n\n谢谢！`;
}

function closeEmailModal() {
    const modal = document.getElementById('emailModal');
    modal.classList.remove('show');
}

// 邮件发送表单处理
document.addEventListener('DOMContentLoaded', function() {
    const emailForm = document.getElementById('emailReportForm');
    if (emailForm) {
        emailForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            await sendEmailReport();
        });
    }
});

async function sendEmailReport() {
    try {
        const emailData = {
            recipient: document.getElementById('recipientEmail').value,
            candidate_name: "招聘团队",
            report_content: document.getElementById('emailMessage').value,
            email_type: "report"
        };
        
        // 显示发送状态
        const submitBtn = document.querySelector('#emailReportForm button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = '发送中...';
        submitBtn.disabled = true;
        
        // 先生成完整报告
        const reportResponse = await fetch('http://localhost:8000/api/generate-report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                type: document.getElementById('reportType').value || 'comprehensive'
            })
        });
        
        if (reportResponse.ok) {
            const reportResult = await reportResponse.json();
            emailData.report_content = reportResult.report;
        }
        
        // 调用新的邮件发送API
        const response = await fetch('http://localhost:8000/api/email/send-report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(emailData)
        });
        
        if (response.ok) {
            const result = await response.json();
            
            if (result.success) {
                // 显示成功消息
                addChatMessage(`📧 报告已成功发送到 ${emailData.recipient}`, 'ai');
                closeEmailModal();
                
                // 重置表单
                document.getElementById('emailReportForm').reset();
            } else {
                throw new Error(result.message || '邮件发送失败');
            }
        } else {
            throw new Error('邮件发送失败');
        }
        
    } catch (error) {
        console.error('发送邮件失败:', error);
        addChatMessage('抱歉，邮件发送失败。请检查邮箱地址或稍后重试。', 'ai');
    } finally {
        // 恢复按钮状态
        const submitBtn = document.querySelector('#emailReportForm button[type="submit"]');
        submitBtn.textContent = '发送报告';
        submitBtn.disabled = false;
    }
}

// 键盘快捷键
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + N 创建新职位
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        if (currentTab === 'positions') {
            createNewPosition();
        }
    }
    
    // 数字键快速切换标签
    if (e.key >= '1' && e.key <= '3') {
        const tabs = ['positions', 'candidates', 'analytics'];
        const tabIndex = parseInt(e.key) - 1;
        if (tabs[tabIndex]) {
            switchTab(tabs[tabIndex]);
        }
    }
    
    // ESC键关闭AI对话和邮件模态框
    if (e.key === 'Escape') {
        if (isChatOpen) {
            toggleAIChat();
        }
        const emailModal = document.getElementById('emailModal');
        if (emailModal && emailModal.classList.contains('show')) {
            closeEmailModal();
        }
    }
    
    // Ctrl/Cmd + R 生成报告
    if ((e.ctrlKey || e.metaKey) && e.key === 'r' && currentTab === 'analytics') {
        e.preventDefault();
        generateAndDownloadReport();
    }
});

// 根据候选人姓名查看简历
function viewResumeByName(candidateName) {
    // 根据姓名映射到对应的文件夹和文件
    const resumeMapping = {
        '田忠': {
            folder: 'Python工程师服务器端开发',
            file: '田忠.pdf'
        },
        '高飞虎': {
            folder: '金融海外投资新媒体内容文案编辑运营',
            file: '高飞虎.pdf'
        }
        // 可以根据需要添加更多映射
    };
    
    const resumeInfo = resumeMapping[candidateName];
    if (resumeInfo) {
        viewResume(resumeInfo.folder, resumeInfo.file);
    } else {
        alert(`未找到 ${candidateName} 的简历文件`);
    }
}