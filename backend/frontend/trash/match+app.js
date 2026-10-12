const DATA_FILES = {
  ancient: ['./data/ancient_visualization_dataset.json', '/frontend/data/ancient_visualization_dataset.json', '/data/ancient_visualization_dataset.json'],
  constel: ['./data/merged_Chinese_astronomy_data.json', '/frontend/data/merged_Chinese_astronomy_data.json', '/data/merged_Chinese_astronomy_data.json'],
  tautou: ['./data/tautou.json', '/frontend/data/tautou.json', '/data/tautou.json'],
  crab: ['./data/crab.json', '/frontend/data/crab.json', '/data/crab.json'],
  gaia: ['./data/gaia.json', '/frontend/data/gaia.json', '/data/gaia.json']
};

const FALLBACK_DATA = {
  ancient: [
    { HIP: '3', RA: '0.00502431', Dec: '38.85927901', Vmag: '6.61', pmRA: '4.28', pmDE: '-3.42', RV: '0.00' },
    { HIP: '19', RA: '0.05330922', Dec: '38.30404973', Vmag: '6.53', pmRA: '-3.17', pmDE: '-15.37', RV: '6.30' },
    { HIP: '11767', RA: '27.479452', Dec: '36.75079', Vmag: '5.96', pmRA: '34.20', pmDE: '-12.10', RV: '2.10' },
    { HIP: '21421', RA: '63.870', Dec: '18.540', Vmag: '4.20', pmRA: '5.80', pmDE: '-8.40', RV: '11.00' }
  ],
  constel: [
    { '编号': '1', '星官': '北极', '星数': '5+3', '中国星名': '北极一(太子)', '拜耳命名法': '小熊座γ', 'HIP': '75097', '视星等': '3.04~3.09' }
  ],
  tautou: [
    { match_id: '70273258', target_name: 'ANY', ra: '57.67301526381938', dec: '17.2204750642015', filter: 'w2_f606w', flux: '19.545900344848633', flux_sigma: '0.07789039611816406' }
  ],
  crab: [
    { match_id: '3698', target_name: 'CRAB-NEB-A', ra: '83.63832659200857', dec: '22.04728069118669', filter: 'w2_f375n', flux: '19.203899383544922', flux_sigma: '0' }
  ],
  gaia: [
    { designation: 'Gaia DR3 3403817725893508224', ra: '83.59623741260648', dec: '21.98394675961578', parallax: '0.39585955061963873', phot_g_mean_mag: '19.0092', bp_rp: '2.0133057', pmra: '1.4450779593975769', pmdec: '-4.55584261044103', radial_velocity: 'null' }
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
  document.getElementById('timeSlider').addEventListener('input', e => {
    state.timeIndex = Number(e.target.value);
    updateTimeLabel();
    renderVisuals();
  });
  document.getElementById('layerSelect').addEventListener('change', e => {
    state.layer = e.target.value;
    renderVisuals();
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
    updateMatchInfo();
  } catch (error) {
    console.error(error);
    state.datasets = cloneFallbackData();
    renderSummary();
    renderDatasetCards();
    renderVisuals();
    updateMatchInfo();
    summaryCards.insertAdjacentHTML('afterbegin', '<div class="stat-card stat-warning">已切换到内置演示数据</div>');
  }
}

async function resolveAncientDataset() {
  const merged = await loadStructuredData('ancient_visualization_dataset');
  const dataset = {
    ancient: Array.isArray(merged?.catalog) ? merged.catalog : [],
    constel: await loadStructuredData('constel'),
    tautou: Array.isArray(merged?.tautou_targets) ? merged.tautou_targets : await loadStructuredData('tautou'),
    sn1054_matches: Array.isArray(merged?.sn1054_matches) ? merged.sn1054_matches : [],
    sn1054_points: Array.isArray(merged?.sn1054_points) ? merged.sn1054_points : [],
    options: merged?.options || {},
    stats: merged?.stats || {},
    constellations: Array.isArray(merged?.constellations) ? merged.constellations : [],
    constellation_points: Array.isArray(merged?.constellation_points) ? merged.constellation_points : []
  };

  if (!Array.isArray(dataset.ancient) || dataset.ancient.length === 0) {
    const fallbackAncient = await loadStructuredData('ancient');
    dataset.ancient = Array.isArray(fallbackAncient) ? fallbackAncient : [];
  }

  if (!dataset.constellations.length && Array.isArray(dataset.constel)) {
    dataset.constellations = buildConstellationsFromChineseAstronomy(dataset.constel);
  }

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
  rows.forEach((row, index) => {
    const name = String(row['星官'] ?? '').trim();
    const hip = String(row.HIP ?? row.hip ?? '').trim();
    if (!name || !hip) return;
    const ra = Number(row.RA ?? row.ra ?? row.ra_j2000 ?? row.ra_1054);
    const dec = Number(row.Dec ?? row.dec ?? row.dec_j2000 ?? row.dec_1054);
    if (!Number.isFinite(ra) || !Number.isFinite(dec)) return;
    if (!groups.has(name)) groups.set(name, []);
    groups.get(name).push({ ra, dec, hip, label: row['中国星名'] || `HIP ${hip}`, order: index });
  });

  return [...groups.entries()]
    .map(([name, points]) => ({
      name,
      points: points.sort((a, b) => a.order - b.order),
      style: { linewidth: 1.2, linestyle: '-' }
    }))
    .filter(group => group.points.length >= 2);
}

function cloneFallbackData() {
  return Object.fromEntries(Object.entries(FALLBACK_DATA).map(([k, v]) => [k, cloneRows(v)]));
}

function updateMatchInfo() {
  const matches = state.datasets.sn1054_matches || [];
  const text = matches.length
    ? matches.map(m => `SN1054 → HIP ${m.matched_hip} / 距离 ${m.distance_deg}°`).join('<br>')
    : '未找到 SN1054 容差匹配结果。';
  document.getElementById('matchInfo').innerHTML = text;
}

function renderSummary() {
  const ancient = state.datasets.ancient || [];
  const constel = state.datasets.constel || [];
  const tautou = state.datasets.tautou || [];
  const matches = Array.isArray(state.datasets.sn1054_matches) ? state.datasets.sn1054_matches : [];

  const summary = [
    { label: '古星表记录', value: ancient.length },
    { label: '星官条目', value: constel.length },
    { label: 'Tautou 目标', value: tautou.length },
    { label: 'SN1054 匹配', value: matches.length }
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
    { title: '古代星表', text: 'merged_Chinese_astronomy_data.json，已包含处理后的古天文星表与星官连线所需字段。' },
    { title: '星官参考', text: 'merged_Chinese_astronomy_data.json，按“星官”分组并生成连线。' },
    { title: '金牛座天区', text: 'clean_cols_HSCv3.1Tautou.xlsx，用于 SN 1054 目标点展示。' },
    { title: '匹配结果', text: '服务端预处理后输出的 SN1054 匹配点和统计信息。' }
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
  const labels = ['1054 / 观测切换', '1054 / 观测切换', '1054 / 观测切换', '1054 / 观测切换', '1054 / 观测切换'];
  const el = document.getElementById('timeSliderLabel');
  if (el) el.textContent = labels[state.timeIndex] || labels[4];
}

function updateMapBadge() {
  const badges = {
    combined: '全天星图 + 星官连线 + 匹配点',
    ancient: '仅全天星图',
    modern: '仅星官连线/匹配点'
  };
  document.getElementById('mapBadge').textContent = badges[state.layer] || '全天星图 + 星官连线 + 匹配点';
}

function normalizeRa(ra) {
  const value = Number(ra);
  if (!Number.isFinite(value)) return null;
  return ((value % 360) + 360) % 360;
}

function renderStarMap() {
  const catalog = state.datasets.ancient || [];
  const constellationGroups = state.datasets.constellations || [];

  const visible = catalog
    .filter(r => Number(r.mag ?? r.Vmag ?? 99) <= state.threshold)
    .slice(0, 12000)
    .map(r => ({
      x: normalizeRa(r.ra_1054 ?? r.ra_j2000 ?? r.RA ?? r.ra),
      y: Number(r.dec_1054 ?? r.dec_j2000 ?? r.Dec ?? r.dec),
      label: `HIP ${r.hip ?? r.HIP ?? 'N/A'}`,
      mag: Number(r.mag ?? r.Vmag ?? 0),
      hip: r.hip ?? r.HIP,
      ra_j2000: r.ra_j2000 ?? r.RA ?? r.ra,
      dec_j2000: r.dec_j2000 ?? r.Dec ?? r.dec,
      ra_1054: r.ra_1054 ?? r.RA ?? r.ra,
      dec_1054: r.dec_1054 ?? r.Dec ?? r.dec,
      pmra: r.pmra ?? r.pmRA ?? '-',
      pmdec: r.pmdec ?? r.pmDE ?? '-',
      rv: r.radial_velocity ?? r.RV ?? '-'
    }))
    .filter(p => Number.isFinite(p.x) && Number.isFinite(p.y));

  const lineDatasets = constellationGroups.map((group, groupIndex) => {
    const points = (group.points || [])
      .map(p => ({ x: normalizeRa(p.ra), y: Number(p.dec) }))
      .filter(p => Number.isFinite(p.x) && Number.isFinite(p.y));

    const ordered = points.length > 1 && points[0].x > points[points.length - 1].x
      ? [...points].sort((a, b) => a.x - b.x)
      : points;

    return {
      label: group.name,
      data: ordered,
      showLine: true,
      borderColor: pickGroupColor(groupIndex),
      borderWidth: group.style?.linewidth || 1.2,
      borderDash: group.style?.linestyle === '--' ? [6, 4] : [],
      pointRadius: 0,
      pointHoverRadius: 0,
      fill: false,
      tension: 0,
      order: 2
    };
  });

  const constellationPointDataset = {
    label: '星官点',
    data: (state.datasets.constel || [])
      .filter(r => Number.isFinite(Number(r.RA ?? r.ra)) && Number.isFinite(Number(r.Dec ?? r.dec)))
      .map(r => ({
        x: normalizeRa(r.RA ?? r.ra),
        y: Number(r.Dec ?? r.dec),
        label: `${r['星官'] ?? ''} ${r['中国星名'] ?? ''}`.trim(),
        hip: r.HIP ?? r.hip
      })),
    showLine: false,
    pointRadius: 2.4,
    pointBackgroundColor: '#f59e0b',
    pointBorderColor: '#ffffff',
    pointBorderWidth: 0.4,
    order: 5
  };

  const starDataset = {
    label: '古星表 (1054)',
    data: visible,
    showLine: false,
    pointRadius: ctx => Math.max(1.8, 7.5 - ctx.raw.mag / 2),
    pointBackgroundColor: ctx => ctx.raw.mag <= 6 ? '#67e8d8' : '#7aa2ff',
    pointBorderColor: 'rgba(255,255,255,0.7)',
    pointBorderWidth: 0.6,
    order: 10
  };

  const snDataset = {
    label: 'SN1054 目标点',
    data: (state.datasets.tautou || [])
      .map(p => ({ x: normalizeRa(p.ra), y: Number(p.dec), label: p.target_name || `ID ${p.match_id}` }))
      .filter(p => Number.isFinite(p.x) && Number.isFinite(p.y)),
    showLine: false,
    pointRadius: 5,
    pointBackgroundColor: '#f7c96d',
    pointBorderColor: '#ffffff',
    pointBorderWidth: 1.0,
    order: 15
  };

  const matchDataset = {
    label: 'SN1054 匹配',
    data: (state.datasets.sn1054_points || [])
      .map(p => ({ x: normalizeRa(p.ra), y: Number(p.dec), label: p.label || `HIP ${p.hip}` }))
      .filter(p => Number.isFinite(p.x) && Number.isFinite(p.y)),
    showLine: false,
    pointRadius: 7,
    pointBackgroundColor: '#f97316',
    pointBorderColor: '#ffffff',
    pointBorderWidth: 1.2,
    order: 20
  };

  const datasets = [];
  if (state.layer !== 'modern') datasets.push(...lineDatasets, constellationPointDataset, starDataset);
  if (state.layer !== 'ancient') datasets.push(snDataset, matchDataset);

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
        legend: { labels: { color: getTextColor() } },
        tooltip: {
          callbacks: {
            label: ctx => {
              const raw = ctx.raw || {};
              return `${ctx.dataset.label}: (${Number(raw.x).toFixed(2)}, ${Number(raw.y).toFixed(2)})`;
            }
          }
        }
      },
      scales: {
        x: {
          min: 360,
          max: 0,
          reverse: true,
          title: { display: true, text: 'RA (deg)', color: getTextColor() },
          ticks: { color: getTextColor() },
          grid: { color: getGridColor() }
        },
        y: { title: { display: true, text: 'Dec (deg)', color: getTextColor() }, ticks: { color: getTextColor() }, grid: { color: getGridColor() } }
      }
    })
  });
}

function renderBrightnessChart() {
  const catalog = state.datasets.ancient || [];
  const bins = [
    { label: '< 4', min: -Infinity, max: 4 },
    { label: '4 - 6', min: 4, max: 6 },
    { label: '6 - 8', min: 6, max: 8 },
    { label: '8 - 10', min: 8, max: 10 },
    { label: '> 10', min: 10, max: Infinity }
  ];
  const countBy = () => bins.map(bin => catalog.filter(r => {
    const mag = Number(r.mag ?? r.Vmag ?? r['视星等'] ?? 99);
    return mag > bin.min && mag <= bin.max;
  }).length);

  if (state.charts.brightness) state.charts.brightness.destroy();
  state.charts.brightness = new Chart(document.getElementById('brightnessChart'), {
    type: 'bar',
    data: {
      labels: bins.map(b => b.label),
      datasets: [
        { label: '古星表亮度分层', data: countBy(), backgroundColor: 'rgba(122,162,255,0.75)' }
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
