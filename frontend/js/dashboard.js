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
        const response = await fetch('data/real_data.json');
        const data = await response.json();
        renderPositions(data.jobs);
    } catch (error) {
        console.error('加载岗位数据失败:', error);
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
        const response = await fetch('data/real_data.json');
        const data = await response.json();
        renderCandidates(data.candidates);
    } catch (error) {
        console.error('加载候选人数据失败:', error);
    }
}

// 渲染候选人列表
function renderCandidates(candidates) {
    const container = document.querySelector('.candidates-list');
    if (!container) return;
    
    container.innerHTML = candidates.map(candidate => {
        const statusClass = getStatusClass(candidate.status);
        const scoreDisplay = candidate.total_score ? `得分: ${candidate.total_score}` : '';
        
        return `
            <div class="candidate-card" data-status="${statusClass}">
                <div class="candidate-header">
                    <div class="candidate-info">
                        <h3>${candidate.name}</h3>
                        <div class="candidate-badges">
                            <span class="badge ${statusClass}">${candidate.status}</span>
                            ${candidate.total_score ? `<span class="badge score">${scoreDisplay}</span>` : ''}
                        </div>
                    </div>
                    <div class="candidate-actions">
                        <button class="action-btn view" onclick="viewCandidate(${candidate.id})">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
                            </svg>
                            查看详情
                        </button>
                        <button class="action-btn resume" onclick="viewResume('${candidate.resume_folder}', '${candidate.resume_file}')">
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
                        <span class="date">${candidate.interview_date || '未安排面试'}</span>
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
function loadAnalyticsData() {
    console.log('加载分析数据');
    // 这里可以从API加载真实数据
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
    
    try {
        const response = await fetch('data/real_data.json');
        const data = await response.json();
        const candidate = data.candidates.find(c => c.id === candidateId);
        
        if (!candidate) {
            alert('候选人信息未找到');
            return;
        }
        
        showCandidateDetailModal(candidate);
    } catch (error) {
        console.error('加载候选人详情失败:', error);
        alert('加载候选人详情失败');
    }
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
});