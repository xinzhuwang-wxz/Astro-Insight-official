const DATA_FILES = {
  dataset: [
    './data/ancient_visualization_dataset.json',
    '/frontend/data/ancient_visualization_dataset.json',
    '/data/ancient_visualization_dataset.json'
  ],
  constel: [
    './data/merged_Chinese_astronomy_data.json',
    '/frontend/data/merged_Chinese_astronomy_data.json',
    '/data/merged_Chinese_astronomy_data.json'
  ]
};

const FALLBACK_DATA = {
  constel: [
    { '编号': '1', '星官': '北极', '星数': '5+3', '中国星名': '北极一(太子)', '拜耳命名法': '小熊座γ', 'HIP': '75097', '视星等': '3.04~3.09' }
  ]
};

const state = {
  theme: 'dark',
  threshold: 10,
  layer: 'combined',
  stage: 'ancient',
  datasets: {},
  charts: {},
  dim: {
    algorithm: 'pca',
    colorField: 'teff',
    sizeField: 'mag',
    clusterEps: 0.38,
    clusterMinPts: 8,
    showClusters: true,
    showOutliers: true,
    payload: null,
    stats: {},
    variance: []
  },
  stellar: {
    viewMode: 'cmd',
    colorField: 'teff',
    sizeField: 'parallax_error',
    parallaxErrThreshold: 2.0,
    epochYears: 0,
    showOutliers: true,
    showTheory: true,
    payload: null,
    stats: {},
    selected: null,
    motionScale: 1.0,
    trajectorySteps: 20
  },
  selection: {
    point: null,
    region: null
  }
};

const backendState = { url: null };

const DIM_ALGO_NOTES = {
  pca: 'PCA 以线性主成分保留全局方差结构，适合先看整体分布。',
  tsne: 't-SNE 强调局部邻域结构，适合发现紧密簇和相似天体群。',
  umap: 'UMAP 在局部与全局之间更平衡，适合大样本快速探索。'
};


window.addEventListener('DOMContentLoaded', () => {
  bindControls();
  applyTheme(state.theme);
  loadAllData();
});

function bindControls() {
  document.getElementById('themeBtn').addEventListener('click', () => {
    applyTheme(state.theme === 'dark' ? 'light' : 'dark');
  });
  document.getElementById('reloadBtn').addEventListener('click', loadAllData);
  document.getElementById('magThreshold').addEventListener('input', e => {
    state.threshold = Number(e.target.value);
    document.getElementById('magThresholdLabel').textContent = `≤ ${state.threshold.toFixed(1)}`;
    renderVisuals();
  });
  document.getElementById('layerSelect').addEventListener('change', e => {
    state.layer = e.target.value;
    renderVisuals();
  });
  document.getElementById('detailBtn').addEventListener('click', openStage2);
  document.getElementById('stage2BackBtn').addEventListener('click', closeStage2);
  const openStellarBtn = document.getElementById('openStellarBtn');
  if (openStellarBtn) openStellarBtn.addEventListener('click', openStage3);
  const stage3BackBtn = document.getElementById('stage3BackBtn');
  if (stage3BackBtn) stage3BackBtn.addEventListener('click', closeStage3);

  document.getElementById('dimAlgorithm').addEventListener('change', e => {
    state.dim.algorithm = e.target.value;
    document.getElementById('algoNote').textContent = DIM_ALGO_NOTES[state.dim.algorithm];
    recomputeDimensionality();
  });
  document.getElementById('colorField').addEventListener('change', e => {
    state.dim.colorField = e.target.value;
    renderDimensionality();
  });
  document.getElementById('sizeField').addEventListener('change', e => {
    state.dim.sizeField = e.target.value;
    renderDimensionality();
  });
  document.getElementById('clusterEps').addEventListener('input', e => {
    state.dim.clusterEps = Number(e.target.value);
    document.getElementById('clusterEpsLabel').textContent = state.dim.clusterEps.toFixed(2);
  });
  document.getElementById('clusterMinPts').addEventListener('input', e => {
    state.dim.clusterMinPts = Number(e.target.value);
    document.getElementById('clusterMinLabel').textContent = String(state.dim.clusterMinPts);
  });
  document.getElementById('showClusters').addEventListener('change', e => {
    state.dim.showClusters = e.target.checked;
    renderDimensionality();
  });
  document.getElementById('showOutliers').addEventListener('change', e => {
    state.dim.showOutliers = e.target.checked;
    renderDimensionality();
  });
  document.getElementById('recomputeDimBtn').addEventListener('click', recomputeDimensionality);

  const stellarViewMode = document.getElementById('stellarViewMode');
  const stellarColorField = document.getElementById('stellarColorField');
  const stellarSizeField = document.getElementById('stellarSizeField');
  const stellarParallaxErrThreshold = document.getElementById('stellarParallaxErrThreshold');
  const stellarEpochSlider = document.getElementById('stellarEpochSlider');
  const stellarShowOutliers = document.getElementById('stellarShowOutliers');
  const stellarShowTheory = document.getElementById('stellarShowTheory');
  const stellarRecomputeBtn = document.getElementById('stellarRecomputeBtn');
  if (stellarViewMode) stellarViewMode.addEventListener('change', e => {
    state.stellar.viewMode = e.target.value;
    renderStellarAnalysis();
  });
  if (stellarColorField) stellarColorField.addEventListener('change', e => {
    state.stellar.colorField = e.target.value;
    renderStellarAnalysis();
  });
  if (stellarSizeField) stellarSizeField.addEventListener('change', e => {
    state.stellar.sizeField = e.target.value;
    renderStellarAnalysis();
  });
  if (stellarParallaxErrThreshold) stellarParallaxErrThreshold.addEventListener('input', e => {
    state.stellar.parallaxErrThreshold = Number(e.target.value);
    document.getElementById('stellarParallaxErrLabel').textContent = `${state.stellar.parallaxErrThreshold.toFixed(1)}σ`;
  });
  if (stellarEpochSlider) stellarEpochSlider.addEventListener('input', e => {
    state.stellar.epochYears = Number(e.target.value);
    document.getElementById('stellarEpochLabel').textContent = String(state.stellar.epochYears);
    renderStellarAnalysis();
  });
  if (stellarShowOutliers) stellarShowOutliers.addEventListener('change', e => {
    state.stellar.showOutliers = e.target.checked;
    renderStellarAnalysis();
  });
  if (stellarShowTheory) stellarShowTheory.addEventListener('change', e => {
    state.stellar.showTheory = e.target.checked;
    renderStellarAnalysis();
  });
  if (stellarRecomputeBtn) stellarRecomputeBtn.addEventListener('click', loadStellarAnalysis);

  document.getElementById('starMap').addEventListener('dblclick', () => {
    if (state.charts.starMap) state.charts.starMap.resetZoom();
  });
}

function applyTheme(theme) {
  state.theme = theme;
  document.documentElement.setAttribute('data-theme', theme);
  document.body.setAttribute('data-theme', theme);
  if (state.charts.starMap || state.charts.brightness || state.charts.dim || state.charts.cluster || state.charts.variance) {
    renderVisuals();
  }
}

function openStage2() {
  console.log('[DEBUG] openStage2: 页面跳转触发');
  state.stage = 'detail';
  
  const stage2Panel = document.getElementById('stage2Panel');
  const stage3Panel = document.getElementById('stage3Panel');
  const starMapPanel = document.querySelector('.star-map-panel');
  const mainSidebar = document.querySelector('.dashboard-sidebar');
  console.log('[DEBUG] openStage2: DOM 节点定位', { stage2Panel, stage3Panel, starMapPanel, mainSidebar });

  if (stage2Panel) {
    stage2Panel.classList.remove('hidden');
    stage2Panel.style.display = 'flex';
  }
  if (stage3Panel) {
    stage3Panel.classList.add('hidden');
    stage3Panel.style.display = 'none';
  }
  if (starMapPanel) starMapPanel.style.display = 'none';
  if (mainSidebar) mainSidebar.style.display = 'none';

  document.getElementById('detailBtn').textContent = '返回';
  recomputeDimensionality();
}

function openStage3() {
  state.stage = 'stellar';
  const stage2Panel = document.getElementById('stage2Panel');
  const stage3Panel = document.getElementById('stage3Panel');
  const starMapPanel = document.querySelector('.star-map-panel');
  const mainSidebar = document.querySelector('.dashboard-sidebar');
  if (stage2Panel) {
    stage2Panel.classList.add('hidden');
    stage2Panel.style.display = 'none';
  }
  if (stage3Panel) {
    stage3Panel.classList.remove('hidden');
    stage3Panel.style.display = 'flex';
  }
  if (starMapPanel) starMapPanel.style.display = 'none';
  if (mainSidebar) mainSidebar.style.display = 'none';
  loadStellarAnalysis();
}

function closeStage3() {
  state.stage = 'detail';
  const stage2Panel = document.getElementById('stage2Panel');
  const stage3Panel = document.getElementById('stage3Panel');
  if (stage3Panel) {
    stage3Panel.classList.add('hidden');
    stage3Panel.style.display = 'none';
  }
  if (stage2Panel) {
    stage2Panel.classList.remove('hidden');
    stage2Panel.style.display = 'flex';
  }
  const note = document.getElementById('stellarSelectionBadge');
  if (note) note.textContent = '未选择对象';
}

function closeStage2() {
  state.stage = 'ancient';
  const stage2Panel = document.getElementById('stage2Panel');
  const starMapPanel = document.querySelector('.star-map-panel');
  const stage3Panel = document.getElementById('stage3Panel');
  const mainSidebar = document.querySelector('.dashboard-sidebar');
  
  if (stage2Panel) {
    stage2Panel.classList.add('hidden');
    stage2Panel.style.display = 'none';
  }
  if (stage3Panel) {
    stage3Panel.classList.add('hidden');
    stage3Panel.style.display = 'none';
  }
  if (starMapPanel) starMapPanel.style.display = '';
  if (mainSidebar) mainSidebar.style.display = '';

  document.getElementById('detailBtn').textContent = '详情';
}


async function loadAllData() {
  const summaryCards = document.getElementById('summaryCards');
  summaryCards.innerHTML = '<div class="stat-card">正在连接后端…</div>';
  try {
    const dataset = await resolveAncientDataset();
    state.datasets = dataset;
    renderVisuals();
    await loadStellarAnalysis();
  } catch (error) {
    console.error('[DEBUG ERROR] loadAllData: 古代数据加载异常', error);
    state.datasets = cloneFallbackData();
    renderVisuals();
    await loadStellarAnalysis();
  }
}

async function resolveAncientDataset() {
  const dataset = await loadBackendDataset();
  if (dataset) return dataset;
  const constel = await loadStructuredData('constel');
  return {
    constel,
    catalog: constel,
    constellations: buildConstellationsFromChineseAstronomy(constel),
    constellation_points: []
  };
}

async function loadBackendDataset() {
  for (const candidate of DATA_FILES.dataset) {
    try {
      const response = await fetch(candidate, { cache: 'no-store' });
      if (!response.ok) continue;
      const data = await response.json();
      if (!data || typeof data !== 'object') continue;
      if (Array.isArray(data.constellations) || Array.isArray(data.catalog)) {
        backendState.url = candidate;
        return normalizeBackendDataset(data);
      }
    } catch (error) {}
  }
  return null;
}

function normalizeBackendDataset(data) {
  const catalog = Array.isArray(data.catalog) ? data.catalog : [];
  const constellations = Array.isArray(data.constellations) ? data.constellations : [];
  return {
    ...data,
    catalog,
    constellations,
    constel: catalog.length ? catalog : cloneRows(FALLBACK_DATA.constel)
  };
}

async function loadStructuredData(name) {
  const candidates = DATA_FILES[name] || [];
  for (const candidate of candidates) {
    try {
      const response = await fetch(candidate, { cache: 'no-store' });
      if (!response.ok) continue;
      const data = await response.json();
      if (Array.isArray(data)) return data;
    } catch (e) {}
  }
  return FALLBACK_DATA[name] ? cloneRows(FALLBACK_DATA[name]) : null;
}

function cloneRows(rows) { return rows.map(row => ({ ...row })); }
function cloneFallbackData() { return { constel: cloneRows(FALLBACK_DATA.constel) }; }

function buildConstellationsFromChineseAstronomy(rows) {
  const groups = new Map();
  const seen = new Map();
  rows.forEach((row, index) => {
    const name = String(row['星官'] ?? '').trim();
    const hip = String(row.HIP ?? row.hip ?? '').trim();
    if (!name || !hip) return;
    const ra = Number(row.RA ?? row.ra ?? row.ra_j2000 ?? row.ra_1054);
    const dec = Number(row.Dec ?? row.dec ?? row.dec_j2000 ?? row.dec_1054);
    if (!Number.isFinite(ra) || !Number.isFinite(dec)) return;
    const key = `${hip}:${ra.toFixed(8)}:${dec.toFixed(8)}`;
    if (!seen.has(name)) seen.set(name, new Set());
    if (seen.get(name).has(key)) return;
    seen.get(name).add(key);
    if (!groups.has(name)) groups.set(name, []);
    groups.get(name).push({ ra, dec, mag: Number(row.mag ?? row.Vmag ?? row['视星等'] ?? 6.0), hip, label: row['中国星名'] || `HIP ${hip}`, order: index });
  });
  return [...groups.entries()].map(([name, points]) => ({ name, points: points.sort((a, b) => a.order - b.order), style: { linewidth: 3, linestyle: '-' } })).filter(group => group.points.length >= 2);
}

function renderSummary() {
  const constellationGroups = state.datasets.constellations || [];
  const visibleCount = constellationGroups.reduce((sum, g) => sum + (g.points?.filter(p => Number(p.mag ?? 99) <= state.threshold).length || 0), 0);
  document.getElementById('summaryCards').innerHTML = `
    <div class="stat-card"><div class="stat-label">星官总数</div><div class="stat-value">${constellationGroups.length}</div></div>
    <div class="stat-card"><div class="stat-label">当前可见恒星</div><div class="stat-value">${visibleCount}</div></div>
  `;
}

function polarProject(ra, dec) {
  const r = 90 - dec;
  const rad = (ra * Math.PI) / 180;
  return { x: r * Math.cos(rad), y: r * Math.sin(rad) };
}

function renderLocalStarMap(payload) {
  const canvas = document.getElementById('stellarAuxChart');
  if (!canvas) return;

  // 销毁旧实例，防止内存泄漏和重叠绘制
  if (state.charts.stellarAux) {
    state.charts.stellarAux.destroy();
  }

  const rows = payload.selected_rows || [];
  const usable = rows.filter(r => Number.isFinite(r.ra) && Number.isFinite(r.dec));

  // 1. 计算点颜色：如果是当前选中星则高亮为红色；否则根据有效温度显示星色
  const colors = usable.map(r => {
    const isSelected = state.stellar.selected && String(state.stellar.selected.id) === String(r.id);
    if (isSelected) return '#f43f5e'; // 玫瑰红高亮选中星
    
    if (r.teff && Number.isFinite(r.teff)) {
      // 经验温度色彩映射（3000K 偏红，10000K+ 偏蓝）
      const t = Math.max(3000, Math.min(10000, r.teff));
      const hue = 240 - ((t - 3000) / 7000) * 240;
      return `hsla(${hue}, 85%, 65%, 0.75)`;
    }
    return 'rgba(251, 191, 36, 0.75)'; // 默认暖黄色星光
  });

  // 2. 根据视星等计算点半径：亮度越亮（星等越小）半径越大
  const radii = usable.map(r => {
    const isSelected = state.stellar.selected && String(state.stellar.selected.id) === String(r.id);
    const mag = r.g_mag ?? r.mag ?? 15;
    const baseRadius = getPointRadius(mag);
    return isSelected ? baseRadius + 4 : baseRadius; // 选中星半径加大
  });

  // 3. 构建局部天区星图实例
  state.charts.stellarAux = new Chart(canvas, {
    type: 'scatter',
    data: {
      datasets: [{
        label: '局部星野坐标 (FOV)',
        data: usable.map((r, idx) => ({
          x: r.ra,
          y: r.dec,
          row: r,
          color: colors[idx],
          radius: radii[idx]
        })),
        pointBackgroundColor: ctx => ctx.raw?.color,
        pointRadius: ctx => ctx.raw?.radius,
        pointBorderColor: ctx => {
          const isSelected = state.stellar.selected && String(state.stellar.selected.id) === String(ctx.raw?.row?.id);
          return isSelected ? '#ffffff' : 'rgba(255, 255, 255, 0.15)';
        },
        pointBorderWidth: ctx => {
          const isSelected = state.stellar.selected && String(state.stellar.selected.id) === String(ctx.raw?.row?.id);
          return isSelected ? 2 : 0.5;
        }
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      parsing: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => {
              const r = ctx.raw?.row || {};
              return [
                `恒星: ${r.name || '未命名'}`,
                `坐标: RA ${r.ra.toFixed(4)}°, Dec ${r.dec.toFixed(4)}°`,
                `视星等: ${r.g_mag ?? r.mag ?? 'N/A'}`
              ];
            }
          }
        }
      },
      scales: {
        x: {
          title: { display: true, text: '赤经 (Right Ascension, 度)', color: getTextColor() },
          ticks: { color: getTextColor() },
          grid: { color: getGridColor() },
          reverse: true // 天文学标准习惯：赤经自右向左递增
        },
        y: {
          title: { display: true, text: '赤纬 (Declination, 度)', color: getTextColor() },
          ticks: { color: getTextColor() },
          grid: { color: getGridColor() }
        }
      },
      onClick: (_, elements) => {
        if (!elements.length) return;
        const raw = state.charts.stellarAux.data.datasets[elements[0].datasetIndex].data[elements[0].index];
        if (raw?.row) {
          state.stellar.selected = raw.row;
          // 触发全局重绘，使主物理图、侧边栏信息和局部星野同步高亮
          renderStellarAnalysis();
        }
      }
    }
  });
}

function renderStarMap() {
  const constellationGroups = state.datasets.constellations || [];
  const lineDatasets = constellationGroups.map((group, groupIndex) => {
    const projectedPoints = (group.points || []).filter(p => p.mag <= state.threshold).map(p => {
      const coords = polarProject(p.ra, p.dec);
      let chineseName = '无';
      if (p.label && !p.label.startsWith('HIP')) {
        chineseName = p.label;
      } else if (state.datasets.constel) {
        const match = state.datasets.constel.find(row => String(row.HIP || row.hip) === String(p.hip));
        if (match && match['中国星名']) chineseName = match['中国星名'];
      }
      return { x: coords.x, y: coords.y, ra: p.ra ?? 0, dec: p.dec ?? 0, mag: p.mag ?? 6.0, label: `${group.name} - ${chineseName}`, hip: p.hip || '无', chineseName };
    });
    const groupColor = pickGroupColor(groupIndex);
    const pointColor = getPointFillColor();
    const lineAlpha = state.layer === 'ancient' ? 0 : 0.3;
    return {
      label: group.name,
      data: projectedPoints,
      showLine: state.layer !== 'ancient',
      borderColor: rgbaFromHex(groupColor, lineAlpha),
      borderWidth: lineAlpha === 0 ? 0 : 1.2,
      fill: false,
      tension: 0.1,
      pointRadius: ctx => getPointRadius(ctx.raw?.mag),
      pointBackgroundColor: pointColor,
      pointBorderColor: pointColor,
      pointBorderWidth: 0,
      pointHoverRadius: ctx => getPointRadius(ctx.raw?.mag),
      order: 10
    };
  });

  const referenceGrids = [];
  [60, 30, 0, -30, -60].forEach(dec => {
    const circlePoints = [];
    for (let ra = 0; ra <= 360; ra += 4) circlePoints.push(polarProject(ra, dec));
    referenceGrids.push({ label: `Dec ${dec}°`, data: circlePoints, showLine: true, borderColor: 'rgba(255,255,255,0.08)', borderWidth: 1, borderDash: [5, 5], pointRadius: 0, fill: false, order: 1 });
  });

  const datasets = [...referenceGrids, ...lineDatasets];
  if (state.charts.starMap) state.charts.starMap.destroy();
  state.charts.starMap = new Chart(document.getElementById('starMap'), {
    type: 'scatter',
    data: { datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      onClick: (_, elements) => {
        if (!elements.length) return;
        const ds = state.charts.starMap.data.datasets[elements[0].datasetIndex];
        const item = ds.data[elements[0].index];
        if (!item || item.ra === undefined) return;
        document.getElementById('starInfo').innerHTML = `<strong>${item.label || ds.label}</strong><br>原始坐标 (RA/Dec)：(${item.ra.toFixed(2)}°, ${item.dec.toFixed(2)}°)<br>平面投影 (X/Y)：(${item.x.toFixed(1)}, ${item.y.toFixed(1)})<br>视星等：${item.mag ?? 'N/A'}<br>HIP编号：${item.hip ?? 'N/A'}`;
      },
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => { const raw = ctx.raw || {}; if (raw.ra === undefined) return ctx.dataset.label || ''; const raStr = typeof raw.ra === 'number' ? raw.ra.toFixed(1) : '无'; const decStr = typeof raw.dec === 'number' ? raw.dec.toFixed(1) : '无'; const magStr = typeof raw.mag === 'number' ? raw.mag.toFixed(1) : '无'; const hipStr = raw.hip || '无'; const chineseNameStr = raw.chineseName || '无'; const groupName = ctx.dataset.label || '未分类星官'; return [`星官: ${groupName}`, `中国星名: ${chineseNameStr}`, `HIP 编号: ${hipStr}`, `坐标: RA ${raStr}°, Dec ${decStr}°`, `视星等: ${magStr}`]; } } },
        zoom: { pan: { enabled: true, mode: 'xy', modifierKey: null }, zoom: { wheel: { enabled: true, speed: 0.1 }, pinch: { enabled: true }, mode: 'xy' } }
      },
      scales: { x: { type: 'linear', display: false, min: -150, max: 150 }, y: { type: 'linear', display: false, min: -150, max: 150 } }
    }
  });
  document.getElementById('mapBadge').textContent = backendState.url ? '后端数据已连接' : '北天投影活跃中';
}

function renderBrightnessChart() {
  const constellationGroups = state.datasets.constellations || [];
  const activeStars = constellationGroups.flatMap(group => (group.points || []).filter(p => Number(p.mag ?? 99) <= state.threshold));
  const bins = [
    { label: '< 4', min: -Infinity, max: 4 },
    { label: '4 - 6', min: 4, max: 6 },
    { label: '6 - 8', min: 6, max: 8 },
    { label: '> 8', min: 8, max: Infinity }
  ];
  const countBy = () => bins.map(bin => activeStars.filter(r => { const mag = Number(r.mag ?? 99); return mag > bin.min && mag <= bin.max; }).length);
  if (state.charts.brightness) state.charts.brightness.destroy();
  state.charts.brightness = new Chart(document.getElementById('brightnessChart'), { type: 'bar', data: { labels: bins.map(b => b.label), datasets: [{ data: countBy(), backgroundColor: 'rgba(99, 102, 241, 0.7)', borderColor: 'rgba(99, 102, 241, 1)', borderWidth: 1, borderRadius: 4 }] }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { ticks: { color: getTextColor(), font: { size: 10 } }, grid: { display: false } }, y: { ticks: { color: getTextColor(), font: { size: 10 } }, grid: { color: getGridColor() } } } } });
}

function renderDatasetCards() {
  const stats = state.datasets.stats || {};
  const cards = [
    { title: '后端数据包', text: backendState.url ? `已从 ${backendState.url} 读取 ancient_visualization_dataset.json。` : '当前使用前端回退数据。' },
    { title: '星官连线', text: `星官组数：${stats.constellation_groups ?? (state.datasets.constellations || []).length}` },
    { title: '恒星目录', text: `有效目录条目：${stats.catalog_rows_valid ?? (state.datasets.catalog || []).length}` }
  ];
  const el = document.getElementById('datasetCards');
  if (el) el.innerHTML = cards.map(card => `<div class="dataset-card"><h4>${card.title}</h4><p>${card.text}</p></div>`).join('');
}

async function loadStellarAnalysis() {
  const badge = document.getElementById('stellarSelectionBadge');
  if (badge) badge.textContent = '正在加载恒星分析…';
  try {
    const response = await fetch('/api/stellar-analysis', { cache: 'no-store' });
    if (!response.ok) throw new Error(`stellar-analysis request failed: ${response.status}`);
    const payload = await response.json();
    state.stellar.payload = payload;
    state.stellar.stats = payload.stats || {};
    
    renderStellarStats();
    renderStellarKeyStats();
    renderStellarAnalysis();

    // 加载成功后更新徽标文字
    if (badge) {
      const validPoints = payload.stats?.filtered || 0;
      badge.textContent = validPoints > 0 ? '加载完毕' : '暂无匹配恒星';
    }
  } catch (error) {
    console.error('[DEBUG ERROR] loadStellarAnalysis:', error);
    if (badge) badge.textContent = '恒星分析加载失败';
    state.stellar.payload = null;
  }
}

function renderStellarStats() {
  const stats = state.stellar.stats || {};
  const el = document.getElementById('stellarStats');
  if (!el) return;
  el.innerHTML = [
    ['总样本', stats.total],
    ['有效样本', stats.filtered],
    ['CMD 点数', stats.cmd_points],
    ['HR 点数', stats.hr_points],
    ['运动样本', stats.motion_points],
    ['剔除缺失 Teff', stats.missing_teff_removed]
  ].map(([label, value]) => `<div class="summary-item"><strong>${label}</strong><span>${value ?? '—'}</span></div>`).join('');
}

function renderVisuals() {
  renderSummary();
  renderStarMap();
  renderBrightnessChart();
  renderDatasetCards();
  if (state.stage === 'detail') {
    recomputeDimensionality();
  }
  if (state.stage === 'stellar') {
    renderStellarAnalysis();
  }
}

async function recomputeDimensionality() {
  console.log('[DEBUG] recomputeDimensionality: 准备读取后端降维输出数据...');
  try {
    const payload = await loadDimensionalityPayload();
    console.log('[DEBUG] recomputeDimensionality: 获取到后端数据', { 
      stats: payload.stats, 
      rowsLength: payload.rows?.length, 
      embeddingsKeys: payload.embeddings ? Object.keys(payload.embeddings) : '无' 
    });
    
    state.dim.payload = payload;
    state.dim.stats = payload.stats || {};
    state.dim.variance = payload.pca?.variance_ratio || [];
    
    document.getElementById('algoNote').textContent = DIM_ALGO_NOTES[state.dim.algorithm];
    
    console.log('[DEBUG] recomputeDimensionality: 执行 renderStage2Stats()');
    renderStage2Stats();
    console.log('[DEBUG] recomputeDimensionality: 执行 renderVarianceChart()');
    renderVarianceChart();
    console.log('[DEBUG] recomputeDimensionality: 执行 renderDimensionality()');
    renderDimensionality();
  } catch (error) {
    console.error('[DEBUG ERROR] recomputeDimensionality: 处理链路中断', error);
    document.getElementById('pointDetails').textContent = '无法加载后端降维结果。错误信息: ' + error.message;
  }
}

async function loadDimensionalityPayload() {
  console.log('[DEBUG] loadDimensionalityPayload: 发起请求 -> /api/dim-reduction');
  const response = await fetch('/api/dim-reduction', { cache: 'no-store' });
  console.log('[DEBUG] loadDimensionalityPayload: 响应状态码', response.status);
  if (!response.ok) throw new Error(`Failed to load backend payload: ${response.status}`);
  const data = await response.json();
  return data;
}

function renderStage2Stats() {
  const stats = state.dim.stats || {};
  const variance = state.dim.variance || [0, 0, 0];
  
  // 兼容读取后端 Python 的下划线命名法
  const missingRatio = stats.missing_ratio ?? stats.missingRatio ?? 0;
  const featureCount = stats.feature_count ?? stats.featureCount ?? '—';

  const html = [
    ['总样本', stats.total],
    ['保留样本', stats.filtered],
    ['缺失率', `${(missingRatio * 100).toFixed(1)}%`],
    ['特征维度', featureCount],
    ['PCA1', `${(variance[0] * 100).toFixed(1)}%`],
    ['PCA2', `${(variance[1] * 100).toFixed(1)}%`]
  ].map(([label, value]) => `<div class="summary-item"><strong>${label}</strong><span>${value ?? '—'}</span></div>`).join('');
  document.getElementById('stage2Stats').innerHTML = html;
}

function renderVarianceChart() {
  console.log('[DEBUG] renderVarianceChart: 渲染方差碎石图');
  const canvas = document.getElementById('varianceChart');
  if (!canvas) return;
  if (state.charts.variance) state.charts.variance.destroy();
  const variance = state.dim.variance.length ? state.dim.variance : [0, 0, 0];
  state.charts.variance = new Chart(canvas, {
    type: 'line', // 修改为折线图
    data: {
      labels: ['PC1', 'PC2', 'Rest'],
      datasets: [{
        data: variance,
        borderColor: 'rgba(99, 102, 241, 1)',
        backgroundColor: 'rgba(168, 85, 247, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(168, 85, 247, 1)',
        pointRadius: 5,
        pointHoverRadius: 7,
        fill: false,
        tension: 0.1
      }]
    },
    options: { 
      responsive: true, 
      maintainAspectRatio: false, 
      plugins: { legend: { display: false } }, 
      scales: { 
        x: { ticks: { color: getTextColor() }, grid: { display: false } }, 
        y: { ticks: { color: getTextColor(), callback: v => `${Math.round(v * 100)}%` }, grid: { color: getGridColor() }, min: 0, max: 1 } 
      } 
    }
  });
}

function renderStellarAnalysis() {
  const payload = state.stellar.payload;
  if (!payload) return;
  
  // 限制仅在主图表更新、初始化时绘制小定位星图
  renderStellarMiniMap(payload);

  if (state.stellar.viewMode === 'cmd') {
    renderCmdChart(payload);
  } else if (state.stellar.viewMode === 'hr') {
    renderHrChart(payload);
  } else if (state.stellar.viewMode === 'cmd3d') {
    renderCmd3DChart(payload);
  } else {
    renderMotionChart(payload);
  }
  renderStellarPointDetails(payload);
  renderStellarMotionStats(payload);
}

// 6. 修正着色的 renderCmdChart (CMD X轴不逆序，颜色 teff 正确反转)
function renderCmdChart(payload) {
  toggleStellarCanvas('cmd');
  const points = payload.cmd?.points || [];
  const usable = points.filter(p => Number.isFinite(Number(p.x)) && Number.isFinite(Number(p.y)));
  const ctx = document.getElementById('stellarCanvas2D');
  if (!ctx) return;
  if (state.charts.stellar) state.charts.stellar.destroy();

  const colorField = state.stellar.colorField;
  const colorValues = usable.map(p => {
    const row = p.row || {};
    if (colorField === 'mh') return Number(row.mh ?? 0);
    if (colorField === 'rv') return Number(row.rv ?? 0);
    if (colorField === 'parallax') return Number(row.parallax ?? 0);
    if (colorField === 'pm_total') return Number(row.pm_total ?? 0);
    if (colorField === 'quality') return row.quality_flag === 'good' ? 1 : 0;
    return Number(row.teff ?? 0);
  });

  const reverse = (colorField === 'teff'); // 有效温度着色时反转：大值(蓝)，小值(红)
  const colorScale = buildColorScale(colorValues, reverse);

  state.charts.stellar = new Chart(ctx, {
    type: 'scatter',
    data: { datasets: [{
      label: 'CMD',
      data: usable.map((p, i) => ({ x: p.x, y: p.y, row: p.row, color: colorScale(colorValues[i]), radius: sizeToStellarRadius(p.row) })),
      pointBackgroundColor: ctx2 => ctx2.raw?.color || 'rgba(59,130,246,.8)',
      pointRadius: ctx2 => ctx2.raw?.radius || 3,
      pointBorderColor: 'rgba(255,255,255,.65)',
      pointBorderWidth: 0.5,
    }] },
    options: stellarScatterOptions('bp_rp (颜色指数)', 'G / Vmag', { reverseY: true }) // CMD 图纵轴视星等通常逆序（越亮星等数值越小，越靠上）
  });
}

function renderHrChart(payload) {
  toggleStellarCanvas('hr');
  const points = payload.hr?.points || [];
  const usable = points.filter(p => Number.isFinite(Number(p.x)) && Number.isFinite(Number(p.y)));
  const ctx = document.getElementById('stellarCanvas2D');
  if (!ctx) return;
  if (state.charts.stellar) state.charts.stellar.destroy();

  const colorField = state.stellar.colorField;
  const colorValues = usable.map(p => {
    const row = p.row || {};
    if (colorField === 'mh') return Number(row.mh ?? 0);
    if (colorField === 'rv') return Number(row.rv ?? 0);
    if (colorField === 'parallax') return Number(row.parallax ?? 0);
    if (colorField === 'pm_total') return Number(row.pm_total ?? 0);
    if (colorField === 'quality') return row.quality_flag === 'good' ? 1 : 0;
    return Number(row.teff ?? 0);
  });

  const reverse = (colorField === 'teff');
  const colorScale = buildColorScale(colorValues, reverse);

  // 1. 恒星本身的数据集
  const stellarDataset = {
    label: '蟹状星云天区恒星',
    data: usable.map((p, i) => {
      const abs_mag = p.row.abs_mag;
      const l_sun = Number.isFinite(abs_mag) ? Math.pow(10, (4.67 - abs_mag) / 2.5) : null;
      return { 
        x: p.x, 
        y: l_sun, 
        row: p.row, 
        color: colorScale(colorValues[i]), 
        radius: sizeToStellarRadius(p.row) 
      };
    }).filter(pt => pt.y !== null && pt.y > 0),
    pointBackgroundColor: ctx2 => ctx2.raw?.color || 'rgba(168,85,247,.8)',
    pointRadius: ctx2 => ctx2.raw?.radius || 3,
    pointBorderColor: 'rgba(255,255,255,.65)',
    pointBorderWidth: 0.5,
    order: 10
  };

  // 2. Heads or Tails "Big Picture"：引入常驻的“太阳参考锚点 (Sol)”
  // 温度 5778K，绝对星等 4.67 (光度为 1.0)
  const sunDataset = {
    label: '我们的太阳 (Sol - 参考锚点)',
    data: [{ 
      x: 5778, 
      y: 1.0, 
      row: { name: '太阳 (Sol)', teff: 5778, abs_mag: 4.67, office: '太阳系 (系统参考原点)' } 
    }],
    pointBackgroundColor: '#f59e0b', // 显眼的黄色金光 [1]
    pointRadius: 8,                  // 突出显示
    pointBorderColor: '#ffffff',
    pointBorderWidth: 1.7,
    order: 100                        // 确保浮于顶层
  };

  state.charts.stellar = new Chart(ctx, {
    type: 'scatter',
    data: { datasets: [stellarDataset, sunDataset] },
    options: stellarScatterOptions('Teff (K)', 'L / L_☉ (相对于太阳的光度)', { 
      reverseX: true, 
      reverseY: false,
      yScaleType: 'logarithmic',
      yMax: 1000000,
      yMin: 0.0001,
      xMin: 2900,
      xMax: 15500
    })
  });
}

// 8. 修正 3D CMD 渲染，确保在 3D 独立容器中运行
function renderCmd3DChart(payload) {
  toggleStellarCanvas('cmd3d');
  const points = payload.cmd3d?.points || [];
  const usable = points.filter(p => Number.isFinite(Number(p.x)) && Number.isFinite(Number(p.y)) && Number.isFinite(Number(p.z)));
  const container = document.getElementById('stellarCanvas3D');
  if (!container) return;

  const trace = {
    type: 'scatter3d',
    mode: 'markers',
    x: usable.map(p => p.x),
    y: usable.map(p => p.y),
    z: usable.map(p => p.z),
    marker: { size: 4, color: usable.map(p => p.z), colorscale: 'Viridis', opacity: 0.85 },
    text: usable.map(p => `${p.row?.name || ''} (d ≈ ${Math.round(p.row?.dist_pc || 0)} pc) / ${p.stage}`),
  };
  Plotly.newPlot('stellarCanvas3D', [trace], { 
    margin: { l: 0, r: 0, t: 0, b: 0 }, 
    scene: { 
      xaxis: { title: 'X 轴 (pc - 空间位置)' }, 
      yaxis: { title: 'Y 轴 (pc - 空间位置)' }, 
      zaxis: { title: 'Z 轴 (pc - 空间位置)' } 
    } 
  }, { responsive: true, displayModeBar: false });
}

// 1. 定义自定义插件用于在 Canvas 上绘制矢量箭头
const motionArrowsPlugin = {
  id: 'motionArrows',
  afterDatasetsDraw(chart, args, options) {
    const { ctx } = chart;
    const quiver = options.arrows;
    if (!quiver) return;

    ctx.save();
    ctx.strokeStyle = 'rgba(99, 102, 241, 0.45)';
    ctx.lineWidth = 1.5;

    quiver.forEach(q => {
      const start = chart.scales.x.getPixelForValue(q.x);
      const startY = chart.scales.y.getPixelForValue(q.y);
      const end = chart.scales.x.getPixelForValue(q.x2);
      const endY = chart.scales.y.getPixelForValue(q.y2);

      // 绘制自行运动线段
      ctx.beginPath();
      ctx.moveTo(start, startY);
      ctx.lineTo(end, endY);
      ctx.stroke();

      // 绘制箭头端点
      ctx.fillStyle = 'rgba(168, 85, 247, 0.8)';
      ctx.beginPath();
      ctx.arc(end, endY, 2, 0, 2 * Math.PI);
      ctx.fill();
    });
    ctx.restore();
  }
};

function renderMotionChart(payload) {
  toggleStellarCanvas('motion');
  const vectors = payload.motion?.vectors || [];
  const usable = vectors.filter(v => Number.isFinite(Number(v.ra)) && Number.isFinite(Number(v.dec)));
  const ctx = document.getElementById('stellarCanvas2D');
  if (!ctx) return;
  if (state.charts.stellar) state.charts.stellar.destroy();
  const quiver = usable.map(v => {
    const scale = 0.02 * state.stellar.motionScale;
    const dx = (v.pmra || 0) * scale / 3600.0;
    const dy = (v.pmdec || 0) * scale / 3600.0;
    return { x: v.ra, y: v.dec, x2: v.ra + dx, y2: v.dec + dy, row: v.row };
  });
  const scatterData = quiver.map(q => ({ x: q.x, y: q.y, row: q.row }));
  state.charts.stellar = new Chart(ctx, {
    type: 'scatter',
    data: { datasets: [{
      label: 'Motion',
      data: scatterData,
      pointBackgroundColor: 'rgba(59,130,246,.9)',
      pointRadius: 3,
      pointBorderColor: 'rgba(255,255,255,.7)',
      pointBorderWidth: 0.5,
    }] },
    options: stellarScatterOptions('RA', 'Dec', { showArrows: quiver })
  });
}

function renderStellarMiniMap(payload) {
  const canvas = document.getElementById('stellarMiniMap');
  if (!canvas) return;
  if (state.charts.stellarMiniMap) {
    // 如果已经存在实例，直接通过高亮更新（例如，若有点击事件选中对象），不销毁图表
    return;
  }

  const vectors = payload.motion?.vectors || [];
  // 蟹状星云天区中心：RA ~ 83.63°, Dec ~ 22.01°
  state.charts.stellarMiniMap = new Chart(canvas, {
    type: 'scatter',
    data: {
      datasets: [{
        label: '天区位置',
        data: vectors.map(v => ({ x: v.ra, y: v.dec })),
        pointBackgroundColor: 'rgba(20, 184, 166, 0.45)',
        pointRadius: 2,
        pointBorderWidth: 0,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { min: 83.4, max: 83.8, ticks: { display: false }, grid: { color: 'rgba(255,255,255,0.03)' } },
        y: { min: 21.8, max: 22.1, ticks: { display: false }, grid: { color: 'rgba(255,255,255,0.03)' } }
      }
    }
  });
}

// 修复版：彻底打破无限 Resize 尺寸死循环的自愈容器切换
function toggleStellarCanvas(viewMode) {
  const wrap = document.getElementById('stellarChartWrap');
  if (!wrap) {
    console.error('[DEBUG ERROR] 未找到 stellarChartWrap 容器节点');
    return;
  }

  let c2D = document.getElementById('stellarCanvas2D');
  let c3D = document.getElementById('stellarCanvas3D');

  if (!c2D || !c3D) {
    console.log('[DEBUG] 检测到旧版 Canvas 结构，正在动态重构双通道 2D/3D 专属容器...');
    wrap.innerHTML = '';

    // 创建 2D Canvas（注意：彻底移除 canvas 元素本身的 style.width/height 以防止死循环）
    c2D = document.createElement('canvas');
    c2D.id = 'stellarCanvas2D';
    wrap.appendChild(c2D);

    // 创建 3D Div
    c3D = document.createElement('div');
    c3D.id = 'stellarCanvas3D';
    c3D.className = 'hidden';
    c3D.style.width = '100%';
    c3D.style.height = '100%';
    wrap.appendChild(c3D);
  }

  // 2. 切换显示状态
  if (viewMode === 'cmd3d') {
    c2D.classList.add('hidden');
    c3D.classList.remove('hidden');
    if (state.charts.stellar) {
      state.charts.stellar.destroy();
      state.charts.stellar = null;
    }
  } else {
    c3D.classList.add('hidden');
    c2D.classList.remove('hidden');
    c3D.innerHTML = ''; // 清理 3D 缓存
  }
}

function stellarScatterOptions(xLabel, yLabel, extra = {}) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    parsing: false,
    plugins: {
      legend: { display: false },
      tooltip: { callbacks: { label: ctx => {
        const row = ctx.raw?.row || {};
        const absMagStr = fmt(row.abs_mag);
        const l_sun = Number.isFinite(row.abs_mag) ? Math.pow(10, (4.67 - row.abs_mag) / 2.5) : null;
        const l_sun_str = l_sun !== null ? (l_sun >= 100 || l_sun <= 0.01 ? l_sun.toExponential(2) : l_sun.toFixed(2)) : '—';
        return [
          `${row.name || '参考原点'}`,
          `Teff: ${fmt(row.teff)} K`,
          `M_G: ${absMagStr}`,
          `L / L_☉: ${l_sun_str}`
        ];
      } } },
      zoom: { pan: { enabled: true, mode: 'xy' }, zoom: { wheel: { enabled: true }, pinch: { enabled: true }, mode: 'xy' } }
    },
    scales: {
      x: { 
        title: { display: true, text: xLabel }, 
        min: extra.xMin !== undefined ? extra.xMin : undefined,
        max: extra.xMax !== undefined ? extra.xMax : undefined,
        ticks: { color: getTextColor() }, 
        grid: { color: getGridColor() },
        reverse: extra.reverseX || false
      },
      y: { 
        type: extra.yScaleType || 'linear',
        min: extra.yMin !== undefined ? extra.yMin : undefined,
        max: extra.yMax !== undefined ? extra.yMax : undefined,
        title: { display: true, text: yLabel }, 
        ticks: { 
          color: getTextColor(),
          callback: function(value) {
            if (extra.yScaleType === 'logarithmic') {
              const remain = value / Math.pow(10, Math.floor(Math.log10(value)));
              if (remain === 1 || remain === 3) {
                if (value >= 100 || value <= 0.01) return value.toExponential(0);
                return value;
              }
              return null;
            }
            return value;
          }
        }, 
        grid: { color: getGridColor() },
        reverse: extra.reverseY || false
      }
    },
    onClick: (_, elements) => {
      if (!elements.length) return;
      const raw = state.charts.stellar.data.datasets[elements[0].datasetIndex].data[elements[0].index];
      if (raw?.row) {
        state.stellar.selected = raw.row;
        renderStellarPointDetailsFromRow(raw.row);
        
        // 【Goodman 联动升级点】：当点击左侧图表的某个恒星时，右侧的小星图自动无延迟地联动高亮该星
        renderStellarMiniMap(state.stellar.payload, raw.row.id);
      }
    },
    ...extra
  };
}

function sizeToStellarRadius(row) {
  const field = state.stellar.sizeField;
  const value = Number(row?.[field] ?? row?.parallax_error ?? row?.pm_total ?? row?.ruwe ?? row?.mag ?? 1);
  if (!Number.isFinite(value)) return 3;
  if (field === 'parallax_error') return Math.min(10, 2 + value * 2.5);
  if (field === 'pm_total') return Math.min(10, 2 + value / 50.0);
  if (field === 'ruwe') return Math.min(10, 2 + value * 1.2);
  return Math.max(2, 8 - value * 0.8);
}

function renderStellarKeyStats() {
  const stats = state.stellar.stats || {};
  const el = document.getElementById('stellarKeyStats');
  if (!el) return;
  const items = [
    `视差异常剔除：${stats.parallax_outliers_removed ?? 0}`,
    `当前视图：${state.stellar.viewMode.toUpperCase()}`,
    `时间偏移：${state.stellar.epochYears} 年`
  ];
  el.innerHTML = items.map(text => `<div class="summary-item"><strong>统计</strong><span>${text}</span></div>`).join('');
}

function renderStellarPointDetails(payload) {
  if (!state.stellar.selected) {
    const first = (payload.cmd?.points || [])[0] || (payload.hr?.points || [])[0] || (payload.motion?.vectors || [])[0];
    if (first?.row) renderStellarPointDetailsFromRow(first.row);
  }
}

function renderStellarPointDetailsFromRow(row) {
  const el = document.getElementById('stellarPointDetails');
  if (!el) return;
  el.innerHTML = [
    `<div><strong>${row.name || '未知对象'}</strong></div>`,
    `<div>HIP：${row.hip ?? '—'}</div>`,
    `<div>星官：${row.office ?? '—'}</div>`,
    `<div>阶段：${row.stage ?? 'unknown'}</div>`,
    `<div>RA / Dec：${fmt(row.ra)} / ${fmt(row.dec)}</div>`,
    `<div>bp_rp：${fmt(row.bp_rp)}</div>`,
    `<div>G：${fmt(row.g_mag ?? row.mag)}</div>`,
    `<div>绝对星等：${fmt(row.abs_mag)}</div>`,
    `<div>Teff：${fmt(row.teff)}</div>`,
    `<div>pmra / pmdec：${fmt(row.pmra)} / ${fmt(row.pmdec)}</div>`,
    `<div>RV：${fmt(row.rv)}</div>`,
    `<div>质量：${row.quality_flag || 'good'}</div>`
  ].join('');
}

function renderStellarMotionStats(payload) {
  const el = document.getElementById('stellarMotionStats');
  if (!el) return;
  const vectors = payload.motion?.vectors || [];
  const valid = vectors.filter(v => Number.isFinite(Number(v.pm_total)));
  const avg = valid.length ? valid.reduce((s, v) => s + (Number(v.pm_total) || 0), 0) / valid.length : 0;
  const max = valid.length ? Math.max(...valid.map(v => Number(v.pm_total) || 0)) : 0;
  el.innerHTML = [
    `<div>有效运动样本：${valid.length}</div>`,
    `<div>平均自行：${avg.toFixed(3)}</div>`,
    `<div>最大自行：${max.toFixed(3)}</div>`,
    `<div>当前时间偏移：${state.stellar.epochYears} 年</div>`
  ].join('');
}
function renderDimensionality() {
  console.log('[DEBUG] renderDimensionality: 开始解析主散点图');
  const payload = state.dim.payload;
  if (!payload || !payload.embeddings) {
    console.error('[DEBUG ERROR] renderDimensionality: 状态池中缺失有效载荷 payload', payload);
    return;
  }
  
  const embedding = payload.embeddings[state.dim.algorithm] || [];
  const rows = payload.rows || [];
  const clusterLabels = payload.cluster_labels || [];
  console.log('[DEBUG] renderDimensionality: 数据池指标', {
    embeddingLength: embedding.length,
    rowsLength: rows.length,
    clusterLabelsLength: clusterLabels.length,
    currentAlgorithm: state.dim.algorithm
  });

  const rowById = new Map(rows.map(row => [String(row.id), row]));
  const colorValues = embedding.map(point => getMetricValue(rowById.get(String(point.id)) || {}, state.dim.colorField));
  
  // 当颜色字段为有效温度 'teff' 时启用反转
  const reverse = (state.dim.colorField === 'teff');
  const colorScale = buildColorScale(colorValues, reverse);
  
  const points = embedding.map((point, index) => {
    const row = rowById.get(String(point.id)) || {};
    const cluster = clusterLabels[index] ?? point.cluster ?? -1;
    return {
      x: point.x,
      y: point.y,
      row,
      cluster,
      color: colorScale(colorValues[index]),
      radius: sizeToRadius(getMetricValue(row, state.dim.sizeField)),
      outlier: cluster === -1 || point.outlier
    };
  });
  
  const activePoints = points.filter(pt => !pt.outlier || state.dim.showOutliers);
  const clusterIds = [...new Set(points.map(pt => pt.cluster).filter(v => v >= 0))];
  console.log('[DEBUG] renderDimensionality: 构建点集成功', {
    activePointsCount: activePoints.length,
    clusterIds: clusterIds
  });

  const clusterDatasets = clusterIds.map(label => {
    const members = activePoints.filter(pt => pt.cluster === label);
    return { 
      label: `Cluster ${label + 1}`, 
      data: members, 
      showLine: false, 
      pointRadius: ctx => (ctx.raw && typeof ctx.raw.radius === 'number') ? ctx.raw.radius : 4, 
      pointBackgroundColor: `hsla(${(label * 61) % 360}, 82%, 62%, 0.78)`, 
      pointBorderColor: 'rgba(255,255,255,0.7)', 
      pointBorderWidth: 0.5, 
      order: 10 
    };
  });
  
  const outliers = activePoints.filter(pt => pt.outlier);
  const scatterDatasets = [
    { 
      label: 'Embedding', 
      data: activePoints, 
      showLine: false, 
      pointRadius: ctx => (ctx.raw && typeof ctx.raw.radius === 'number') ? ctx.raw.radius : 4, 
      pointBackgroundColor: ctx => ctx.raw ? ctx.raw.color : 'rgba(99,102,241,0.8)', 
      pointBorderColor: ctx => (ctx.raw && ctx.raw.outlier) ? 'rgba(239,68,68,.95)' : 'rgba(255,255,255,.45)', 
      pointBorderWidth: ctx => (ctx.raw && ctx.raw.outlier) ? 1.7 : 0.6, 
      order: 20 
    },
    ...(state.dim.showClusters ? clusterDatasets : []),
    ...(state.dim.showOutliers ? [{ 
      label: 'Outliers', 
      data: outliers, 
      showLine: false, 
      pointRadius: ctx => (ctx.raw && typeof ctx.raw.radius === 'number') ? Math.max(ctx.raw.radius + 2, 4.2) : 5, 
      pointBackgroundColor: 'rgba(239,68,68,.9)', 
      pointBorderColor: 'rgba(255,255,255,.85)', 
      pointBorderWidth: 1.2, 
      order: 30 
    }] : [])
  ];

  const dimCanvas = document.getElementById('dimCanvas');
  console.log('[DEBUG] renderDimensionality: 检查 DOM 节点 #dimCanvas', dimCanvas);
  if (!dimCanvas) {
    console.error('[DEBUG ERROR] renderDimensionality: 未能在页面上定位到 #dimCanvas');
    return;
  }

  try {
    if (state.charts.dim) {
      console.log('[DEBUG] renderDimensionality: 销毁原降维图表实例');
      state.charts.dim.destroy();
    }
    
    console.log('[DEBUG] renderDimensionality: 开始构造 Chart.js 降维散点图');
    state.charts.dim = new Chart(dimCanvas, {
      type: 'scatter',
      data: { datasets: scatterDatasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        parsing: false,
        onHover: (_, elements) => { 
          const badge = document.getElementById('selectionBadge');
          if (badge) badge.textContent = elements.length ? '悬停查看样本' : '尚未刷选'; 
        },
        onClick: (_, elements) => {
          if (!elements.length) return;
          const raw = state.charts.dim.data.datasets[elements[0].datasetIndex].data[elements[0].index];
          if (!raw) return;
          state.selection.point = raw.row;
          renderPointDetails(raw.row, raw.cluster);
        },
        plugins: {
          legend: { display: false },
          tooltip: { callbacks: { label: ctx => { const raw = ctx.raw || {}; const row = raw.row || {}; return [`${row.name || '样本'}`, `星官: ${row.office || '未分组'}`, `HIP: ${row.hip ?? '—'}`, `颜色字段值: ${formatMetric(row, state.dim.colorField)}`, `点大小字段值: ${formatMetric(row, state.dim.sizeField)}`]; } } },
          zoom: { pan: { enabled: true, mode: 'xy', modifierKey: null }, zoom: { wheel: { enabled: true, speed: 0.08 }, pinch: { enabled: true }, mode: 'xy' } }
        },
        scales: { x: { ticks: { color: getTextColor(), maxTicksLimit: 8 }, grid: { color: getGridColor() } }, y: { ticks: { color: getTextColor(), maxTicksLimit: 8 }, grid: { color: getGridColor() } } }
      }
    });
    console.log('[DEBUG] renderDimensionality: 主图 Chart.js 实例化完毕');
  } catch (chartErr) {
    console.error('[DEBUG ERROR] renderDimensionality: 主散点图初始化失败', chartErr);
  }

  const clusterChartCanvas = document.getElementById('clusterChart');
  console.log('[DEBUG] renderDimensionality: 检查 DOM 节点 #clusterChart', clusterChartCanvas);
  
  if (clusterChartCanvas) {
    try {
      if (state.charts.cluster) {
        state.charts.cluster.destroy();
      }
      
      const clusterSizes = clusterIds.map(clusterId => {
        return points.filter(point => point.cluster === clusterId).length;
      });
      
      state.charts.cluster = new Chart(clusterChartCanvas, {
        type: 'bar',
        data: { 
          labels: clusterIds.map(clusterId => `C${clusterId + 1}`), 
          datasets: [{ 
            data: clusterSizes, 
            backgroundColor: 'rgba(20, 184, 166, 0.75)', 
            borderRadius: 6 
          }] 
        },
        options: { 
          responsive: true, 
          maintainAspectRatio: false, 
          plugins: { 
            legend: { display: false } 
          }, 
          scales: { 
            x: { 
              ticks: { color: getTextColor(), font: { size: 10 } }, 
              grid: { display: false } 
            }, 
            y: { 
              ticks: { color: getTextColor(), font: { size: 10 } }, 
              grid: { color: getGridColor() } 
            } 
          } 
        }
      });
      console.log('[DEBUG] renderDimensionality: 聚类分块柱状图实例化完毕');
    } catch (clusterChartErr) {
      console.error('[DEBUG ERROR] renderDimensionality: 聚类柱状图构建失败', clusterChartErr);
    }
  }

  if (state.selection.point) {
    const selected = state.selection.point;
    const match = points.find(item => String(item.row.id) === String(selected.id));
    renderPointDetails(selected, match ? match.cluster : -1);
  }
  
  renderRegionStats(activePoints);
} 

function renderPointDetails(row, clusterId) {
  const lines = [
    `<div><strong>${row.name || '未知样本'}</strong></div>`,
    `<div>HIP：${row.hip ?? '—'}</div>`,
    `<div>星官：${row.office ?? '—'}</div>`,
    `<div>聚类：${clusterId >= 0 ? `Cluster ${clusterId + 1}` : '异常点 / 噪声'}</div>`,
    `<div>RA/Dec：${formatMetric(row, 'ra')} / ${formatMetric(row, 'dec')}</div>`,
    `<div>视差：${formatMetric(row, 'parallax')}</div>`,
    `<div>自行：${formatMetric(row, 'pmra')} / ${formatMetric(row, 'pmdec')}</div>`,
    `<div>温度：${formatMetric(row, 'teff')}</div>`,
    `<div>星等：${formatMetric(row, 'mag')}</div>`,
    `<div>RUWE：${formatMetric(row, 'ruwe')}</div>`
  ];
  document.getElementById('pointDetails').innerHTML = lines.join('');
}

function renderRegionStats(points) {
  if (!points.length) {
    document.getElementById('regionStats').textContent = '当前没有可统计的点。';
    return;
  }
  const avg = key => average(points.map(p => Number(p.row[key])).filter(Number.isFinite));
  const outlierCount = points.filter(p => p.outlier).length;
  document.getElementById('regionStats').innerHTML = [
    `<div>区域样本：${points.length}</div>`,
    `<div>平均温度：${fmt(avg('teff'))}</div>`,
    `<div>平均星等：${fmt(avg('mag'))}</div>`,
    `<div>平均视差：${fmt(avg('parallax'))}</div>`,
    `<div>异常点：${outlierCount}</div>`
  ].join('');
}

function getMetricValue(row, field) {
  const map = { teff: row.teff, mag: row.mag, parallax: row.parallax, ruwe: row.ruwe, abs_mag: row.abs_mag, pm_total: row.pm_total, parallax_error: row.parallax_error, rv: row.rv, mh: row.mh };
  return Number.isFinite(map[field]) ? map[field] : 0;
}

function formatMetric(row, field) {
  const value = getMetricValue(row, field);
  return Number.isFinite(value) ? value.toFixed(3).replace(/\.000$/, '.000') : '—';
}

function buildColorScale(values, reverse = false) {
  const filtered = values.filter(Number.isFinite);
  const min = filtered.length ? Math.min(...filtered) : 0;
  const max = filtered.length ? Math.max(...filtered) : 1;
  return value => {
    const t = max === min ? 0.5 : (value - min) / (max - min);
    const hue = reverse ? (10 + t * 220) : (230 - t * 220); // reverse = true 时，低温(t=0)对应10红，高温(t=1)对应230蓝
    const sat = 75;
    const light = 55 - t * 10;
    return `hsla(${hue}, ${sat}%, ${light}%, 0.82)`;
  };
}

function sizeToRadius(value) {
  const v = Number(value);
  if (!Number.isFinite(v)) return 4;
  if (state.dim.sizeField === 'mag') return Math.max(2.4, 9.5 - v * 0.8);
  if (state.dim.sizeField === 'parallax') return Math.min(9, 2.2 + v * 0.25);
  return Math.min(8.2, 2.5 + v * 0.9);
}

function average(values) { return values.length ? values.reduce((a, b) => a + b, 0) / values.length : 0; }
function fmt(v) { return Number.isFinite(v) ? v.toFixed(3) : '—'; }

function pickGroupColor(index) {
  const palette = ['#6366f1', '#a855f7', '#14b8a6', '#f59e0b', '#f97316', '#10b981', '#06b6d4', '#ec4899'];
  return palette[index % palette.length];
}
function getPointFillColor() { return state.theme === 'dark' ? 'rgba(255, 255, 255)' : 'rgba(0, 0, 0)'; }
function rgbaFromHex(hex, alpha) { const normalized = hex.replace('#', ''); const bigint = parseInt(normalized, 16); const r = (bigint >> 16) & 255; const g = (bigint >> 8) & 255; const b = bigint & 255; return `rgba(${r}, ${g}, ${b}, ${alpha})`; }
function getPointRadius(mag) { const value = Number(mag); if (!Number.isFinite(value)) return 0.01; const MIN_RADIUS = 0.7; const MAX_RADIUS = 8; const MIN_MAG = -1.44; const MAX_MAG = 12; const clampedMag = Math.max(MIN_MAG, Math.min(MAX_MAG, value)); const relativeBrightness = Math.pow(10, -0.4 * clampedMag); const maxBrightness = Math.pow(10, -0.4 * MIN_MAG); const minBrightness = Math.pow(10, -0.4 * MAX_MAG); const normalized = (relativeBrightness - minBrightness) / (maxBrightness - minBrightness); return MIN_RADIUS + normalized * (MAX_RADIUS - MIN_RADIUS); }
function getTextColor() { return getComputedStyle(document.documentElement).getPropertyValue('--text').trim(); }
function getGridColor() { return getComputedStyle(document.documentElement).getPropertyValue('--line').trim(); }