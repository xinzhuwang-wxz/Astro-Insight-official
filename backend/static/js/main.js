// 天体分析系统 - 分析工作台前端逻辑

let currentSection = 'overview';
let charts = {};
let currentTheme = 'light';
let currentChartPref = 'structure';
let currentDataView = 'overview';

const API_BASE = window.location.origin;

const sectionTitles = {
    overview: '首页总览',
    data: '数据概览',
    analysis: 'EDA分析',
    structure: '结构空间',
    compare: '方法对比',
    results: '结果解释'
};

document.addEventListener('DOMContentLoaded', function() {
    bindUIEvents();
    applyTheme(currentTheme);
    showSection('overview');
    loadSystemStatus();
    loadDataSummary();
});

function bindUIEvents() {
    document.querySelectorAll('[data-nav]').forEach(btn => {
        btn.addEventListener('click', () => showSection(btn.dataset.nav));
    });

    document.getElementById('startAnalysisBtn')?.addEventListener('click', startAnalysis);
    document.getElementById('loadOverviewBtn')?.addEventListener('click', loadDataSummary);
    document.getElementById('loadObjectsBtn')?.addEventListener('click', loadCelestialObjects);
    document.getElementById('loadClassificationsBtn')?.addEventListener('click', loadClassifications);
    document.getElementById('loadHistoryBtn')?.addEventListener('click', loadExecutionHistory);
    document.getElementById('refreshStatusBtn')?.addEventListener('click', checkSystemStatus);
    document.getElementById('themeToggle')?.addEventListener('click', () => {
        applyTheme(currentTheme === 'light' ? 'dark' : 'light');
    });

    document.querySelectorAll('[data-theme]').forEach(btn => {
        btn.addEventListener('click', () => applyTheme(btn.dataset.theme));
    });

    document.querySelectorAll('[data-chart-pref]').forEach(btn => {
        btn.addEventListener('click', () => {
            currentChartPref = btn.dataset.chartPref;
            updateChartPreferenceUI();
            updateRecommendation();
        });
    });
}

function applyTheme(theme) {
    currentTheme = theme;
    document.getElementById('appRoot')?.setAttribute('data-theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
    document.body.style.transition = 'background 220ms ease, color 220ms ease';
    updateThemeUI();
    updateChartColors();
}

function updateThemeUI() {
    document.querySelectorAll('[data-theme]').forEach(btn => {
        const active = btn.dataset.theme === currentTheme;
        btn.classList.toggle('primary-button', active);
        btn.classList.toggle('secondary-button', !active);
    });
}

function updateChartPreferenceUI() {
    document.querySelectorAll('[data-chart-pref]').forEach(btn => {
        const active = btn.dataset.chartPref === currentChartPref;
        btn.classList.toggle('primary-button', active);
        btn.classList.toggle('secondary-button', !active);
    });
}

function showNotification(title, message, type = 'info') {
    const notification = document.getElementById('notification');
    const icon = document.getElementById('notificationIcon');
    const titleEl = document.getElementById('notificationTitle');
    const messageEl = document.getElementById('notificationMessage');

    const config = {
        info: { icon: 'fas fa-info-circle', color: '#335cff' },
        success: { icon: 'fas fa-check-circle', color: '#0f766e' },
        warning: { icon: 'fas fa-exclamation-triangle', color: '#b45309' },
        error: { icon: 'fas fa-times-circle', color: '#dc2626' }
    };

    const typeConfig = config[type] || config.info;
    icon.className = `${typeConfig.icon}`;
    icon.style.color = typeConfig.color;
    titleEl.textContent = title;
    messageEl.textContent = message;

    notification.classList.remove('translate-x-full');
    notification.classList.add('translate-x-0');

    setTimeout(() => {
        notification.classList.remove('translate-x-0');
        notification.classList.add('translate-x-full');
    }, 2800);
}

function showSection(sectionName) {
    currentSection = sectionName;
    document.querySelectorAll('.section-view').forEach(section => {
        section.classList.add('hidden');
    });

    const targetSection = document.querySelector(`[data-section="${sectionName}"]`);
    if (targetSection) targetSection.classList.remove('hidden');

    document.querySelectorAll('[data-nav]').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.nav === sectionName);
    });

    if (sectionName === 'data') loadDataSummary();
    if (sectionName === 'analysis') loadStatistics();
    if (sectionName === 'structure') loadStatistics();
    if (sectionName === 'compare') updateRecommendation();
    if (sectionName === 'results') updateInsightPanel();
}

async function startAnalysis() {
    const query = document.getElementById('analysisQuery').value.trim();
    const userType = document.getElementById('userType').value;
    const analysisType = document.getElementById('analysisType').value;

    if (!query) {
        showNotification('错误', '请输入分析任务描述', 'error');
        return;
    }

    toggleLoading(true);
    try {
        const response = await axios.post(`${API_BASE}/api/analyze`, {
            query,
            user_type: userType,
            analysis_type: analysisType
        });

        if (response.data.success) {
            displayAnalysisResult(response.data.result);
            updateRecommendation(response.data.result);
            updateInsightPanel(response.data.result);
            showNotification('成功', '分析完成，已更新结果解释', 'success');
            showSection('results');
        } else {
            throw new Error(response.data.message || '分析失败');
        }
    } catch (error) {
        console.error('分析错误:', error);
        showNotification('错误', error.response?.data?.message || error.message || '分析失败', 'error');
    } finally {
        toggleLoading(false);
    }
}

function toggleLoading(show) {
    const btn = document.getElementById('startAnalysisBtn');
    if (!btn) return;
    btn.disabled = show;
    btn.innerHTML = show
        ? '<i class="fas fa-spinner fa-spin mr-2"></i>分析中...'
        : '<i class="fas fa-play mr-2"></i>开始分析';
}

function displayAnalysisResult(result) {
    const analysisResult = document.getElementById('analysisResult');
    if (!analysisResult) return;

    const confidence = typeof result.confidence === 'number' ? `${(result.confidence * 100).toFixed(1)}%` : 'N/A';
    const info = result.celestial_info || {};
    const code = result.generated_code || '# 暂无生成代码';

    analysisResult.innerHTML = `
        <div class="grid grid-cols-1 gap-4">
            <div class="rounded-3xl p-4" style="background: var(--accent-soft);">
                <div class="text-xs uppercase tracking-wider" style="color: var(--muted);">天体信息</div>
                <div class="mt-2 space-y-1">
                    <div><span class="font-medium">名称：</span>${info.name || '未知'}</div>
                    <div><span class="font-medium">类型：</span>${info.type || '未知'}</div>
                    <div><span class="font-medium">坐标：</span>${info.coordinates || '未知'}</div>
                    <div><span class="font-medium">描述：</span>${info.description || '无'}</div>
                </div>
            </div>
            <div class="rounded-3xl p-4" style="background: rgba(124,58,237,0.10);">
                <div class="text-xs uppercase tracking-wider" style="color: var(--muted);">分类结果</div>
                <div class="mt-2 space-y-1">
                    <div><span class="font-medium">分类：</span>${result.classification || '暂无'}</div>
                    <div><span class="font-medium">置信度：</span>${confidence}</div>
                    <div><span class="font-medium">分析类型：</span>${result.analysis_type || '未知'}</div>
                    <div><span class="font-medium">处理时间：</span>${result.processing_time ? `${result.processing_time} 秒` : 'N/A'}</div>
                </div>
            </div>
            <div class="rounded-3xl p-4 glass-strong">
                <div class="text-xs uppercase tracking-wider" style="color: var(--muted);">生成代码</div>
                <pre class="mt-2 text-xs whitespace-pre-wrap overflow-x-auto" style="color: var(--text);">${escapeHTML(code)}</pre>
            </div>
        </div>
    `;
}

function updateRecommendation(result = null) {
    const recommendation = document.getElementById('chartRecommendation');
    const tag = document.getElementById('recommendedChartTag');
    if (!recommendation || !tag) return;

    const task = result?.analysis_type || document.getElementById('analysisType')?.value || 'classification';
    let text = '';
    let label = '';

    if (task === 'structure') {
        text = '推荐使用结构图、降维散点图、平行坐标和方法对比图。重点回答：结构是否稳定、是否被投影方法放大或扭曲。';
        label = '推荐图表：结构图';
    } else if (task === 'spectroscopy') {
        text = '推荐使用分布图、相关性热力图和特征贡献图。重点回答：哪些谱线或特征最能区分不同类别。';
        label = '推荐图表：关系图';
    } else if (task === 'variability') {
        text = '推荐使用时序图、分组折线和异常点标记。重点回答：变化趋势是否周期性、是否存在异常波动。';
        label = '推荐图表：时序图';
    } else if (task === 'photometry') {
        text = '推荐使用分布图、箱线图和对比图。重点回答：亮度分布是否存在明显分层或离群值。';
        label = '推荐图表：分布图';
    } else {
        text = '推荐使用分类分布图、散点图矩阵和结构图。重点回答：类别是否分离、边界是否清晰、哪些变量更重要。';
        label = '推荐图表：结构图';
    }

    recommendation.textContent = text;
    tag.textContent = label;
}

function updateInsightPanel(result = null) {
    const panel = document.getElementById('insightPanel');
    if (!panel) return;

    const task = result?.analysis_type || document.getElementById('analysisType')?.value || 'classification';
    const pref = currentChartPref;
    let content = [];

    content.push(`<p><span class="font-semibold">当前任务：</span>${task}</p>`);
    content.push(`<p><span class="font-semibold">偏好图表：</span>${pref}</p>`);
    content.push('<p>解释重点：图表是否只是在展示结果，还是在帮助我们发现结构和生成问题意识。</p>');
    content.push('<p>方法意识：PCA、t-SNE、UMAP 等方法不只是算法选择，它们会改变“我们看到的结构”。</p>');
    content.push('<p>设计判断：每张图都应该对应一个分析问题，不做无意义装饰图。</p>');

    panel.innerHTML = content.join('');
}

async function checkSystemStatus() {
    try {
        const response = await axios.get(`${API_BASE}/api/status`);
        if (response.data.success) {
            const status = response.data.system_status;
            const uptime = Math.floor(response.data.uptime / 3600);
            document.getElementById('backendState').textContent = '在线';
            document.getElementById('sessionState').textContent = `${uptime} 小时`;
            document.getElementById('dbStatus').textContent = status.database;
            document.getElementById('graphStatus').textContent = status.analysis_graph;
            document.getElementById('systemUptime').textContent = `${uptime} 小时`;
            showNotification('系统状态', `数据库：${status.database} · 分析图：${status.analysis_graph}`, 'info');
        }
    } catch (error) {
        console.error('获取系统状态失败:', error);
        document.getElementById('backendState').textContent = '离线';
        showNotification('错误', '无法获取系统状态', 'error');
    }
}

async function loadSystemStatus() {
    await checkSystemStatus();
}

async function loadDataSummary() {
    try {
        const response = await axios.get(`${API_BASE}/api/data/statistics`);
        if (response.data.success) {
            const mvpStats = response.data.mvp_statistics || {};
            const legacyStats = response.data.statistics || {};

            const objects = mvpStats.dataset_records ?? legacyStats.total_objects ?? 0;
            const classifications = mvpStats.analysis_results ?? legacyStats.total_classifications ?? 0;
            const history = mvpStats.analysis_runs ?? legacyStats.total_executions ?? 0;

            document.getElementById('objectsCount').textContent = objects;
            document.getElementById('classificationsCount').textContent = classifications;
            document.getElementById('historyCount').textContent = history;
            document.getElementById('avgResponseTime').textContent = legacyStats.avg_response_time ? `${legacyStats.avg_response_time.toFixed(2)}s` : 'N/A';
            updateRecommendation();
        }
    } catch (error) {
        console.error('加载数据摘要失败:', error);
        document.getElementById('objectsCount').textContent = '0';
        document.getElementById('classificationsCount').textContent = '0';
        document.getElementById('historyCount').textContent = '0';
        document.getElementById('avgResponseTime').textContent = 'N/A';
    }
}

async function loadCelestialObjects() {
    try {
        const response = await axios.get(`${API_BASE}/api/mvp/overview?limit=50`);
        if (response.data.success) {
            currentDataView = 'objects';
            displayDataTable('MVP 数据记录', response.data.data?.records || [], [
                { key: 'record_id', label: '记录ID' },
                { key: 'dataset_id', label: '数据集ID' },
                { key: 'object_name', label: '对象名称' },
                { key: 'object_family', label: '对象类别' },
                { key: 'ingested_at', label: '导入时间' }
            ]);
            showSection('data');
        }
    } catch (error) {
        console.error('加载MVP数据记录失败:', error);
        showNotification('错误', '加载MVP数据记录失败', 'error');
    }
}

async function loadClassifications() {
    try {
        const response = await axios.get(`${API_BASE}/api/mvp/overview?limit=50`);
        if (response.data.success) {
            currentDataView = 'classifications';
            displayDataTable('MVP 分析结果', response.data.data?.analysis_results || [], [
                { key: 'result_id', label: '结果ID' },
                { key: 'run_id', label: '运行ID' },
                { key: 'result_type', label: '结果类型' },
                { key: 'summary_text', label: '摘要' },
                { key: 'created_at', label: '创建时间' }
            ]);
            showSection('data');
        }
    } catch (error) {
        console.error('加载MVP分析结果失败:', error);
        showNotification('错误', '加载MVP分析结果失败', 'error');
    }
}

async function loadExecutionHistory() {
    try {
        const response = await axios.get(`${API_BASE}/api/mvp/overview?limit=50`);
        if (response.data.success) {
            currentDataView = 'history';
            displayDataTable('MVP 分析运行', response.data.data?.analysis_runs || [], [
                { key: 'run_id', label: '运行ID' },
                { key: 'task_id', label: '任务ID' },
                { key: 'method_id', label: '方法ID' },
                { key: 'run_status', label: '运行状态' },
                { key: 'runtime_ms', label: '运行耗时(ms)' },
                { key: 'created_at', label: '创建时间' }
            ]);
            showSection('data');
        }
    } catch (error) {
        console.error('加载MVP分析运行失败:', error);
        showNotification('错误', '加载MVP分析运行失败', 'error');
    }
}

function displayDataTable(title, data, columns) {
    const tableContainer = document.getElementById('dataTable');
    if (!tableContainer) return;

    if (!data || data.length === 0) {
        tableContainer.innerHTML = `<p class="text-sm" style="color: var(--muted);">暂无${title}数据</p>`;
        return;
    }

    let tableHTML = `
        <div class="mb-4 flex items-center justify-between flex-wrap gap-2">
            <h4 class="text-lg font-semibold">${title}</h4>
            <span class="mini-badge rounded-full px-3 py-1 text-xs" style="color: var(--muted);">${data.length} 条记录</span>
        </div>
        <table class="min-w-full divide-y soft-line">
            <thead>
                <tr>
    `;

    columns.forEach(column => {
        tableHTML += `<th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style="color: var(--muted);">${column.label}</th>`;
    });

    tableHTML += `
                </tr>
            </thead>
            <tbody class="divide-y soft-line">
    `;

    data.forEach((row, index) => {
        tableHTML += `<tr class="${index % 2 === 0 ? '' : ''}">`;
        columns.forEach(column => {
            let value = row[column.key] ?? '-';
            if (column.key === 'confidence' && typeof value === 'number') value = `${(value * 100).toFixed(1)}%`;
            else if (column.key.includes('_at') && value !== '-') value = new Date(value).toLocaleString('zh-CN');
            else if (column.key === 'execution_time' && typeof value === 'number') value = `${value.toFixed(2)}s`;
            else if (column.key === 'memory_usage' && typeof value === 'number') value = `${(value / 1024 / 1024).toFixed(2)}MB`;
            tableHTML += `<td class="px-4 py-3 text-sm" style="color: var(--text);">${escapeHTML(String(value))}</td>`;
        });
        tableHTML += '</tr>';
    });

    tableHTML += `</tbody></table>`;
    tableContainer.innerHTML = tableHTML;
}

async function loadStatistics() {
    try {
        const response = await axios.get(`${API_BASE}/api/data/statistics`);
        if (response.data.success) {
            const stats = response.data.statistics || {};
            createAnalysisTypeChart(stats.analysis_type_distribution || {});
            createUserTypeChart(stats.user_type_distribution || {});
            createSuccessRateChart(stats.success_rate_trend || []);
            document.getElementById('avgResponseTime').textContent = stats.avg_response_time ? `${stats.avg_response_time.toFixed(2)}s` : 'N/A';
            updateRecommendation();
        }
    } catch (error) {
        console.error('加载统计数据失败:', error);
        showNotification('错误', '加载统计数据失败', 'error');
    }
}

function createAnalysisTypeChart(data) {
    const canvas = document.getElementById('analysisTypeChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (charts.analysisType) charts.analysisType.destroy();

    charts.analysisType = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: ['#335cff', '#7c3aed', '#0f766e', '#f59e0b', '#ef4444'],
                borderWidth: 0,
                hoverOffset: 8
            }]
        },
        options: baseChartOptions({
            plugins: { legend: { position: 'bottom', labels: { color: getTextColor() } } }
        })
    });
}

function createUserTypeChart(data) {
    const canvas = document.getElementById('userTypeChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (charts.userType) charts.userType.destroy();

    charts.userType = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data),
            datasets: [{
                label: '用户数量',
                data: Object.values(data),
                backgroundColor: 'rgba(51,92,255,0.75)',
                borderRadius: 12,
                borderSkipped: false
            }]
        },
        options: baseChartOptions({
            scales: {
                x: { ticks: { color: getTextColor() }, grid: { color: getGridColor() } },
                y: { beginAtZero: true, ticks: { color: getTextColor() }, grid: { color: getGridColor() } }
            },
            plugins: { legend: { display: false } }
        })
    });
}

function createSuccessRateChart(data) {
    const canvas = document.getElementById('successRateChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (charts.successRate) charts.successRate.destroy();

    charts.successRate = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(item => item.date || ''),
            datasets: [{
                label: '成功率 (%)',
                data: data.map(item => (item.success_rate || 0) * 100),
                borderColor: '#7c3aed',
                backgroundColor: 'rgba(124,58,237,0.12)',
                tension: 0.32,
                fill: true,
                pointRadius: 3,
                pointHoverRadius: 5
            }]
        },
        options: baseChartOptions({
            scales: {
                x: { ticks: { color: getTextColor() }, grid: { color: getGridColor() } },
                y: { beginAtZero: true, max: 100, ticks: { color: getTextColor() }, grid: { color: getGridColor() } }
            },
            plugins: { legend: { labels: { color: getTextColor() } } }
        })
    });
}

function baseChartOptions(extra = {}) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 700, easing: 'easeOutQuart' },
        ...extra
    };
}

function updateChartColors() {
    Object.values(charts).forEach(chart => {
        if (!chart) return;
        chart.options = baseChartOptions({
            scales: chart.options.scales,
            plugins: chart.options.plugins
        });
        chart.update();
    });
}

function getTextColor() {
    return getComputedStyle(document.documentElement).getPropertyValue('--text').trim() || '#101828';
}

function getGridColor() {
    return getComputedStyle(document.documentElement).getPropertyValue('--line').trim() || 'rgba(15,23,42,0.08)';
}

function escapeHTML(str) {
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

function formatDuration(seconds) {
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${(seconds % 60).toFixed(0)}s`;
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
}
