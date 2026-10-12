const DATA_FILES = {
    constel: ['./data/merged_Chinese_astronomy_data.json', '/frontend/data/merged_Chinese_astronomy_data.json', '/data/merged_Chinese_astronomy_data.json']
  };
  
  const FALLBACK_DATA = {
    constel: [
      { '编号': '1', '星官': '北极', '星数': '5+3', '中国星名': '北极一(太子)', '拜耳命名法': '小熊座γ', 'HIP': '75097', '视星等': '3.04~3.09' }
    ]
  };
  
  const state = {
    theme: 'dark',
    threshold: 10,
    timeIndex: 4,
    layer: 'combined',
    datasets: {},
    charts: {}
  };
  
  document.addEventListener('DOMContentLoaded', () => {
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
    
    // Double click on Star Map canvas to reset zoom
    document.getElementById('starMap').addEventListener('dblclick', () => {
      if (state.charts.starMap) {
        state.charts.starMap.resetZoom();
      }
    });
  }
  
  function applyTheme(theme) {
    state.theme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    document.body.setAttribute('data-theme', theme);
  }
  
  async function loadAllData() {
    const summaryCards = document.getElementById('summaryCards');
    summaryCards.innerHTML = '<div class="stat-card">正在读取数据…</div>';
    try {
      const dataset = await resolveAncientDataset();
      state.datasets = dataset;
      renderSummary();
      renderDatasetCards();
      renderVisuals();
    } catch (error) {
      console.error(error);
      state.datasets = cloneFallbackData();
      renderSummary();
      renderDatasetCards();
      renderVisuals();
      summaryCards.insertAdjacentHTML('afterbegin', '<div class="stat-card stat-warning">已切换到内置演示数据</div>');
    }
  }
  
  async function resolveAncientDataset() {
    const constel = await loadStructuredData('constel');
    const dataset = {
      constel,
      constellations: buildConstellationsFromChineseAstronomy(constel),
      constellation_points: []
    };
  
    return dataset;
  }
  
  async function loadStructuredData(name) {
    const candidates = DATA_FILES[name] || [];
    for (const candidate of candidates) {
      try {
        console.log(`[data] trying ${name}: ${candidate}`);
        const response = await fetch(candidate, { cache: 'no-store' });
        if (!response.ok) continue;
        const data = await response.json();
        if (Array.isArray(data)) {
          console.log(`[data] loaded ${name} from ${candidate} rows=${data.length}`);
          return data;
        }
        if (data && typeof data === 'object') {
          console.log(`[data] loaded ${name} from ${candidate} object keys=${Object.keys(data).join(',')}`);
          return data;
        }
      } catch (error) {
        console.warn(`[data] failed ${name}: ${candidate}`, error);
      }
    }
    console.warn(`[data] fallback to embedded data for ${name}`);
    return FALLBACK_DATA[name] ? cloneRows(FALLBACK_DATA[name]) : null;
  }
  
  function cloneRows(rows) {
    return rows.map(row => ({ ...row }));
  }
  
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
      groups.get(name).push({
        ra,
        dec,
        mag: Number(row.mag ?? row.Vmag ?? row['视星等'] ?? 6.0),
        hip,
        label: row['中国星名'] || `HIP ${hip}`,
        order: index
      });
    });
  
    return [...groups.entries()]
      .map(([name, points]) => ({
        name,
        points: points.sort((a, b) => a.order - b.order),
        style: { linewidth: 1.5, linestyle: '-' }
      }))
      .filter(group => group.points.length >= 2);
  }
  
  function cloneFallbackData() {
    return Object.fromEntries(Object.entries(FALLBACK_DATA).map(([k, v]) => [k, cloneRows(v)]));
  }
  
  function renderSummary() {
    const constellationGroups = state.datasets.constellations || [];
  
    const summary = [
      { label: '星官数量', value: constellationGroups.length },
      { label: '可见星官点数', value: constellationGroups.reduce((sum, g) => sum + (g.points?.filter(p => Number(p.mag ?? 99) <= state.threshold).length || 0), 0) }
    ];
  
    document.getElementById('summaryCards').innerHTML = summary.map(item => `
      <div class="stat-card">
        <div class="stat-label">${item.label}</div>
        <div class="stat-value">${item.value}</div>
      </div>
    `).join('');
  }
  
  function renderDatasetCards() {
    const cards = [
      { title: '星官连线 (Constellations)', text: '仅从 merged_Chinese_astronomy_data.json 中提取星官及其连线信息。' }
    ];
    document.getElementById('datasetCards').innerHTML = cards.map(card => `
      <div class="dataset-card">
        <h4>${card.title}</h4>
        <p>${card.text}</p>
      </div>
    `).join('');
  }
  
  function renderVisuals() {
    renderStarMap();
    renderBrightnessChart();
    updateTimeLabel();
    updateMapBadge();
    syncChartHeights();
  }
  
  function syncChartHeights() {
    const starBox = document.querySelector('.chart-box-large');
    const brightBox = document.querySelector('.chart-box-medium');
    if (starBox) starBox.style.height = '560px';
    if (brightBox) brightBox.style.height = '320px';
  }
  
  function updateTimeLabel() {
    const labels = ['1054 / 星官连线', '1054 / 星官连线', '1054 / 星官连线', '1054 / 星官连线', '1054 / 星官连线'];
    const el = document.getElementById('timeSliderLabel');
    if (el) el.textContent = labels[state.timeIndex] || labels[4];
  }
  
  function updateMapBadge() {
    const badges = {
      combined: '仅星官 (Constellations)',
      ancient: '仅星官 (Constellations)',
      modern: '仅星官 (Constellations)'
    };
    document.getElementById('mapBadge').textContent = badges[state.layer] || '仅星官 (Constellations)';
  }
  
  function normalizeRa(ra) {
    const value = Number(ra);
    if (!Number.isFinite(value)) return null;
    return ((value % 360) + 360) % 360;
  }
  
  function renderStarMap() {
    const constellationGroups = state.datasets.constellations || [];
  
    const lineDatasets = constellationGroups.map((group, groupIndex) => {
      const points = (group.points || [])
        .map(p => ({
          x: normalizeRa(p.ra),
          y: Number(p.dec),
          mag: Number(p.mag ?? 6.0),
          label: `${group.name} - ${p.hip ? 'HIP ' + p.hip : 'N/A'}`,
          hip: p.hip
        }))
        .filter(p => Number.isFinite(p.x) && Number.isFinite(p.y))
        .filter(p => p.mag <= state.threshold);
  
      const groupColor = pickGroupColor(groupIndex);
  
      return {
        label: group.name,
        data: points,
        showLine: true,
        borderColor: groupColor,
        borderWidth: 1.5,
        borderDash: group.style?.linestyle === '--' ? [6, 4] : [],
        fill: false,
        tension: 0.1,
        pointRadius: ctx => {
          const mag = ctx.raw ? Number(ctx.raw.mag ?? 6) : 6;
          return Math.max(2.5, 8.0 - mag / 2);
        },
        pointBackgroundColor: '#ffffff',
        pointBorderColor: groupColor,
        pointBorderWidth: 1.5,
        pointHoverRadius: 9,
        order: 10
      };
    });
  
    const datasets = [...lineDatasets];
  
    if (state.charts.starMap) state.charts.starMap.destroy();
    const canvas = document.getElementById('starMap');
    state.charts.starMap = new Chart(canvas, {
      type: 'scatter',
      data: { datasets },
      options: baseOptions('RA (deg)', 'Dec (deg)', true, {
        animation: false,
        onClick: (_, elements) => {
          if (!elements.length) return;
          const ds = state.charts.starMap.data.datasets[elements[0].datasetIndex];
          const item = ds.data[elements[0].index];
          document.getElementById('starInfo').innerHTML = `
            <strong>${item.label || ds.label}</strong><br>
            位置：(${Number(item.x).toFixed(3)}, ${Number(item.y).toFixed(3)})<br>
            星等：${item.mag ?? 'N/A'}<br>
            HIP：${item.hip ?? 'N/A'}<br>
            自行：${item.pmra ?? '-'} / ${item.pmdec ?? '-'}<br>
            径向速度：${item.rv ?? '-'}
          `;
        },
        plugins: {
          legend: {
            labels: {
              color: getTextColor(),
              filter: item => !item.text.startsWith('古背景星官') && item.text.length < 15
            }
          },
          tooltip: {
            callbacks: {
              label: ctx => {
                const raw = ctx.raw || {};
                return `${raw.label || ctx.dataset.label}: (${Number(raw.x).toFixed(2)}, ${Number(raw.y).toFixed(2)})`;
              }
            }
          },
          zoom: {
            pan: {
              enabled: true,
              mode: 'xy',
              threshold: 10
            },
            zoom: {
              wheel: {
                enabled: true,
                speed: 0.08
              },
              pinch: {
                enabled: true
              },
              mode: 'xy'
            }
          }
        },
        scales: {
          x: {
            min: 0,
            max: 360,
            reverse: true,
            title: { display: true, text: 'RA (deg)', color: getTextColor() },
            ticks: { color: getTextColor() },
            grid: { color: getGridColor() }
          },
          y: { 
            title: { display: true, text: 'Dec (deg)', color: getTextColor() }, 
            ticks: { color: getTextColor() }, 
            grid: { color: getGridColor() } 
          }
        }
      })
    });
  }
  
  function renderBrightnessChart() {
    const constellationGroups = state.datasets.constellations || [];
    const activeStars = constellationGroups.flatMap(group => (group.points || []).filter(p => Number(p.mag ?? 99) <= state.threshold));
  
    const bins = [
      { label: '< 4', min: -Infinity, max: 4 },
      { label: '4 - 6', min: 4, max: 6 },
      { label: '6 - 8', min: 6, max: 8 },
      { label: '8 - 10', min: 8, max: 10 },
      { label: '> 10', min: 10, max: Infinity }
    ];
    
    const countBy = () => bins.map(bin => activeStars.filter(r => {
      const mag = Number(r.mag ?? 99);
      return mag > bin.min && mag <= bin.max;
    }).length);
  
    if (state.charts.brightness) state.charts.brightness.destroy();
    state.charts.brightness = new Chart(document.getElementById('brightnessChart'), {
      type: 'bar',
      data: {
        labels: bins.map(b => b.label),
        datasets: [
          { 
            label: `当前选中星官点 (共 ${activeStars.length} 颗)`, 
            data: countBy(), 
            backgroundColor: 'rgba(122,162,255,0.75)' 
          }
        ]
      },
      options: baseOptions('星等区间', '数量', false)
    });
  
    document.getElementById('brightnessLegend').innerHTML = [
      ['< 4 等', '极亮星体'],
      ['4 - 6 等', '肉眼可见星体'],
      ['6 - 8 等', '较暗星体'],
      ['8 - 10 等', '更暗星体'],
      ['> 10 等', '高阈值下隐藏']
    ].map(([title, desc]) => `<div class="legend-item"><h4>${title}</h4><p>${desc}</p></div>`).join('');
  }
  
  function baseOptions(xLabel, yLabel, showAspect, extra = {}) {
    return {
      responsive: true,
      maintainAspectRatio: false,
      parsing: false,
      plugins: {
        legend: { labels: { color: getTextColor() } }
      },
      scales: {
        x: { title: { display: true, text: xLabel, color: getTextColor() }, ticks: { color: getTextColor() }, grid: { color: getGridColor() } },
        y: { title: { display: true, text: yLabel, color: getTextColor() }, ticks: { color: getTextColor() }, grid: { color: getGridColor() } }
      },
      ...extra,
      aspectRatio: showAspect ? 1.8 : undefined
    };
  }
  
  function pickGroupColor(index) {
    const palette = ['#7aa2ff', '#b18cff', '#67e8d8', '#f7c96d', '#f97316', '#22c55e', '#38bdf8', '#e879f9'];
    return palette[index % palette.length];
  }
  
  function getTextColor() {
    return getComputedStyle(document.documentElement).getPropertyValue('--text').trim();
  }
  
  function getGridColor() {
    return getComputedStyle(document.documentElement).getPropertyValue('--line').trim();
  }
  
  function getLineColor() {
    return getComputedStyle(document.documentElement).getPropertyValue('--accent').trim() || '#8ea2ff';
  }