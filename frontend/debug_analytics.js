// 简单的调试脚本
console.log('Debug script loaded');

// 测试API调用
async function testAPI() {
    try {
        console.log('Testing API...');
        const response = await fetch('http://localhost:8000/api/dashboard/stats');
        console.log('Response status:', response.status);
        
        if (response.ok) {
            const data = await response.json();
            console.log('API Data:', data);
            
            // 测试DOM元素
            const container1 = document.querySelector('.candidates-ranking');
            const container2 = document.querySelector('.salary-ranking');
            console.log('Candidates container:', container1);
            console.log('Salary container:', container2);
            
            // 直接更新DOM
            if (container1) {
                container1.innerHTML = `
                    <div style="padding: 10px; background: #e3f2fd;">
                        <h4>测试数据 - 最佳候选人</h4>
                        ${data.best_candidates.map((item, index) => `
                            <div style="margin: 5px 0; padding: 5px; background: white;">
                                ${index + 1}. ${item.candidate.name} - ${item.candidate.position} 
                                (评分: ${item.candidate.score || '未评分'})
                            </div>
                        `).join('')}
                    </div>
                `;
            }
            
            if (container2) {
                container2.innerHTML = `
                    <div style="padding: 10px; background: #f3e5f5;">
                        <h4>测试数据 - 最低薪资候选人</h4>
                        ${data.lowest_salary_candidates.map((item, index) => `
                            <div style="margin: 5px 0; padding: 5px; background: white;">
                                ${index + 1}. ${item.candidate.name} - ${item.candidate.position} 
                                (薪资: ${item.candidate.expected_salary})
                            </div>
                        `).join('')}
                    </div>
                `;
            }
        }
    } catch (error) {
        console.error('Test failed:', error);
    }
}

// 等待页面加载完成后执行
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', testAPI);
} else {
    testAPI();
}