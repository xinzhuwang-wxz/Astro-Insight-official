// 天体分析系统 - 前端JavaScript

// 全局变量
let currentSection = 'analysis';
let charts = {};

// API基础URL
const API_BASE = window.location.origin;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    showSection('analysis');
    loadSystemStatus();
});

// 显示通知
function showNotification(title, message, type = 'info') {
    const notification = document.getElementById('notification');
    const icon = document.getElementById('notificationIcon');
    const titleEl = document.getElementById('notificationTitle');
    const messageEl = document.getElementById('notificationMessage');
    
    // 设置图标和颜色
    const config = {
        'info': { icon: 'fas fa-info-circle', color: 'blue' },
        'success': { icon: 'fas fa-check-circle', color: 'green' },
        'warning': { icon: 'fas fa-exclamation-triangle', color: 'yellow' },
        'error': { icon: 'fas fa-times-circle', color: 'red' }
    };
    
    const typeConfig = config[type] || config['info'];
    icon.className = typeConfig.icon + ` text-${typeConfig.color}-500`;
    notification.className = notification.className.replace(/border-\w+-500/, `border-${typeConfig.color}-500`);
    
    titleEl.textContent = title;
    messageEl.textContent = message;
    
    // 显示通知
    notification.classList.remove('translate-x-full');
    notification.classList.add('translate-x-0');
    
    // 3秒后自动隐藏
    setTimeout(() => {
        notification.classList.remove('translate-x-0');
        notification.classList.add('translate-x-full');
    }, 3000);
}

// 显示/隐藏加载状态
function toggleLoading(elementId, show) {
    const element = document.getElementById(elementId);
    if (show) {
        element.classList.add('active');
    } else {
        element.classList.remove('active');
    }
}

// 显示/隐藏结果容器
function toggleResult(elementId, show) {
    const element = document.getElementById(elementId);
    if (show) {
        element.classList.add('active');
    } else {
        element.classList.remove('active');
    }
}

// 切换界面
function showSection(sectionName) {
    // 隐藏所有界面
    document.querySelectorAll('.section').forEach(section => {
        section.classList.add('hidden');
    });
    
    // 显示指定界面
    const targetSection = document.getElementById(`${sectionName}-section`);
    if (targetSection) {
        targetSection.classList.remove('hidden');
        currentSection = sectionName;
        
        // 根据界面类型加载相应数据
        if (sectionName === 'statistics') {
            loadStatistics();
        } else if (sectionName === 'data') {
            loadDataSummary();
        }
    }
}

// 开始分析
async function startAnalysis() {
    const query = document.getElementById('analysisQuery').value.trim();
    const userType = document.getElementById('userType').value;
    const analysisType = document.getElementById('analysisType').value;
    
    if (!query) {
        showNotification('错误', '请输入分析查询内容', 'error');
        return;
    }
    
    // 显示加载状态
    toggleLoading('analysisLoading', true);
    toggleResult('analysisResult', false);
    
    try {
        const response = await axios.post(`${API_BASE}/api/analyze`, {
            query: query,
            user_type: userType,
            analysis_type: analysisType
        });
        
        if (response.data.success) {
            displayAnalysisResult(response.data.result);
            showNotification('成功', '分析完成', 'success');
        } else {
            throw new Error(response.data.message || '分析失败');
        }
    } catch (error) {
        console.error('分析错误:', error);
        showNotification('错误', error.response?.data?.message || error.message || '分析失败', 'error');
    } finally {
        toggleLoading('analysisLoading', false);
    }
}

// 显示分析结果
function displayAnalysisResult(result) {
    // 天体信息
    const celestialInfo = document.getElementById('celestialInfo');
    if (result.celestial_info) {
        const info = result.celestial_info;
        celestialInfo.innerHTML = `
            <div class="space-y-2">
                <div><strong>名称:</strong> ${info.name || '未知'}</div>
                <div><strong>类型:</strong> ${info.type || '未知'}</div>
                <div><strong>坐标:</strong> ${info.coordinates || '未知'}</div>
                <div><strong>描述:</strong> ${info.description || '无'}</div>
            </div>
        `;
    } else {
        celestialInfo.innerHTML = '<p class="text-gray-500">暂无天体信息</p>';
    }
    
    // 分类结果
    const classificationResult = document.getElementById('classificationResult');
    if (result.classification) {
        const confidence = result.confidence ? (result.confidence * 100).toFixed(1) : 'N/A';
        classificationResult.innerHTML = `
            <div class="space-y-2">
                <div><strong>分类:</strong> ${result.classification}</div>
                <div><strong>置信度:</strong> ${confidence}%</div>
                <div><strong>分析类型:</strong> ${result.analysis_type}</div>
                <div><strong>处理时间:</strong> ${result.processing_time || 'N/A'}秒</div>
            </div>
        `;
    } else {
        classificationResult.innerHTML = '<p class="text-gray-500">暂无分类结果</p>';
    }
    
    // 生成代码
    const generatedCode = document.getElementById('generatedCode');
    if (result.generated_code) {
        generatedCode.textContent = result.generated_code;
    } else {
        generatedCode.textContent = '# 暂无生成代码';
    }
    
    // 显示结果容器
    toggleResult('analysisResult', true);
}

// 检查系统状态
async function checkSystemStatus() {
    try {
        const response = await axios.get(`${API_BASE}/api/status`);
        
        if (response.data.success) {
            const status = response.data.system_status;
            const uptime = Math.floor(response.data.uptime / 3600); // 转换为小时
            
            showNotification('系统状态', 
                `数据库: ${status.database} | 分析图: ${status.analysis_graph} | 运行时间: ${uptime}小时`, 
                'info');
        }
    } catch (error) {
        console.error('获取系统状态失败:', error);
        showNotification('错误', '无法获取系统状态', 'error');
    }
}

// 加载系统状态
async function loadSystemStatus() {
    try {
        const response = await axios.get(`${API_BASE}/api/status`);
        
        if (response.data.success) {
            const status = response.data.system_status;
            const uptime = Math.floor(response.data.uptime / 3600);
            
            // 更新性能指标
            document.getElementById('systemUptime').textContent = `${uptime} 小时`;
            document.getElementById('dbStatus').textContent = status.database;
            document.getElementById('graphStatus').textContent = status.analysis_graph;
        }
    } catch (error) {
        console.error('加载系统状态失败:', error);
    }
}

// 加载数据摘要
async function loadDataSummary() {
    try {
        const response = await axios.get(`${API_BASE}/api/data/statistics`);
        
        if (response.data.success) {
            const stats = response.data.statistics;
            
            // 更新计数
            document.getElementById('objectsCount').textContent = stats.total_objects || 0;
            document.getElementById('classificationsCount').textContent = stats.total_classifications || 0;
            document.getElementById('historyCount').textContent = stats.total_executions || 0;
        }
    } catch (error) {
        console.error('加载数据摘要失败:', error);
        // 设置默认值
        document.getElementById('objectsCount').textContent = '0';
        document.getElementById('classificationsCount').textContent = '0';
        document.getElementById('historyCount').textContent = '0';
    }
}

// 加载天体对象
async function loadCelestialObjects() {
    try {
        const response = await axios.get(`${API_BASE}/api/data/objects?limit=50`);
        
        if (response.data.success) {
            displayDataTable('天体对象', response.data.data, [
                { key: 'name', label: '名称' },
                { key: 'object_type', label: '类型' },
                { key: 'coordinates', label: '坐标' },
                { key: 'magnitude', label: '星等' },
                { key: 'created_at', label: '创建时间' }
            ]);
        }
    } catch (error) {
        console.error('加载天体对象失败:', error);
        showNotification('错误', '加载天体对象失败', 'error');
    }
}

// 加载分类结果
async function loadClassifications() {
    try {
        const response = await axios.get(`${API_BASE}/api/data/classifications?limit=50`);
        
        if (response.data.success) {
            displayDataTable('分类结果', response.data.data, [
                { key: 'object_name', label: '天体名称' },
                { key: 'classification', label: '分类' },
                { key: 'confidence', label: '置信度' },
                { key: 'analysis_type', label: '分析类型' },
                { key: 'user_type', label: '用户类型' },
                { key: 'created_at', label: '创建时间' }
            ]);
        }
    } catch (error) {
        console.error('加载分类结果失败:', error);
        showNotification('错误', '加载分类结果失败', 'error');
    }
}

// 加载执行历史
async function loadExecutionHistory() {
    try {
        const response = await axios.get(`${API_BASE}/api/data/history?limit=50`);
        
        if (response.data.success) {
            displayDataTable('执行历史', response.data.data, [
                { key: 'request_id', label: '请求ID' },
                { key: 'code_type', label: '代码类型' },
                { key: 'execution_status', label: '执行状态' },
                { key: 'execution_time', label: '执行时间' },
                { key: 'memory_usage', label: '内存使用' },
                { key: 'created_at', label: '创建时间' }
            ]);
        }
    } catch (error) {
        console.error('加载执行历史失败:', error);
        showNotification('错误', '加载执行历史失败', 'error');
    }
}

// 显示数据表格
function displayDataTable(title, data, columns) {
    const tableContainer = document.getElementById('dataTable');
    
    if (!data || data.length === 0) {
        tableContainer.innerHTML = `<p class="text-gray-500 text-center py-8">暂无${title}数据</p>`;
        return;
    }
    
    let tableHTML = `
        <div class="mb-4">
            <h4 class="text-lg font-semibold text-gray-900">${title} (${data.length} 条记录)</h4>
        </div>
        <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
                <tr>
    `;
    
    // 表头
    columns.forEach(column => {
        tableHTML += `<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">${column.label}</th>`;
    });
    
    tableHTML += `
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
    `;
    
    // 表格数据
    data.forEach((row, index) => {
        tableHTML += `<tr class="${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}">`;
        
        columns.forEach(column => {
            let value = row[column.key] || '-';
            
            // 格式化特殊字段
            if (column.key === 'confidence' && typeof value === 'number') {
                value = (value * 100).toFixed(1) + '%';
            } else if (column.key.includes('_at') && value !== '-') {
                value = new Date(value).toLocaleString('zh-CN');
            } else if (column.key === 'execution_time' && typeof value === 'number') {
                value = value.toFixed(2) + 's';
            } else if (column.key === 'memory_usage' && typeof value === 'number') {
                value = (value / 1024 / 1024).toFixed(2) + 'MB';
            }
            
            tableHTML += `<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${value}</td>`;
        });
        
        tableHTML += '</tr>';
    });
    
    tableHTML += `
            </tbody>
        </table>
    `;
    
    tableContainer.innerHTML = tableHTML;
}

// 加载统计数据
async function loadStatistics() {
    try {
        const response = await axios.get(`${API_BASE}/api/data/statistics`);
        
        if (response.data.success) {
            const stats = response.data.statistics;
            
            // 创建图表
            createAnalysisTypeChart(stats.analysis_type_distribution || {});
            createUserTypeChart(stats.user_type_distribution || {});
            createSuccessRateChart(stats.success_rate_trend || []);
            
            // 更新性能指标
            document.getElementById('avgResponseTime').textContent = 
                stats.avg_response_time ? stats.avg_response_time.toFixed(2) + 's' : 'N/A';
        }
    } catch (error) {
        console.error('加载统计数据失败:', error);
        showNotification('错误', '加载统计数据失败', 'error');
    }
}

// 创建分析类型分布图
function createAnalysisTypeChart(data) {
    const ctx = document.getElementById('analysisTypeChart').getContext('2d');
    
    if (charts.analysisType) {
        charts.analysisType.destroy();
    }
    
    charts.analysisType = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: [
                    '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'
                ],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// 创建用户类型分布图
function createUserTypeChart(data) {
    const ctx = document.getElementById('userTypeChart').getContext('2d');
    
    if (charts.userType) {
        charts.userType.destroy();
    }
    
    charts.userType = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data),
            datasets: [{
                label: '用户数量',
                data: Object.values(data),
                backgroundColor: '#10B981',
                borderColor: '#059669',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// 创建成功率趋势图
function createSuccessRateChart(data) {
    const ctx = document.getElementById('successRateChart').getContext('2d');
    
    if (charts.successRate) {
        charts.successRate.destroy();
    }
    
    charts.successRate = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(item => item.date || ''),
            datasets: [{
                label: '成功率 (%)',
                data: data.map(item => item.success_rate * 100 || 0),
                borderColor: '#8B5CF6',
                backgroundColor: 'rgba(139, 92, 246, 0.1)',
                borderWidth: 2,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

// 工具函数：格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 工具函数：格式化时间
function formatDuration(seconds) {
    if (seconds < 60) return seconds.toFixed(1) + 's';
    if (seconds < 3600) return Math.floor(seconds / 60) + 'm ' + (seconds % 60).toFixed(0) + 's';
    return Math.floor(seconds / 3600) + 'h ' + Math.floor((seconds % 3600) / 60) + 'm';
}