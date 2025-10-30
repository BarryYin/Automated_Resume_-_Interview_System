// 全局变量
let uploadedFileData = null;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeUploadArea();
    initializeForm();
});

// 初始化上传区域
function initializeUploadArea() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    
    // 点击上传区域触发文件选择
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });
    
    // 文件选择事件
    fileInput.addEventListener('change', handleFileSelect);
    
    // 拖拽事件
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleFileDrop);
}

// 初始化表单
function initializeForm() {
    const form = document.getElementById('candidateForm');
    form.addEventListener('submit', handleFormSubmit);
}

// 触发文件输入
function triggerFileInput() {
    document.getElementById('fileInput').click();
}

// 处理文件选择
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        uploadFile(file);
    }
}

// 处理拖拽悬停
function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('dragover');
}

// 处理拖拽离开
function handleDragLeave(event) {
    event.currentTarget.classList.remove('dragover');
}

// 处理文件拖拽放下
function handleFileDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

// 上传并解析文件
async function uploadFile(file) {
    // 验证文件类型
    const allowedTypes = ['.pdf', '.docx', '.doc'];
    const fileExt = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(fileExt)) {
        showMessage('不支持的文件格式。请上传PDF或Word文档。', 'error');
        return;
    }
    
    // 验证文件大小 (10MB)
    if (file.size > 10 * 1024 * 1024) {
        showMessage('文件大小不能超过10MB。', 'error');
        return;
    }
    
    // 显示解析进度
    showParsingProgress(true);
    updateProgressMessage('正在上传文件...');
    
    try {
        // 创建FormData
        const formData = new FormData();
        formData.append('file', file);
        
        updateProgressMessage('正在解析简历内容...');
        
        // 调用后端API
        const response = await fetch('http://localhost:8000/api/candidates/parse-resume', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            updateProgressMessage('解析完成，正在填充表单...');
            
            // 填充表单
            fillFormWithData(result.data);
            
            // 保存文件数据
            uploadedFileData = result.data;
            
            setTimeout(() => {
                showParsingProgress(false);
                showMessage('简历解析成功！请确认信息是否正确。', 'success');
            }, 500);
            
        } else {
            throw new Error(result.message || '简历解析失败');
        }
        
    } catch (error) {
        console.error('文件上传失败:', error);
        showParsingProgress(false);
        showMessage(`解析失败: ${error.message}`, 'error');
    }
}

// 显示/隐藏解析进度
function showParsingProgress(show) {
    const progressElement = document.getElementById('parsingProgress');
    progressElement.style.display = show ? 'block' : 'none';
}

// 更新进度消息
function updateProgressMessage(message) {
    const messageElement = document.getElementById('progressMessage');
    if (messageElement) {
        messageElement.textContent = message;
    }
}

// 用解析的数据填充表单
function fillFormWithData(data) {
    const form = document.getElementById('candidateForm');
    
    // 填充各个字段
    const fieldMapping = {
        'name': 'name',
        'email': 'email',
        'phone': 'phone',
        'education': 'education',
        'experience': 'experience',
        'current_position': 'currentPosition',
        'expected_salary': 'expectedSalary',
        'skills': 'skills',
        'summary': 'summary'
    };
    
    Object.entries(fieldMapping).forEach(([dataKey, formFieldId]) => {
        const field = document.getElementById(formFieldId);
        if (field && data[dataKey]) {
            field.value = data[dataKey];
            
            // 添加高亮效果表示AI填充的字段
            field.classList.add('ai-filled');
            setTimeout(() => {
                field.classList.remove('ai-filled');
            }, 2000);
        }
    });
}

// 处理表单提交
async function handleFormSubmit(event) {
    event.preventDefault();
    
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    
    // 显示加载状态
    submitBtn.textContent = '保存中...';
    submitBtn.disabled = true;
    
    try {
        // 收集表单数据
        const formData = new FormData(event.target);
        const candidateData = Object.fromEntries(formData);
        
        // 验证必填字段
        if (!candidateData.name || !candidateData.email) {
            throw new Error('姓名和邮箱为必填字段');
        }
        
        // 调用后端API
        const response = await fetch('http://localhost:8000/api/candidates', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(candidateData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showMessage('候选人添加成功！', 'success');
            
            // 2秒后返回候选人列表
            setTimeout(() => {
                goBack();
            }, 2000);
            
        } else {
            throw new Error(result.message || '保存失败');
        }
        
    } catch (error) {
        console.error('保存候选人失败:', error);
        showMessage(`保存失败: ${error.message}`, 'error');
        
        // 恢复按钮状态
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
}

// 显示消息
function showMessage(message, type = 'info') {
    // 移除现有消息
    const existingMessage = document.querySelector('.message');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    // 创建新消息
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    messageDiv.textContent = message;
    
    // 插入到表单前面
    const formSection = document.querySelector('.form-section');
    formSection.insertBefore(messageDiv, formSection.firstChild);
    
    // 自动移除消息
    if (type === 'success') {
        setTimeout(() => {
            messageDiv.remove();
        }, 3000);
    }
}

// 返回上一页
function goBack() {
    // 检查是否有未保存的更改
    const form = document.getElementById('candidateForm');
    const formData = new FormData(form);
    let hasData = false;
    
    for (let [key, value] of formData.entries()) {
        if (value.trim()) {
            hasData = true;
            break;
        }
    }
    
    if (hasData) {
        if (confirm('您有未保存的更改，确定要离开吗？')) {
            window.location.href = 'dashboard.html';
        }
    } else {
        window.location.href = 'dashboard.html';
    }
}

// 添加AI填充字段的样式
const style = document.createElement('style');
style.textContent = `
    .ai-filled {
        background-color: #f0f9ff !important;
        border-color: #0ea5e9 !important;
        animation: aiHighlight 2s ease-out;
    }
    
    @keyframes aiHighlight {
        0% {
            background-color: #dbeafe;
            transform: scale(1.02);
        }
        100% {
            background-color: #f0f9ff;
            transform: scale(1);
        }
    }
    
    .message {
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 16px;
        font-weight: 500;
    }
    
    .success-message {
        background: #d1fae5;
        color: #065f46;
        border: 1px solid #a7f3d0;
    }
    
    .error-message {
        background: #fee2e2;
        color: #991b1b;
        border: 1px solid #fca5a5;
    }
`;
document.head.appendChild(style);