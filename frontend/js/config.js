// API配置文件 - 统一管理前后端接口地址
// 部署时只需要修改这个文件中的地址即可

// 获取当前环境的API基础地址
function getApiBaseUrl() {
    // 如果是本地开发环境
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://localhost:8000';
    }
    
    // 如果是生产环境，使用相对路径或者当前域名
    // 方案1: 使用相对路径（推荐）
    return '';  // 空字符串表示使用相对路径，如 '/api/candidates'
    
    // 方案2: 使用当前域名的8000端口
    // return `${window.location.protocol}//${window.location.hostname}:8000`;
    
    // 方案3: 使用完全自定义的域名
    // return 'https://your-api-domain.com';
}

// API配置
const API_CONFIG = {
    BASE_URL: getApiBaseUrl(),
    
    // API端点
    ENDPOINTS: {
        // 认证相关
        AUTH: {
            LOGIN: '/api/auth/login',
            REGISTER: '/api/auth/register'
        },
        
        // 候选人相关
        CANDIDATES: {
            LIST: '/api/candidates',
            CREATE: '/api/candidates',
            DETAIL: (id) => `/api/candidates/${id}`,
            STATUS: (id) => `/api/candidates/${id}/status`,
            QUESTIONS: (id) => `/api/candidates/${id}/questions`,
            GENERATE_QUESTIONS: (id) => `/api/candidates/${id}/generate-questions`,
            AI_FEEDBACK: (id) => `/api/candidates/${id}/ai-feedback`,
            EVALUATION: (id) => `/api/candidates/${id}/evaluation`,
            INTERVIEW_RECORDS: (id) => `/api/candidates/${id}/interview-records`,
            FINALIZE_SCORES: (name) => `/api/candidates/${name}/finalize-scores`,
            PARSE_RESUME: '/api/candidates/parse-resume',
            TOP: '/api/candidates/top',
            RECENT: '/api/candidates/recent'
        },
        
        // 面试相关
        INTERVIEW: {
            START: '/api/interview/start',
            GENERATE_QUESTIONS: '/api/interview/generate-questions',
            ANSWER: (sessionId) => `/api/interview/${sessionId}/answer`
        },
        
        // 仪表板相关
        DASHBOARD: {
            STATS: '/api/dashboard/stats'
        },
        
        // 职位相关
        JOBS: '/api/jobs',
        
        // 简历相关
        RESUME: (folder, filename) => `/api/resume/${encodeURIComponent(folder)}/${encodeURIComponent(filename)}`,
        
        // 邮件相关
        EMAIL: {
            SEND_INVITE: '/api/email/send-invite',
            SEND_REPORT: '/api/email/send-report',
            SEND_NOTIFICATION: '/api/email/send-notification'
        },
        
        // AI聊天
        AI_CHAT: '/api/ai-chat',
        
        // 报告生成
        GENERATE_REPORT: '/api/generate-report'
    }
};

// 构建完整的API URL
function buildApiUrl(endpoint) {
    if (API_CONFIG.BASE_URL) {
        return API_CONFIG.BASE_URL + endpoint;
    }
    return endpoint;  // 使用相对路径
}

// 导出配置（兼容不同的模块系统）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { API_CONFIG, buildApiUrl };
} else {
    window.API_CONFIG = API_CONFIG;
    window.buildApiUrl = buildApiUrl;
}

// 为了向后兼容，保留原有的API_BASE变量
window.API_BASE = buildApiUrl('/api');