// 论点验证 - 前端逻辑

const state = {
  currentClaim: null,
  currentResult: null,
  isAnalyzing: false,
  history: JSON.parse(localStorage.getItem('claim_history') || '[]')
};

// DOM 元素
const claimInput = document.getElementById('claim-input');
const charCurrent = document.getElementById('char-current');
const timeWindow = document.getElementById('time-window');
const customDates = document.getElementById('custom-dates');
const dateStart = document.getElementById('date-start');
const dateEnd = document.getElementById('date-end');
const llmModel = document.getElementById('llm-model');
const verifyBtn = document.getElementById('verify-btn');
const loadingSection = document.getElementById('loading-section');
const loadingText = document.getElementById('loading-text');
const resultSection = document.getElementById('result-section');
const verdictCard = document.getElementById('verdict-card');
const verdictIcon = document.getElementById('verdict-icon');
const verdictTitle = document.getElementById('verdict-title');
const verdictConfidence = document.getElementById('verdict-confidence');
const confidenceFill = document.getElementById('confidence-fill');
const verdictReasoning = document.getElementById('verdict-reasoning');
const evidenceSummary = document.getElementById('evidence-summary');
const evidenceList = document.getElementById('evidence-list');
const historyList = document.getElementById('history-list');

// 初始化
function init() {
  bindEvents();
  renderHistory();
}

// 绑定事件
function bindEvents() {
  verifyBtn.addEventListener('click', handleVerify);

  claimInput.addEventListener('input', () => {
    charCurrent.textContent = claimInput.value.length;
  });

  timeWindow.addEventListener('change', (e) => {
    if (e.target.value === 'custom') {
      customDates.style.display = 'flex';
    } else {
      customDates.style.display = 'none';
    }
  });

  document.getElementById('reanalyze-btn')?.addEventListener('click', handleVerify);
  document.getElementById('save-btn')?.addEventListener('click', handleSave);
  document.getElementById('publish-btn')?.addEventListener('click', handlePublish);
}

// 处理验证
async function handleVerify() {
  const claim = claimInput.value.trim();

  if (!claim) {
    alert('请输入论点');
    return;
  }

  if (claim.length < 5) {
    alert('论点太短，请至少输入 5 个字符');
    return;
  }

  state.currentClaim = claim;
  state.isAnalyzing = true;

  // 显示加载状态
  showLoading();

  // 获取参数
  const params = {
    claim: claim,
    timeWindow: timeWindow.value === 'custom'
      ? getCustomDays()
      : parseInt(timeWindow.value),
    model: llmModel.value
  };

  try {
    // 调用后端 API
    const result = await callVerifyAPI(params);

    state.currentResult = result;

    // 显示结果
    showResult(result);

    // 保存到历史
    saveToHistory(result);

  } catch (error) {
    console.error('验证失败:', error);
    alert('验证失败: ' + error.message);
    hideLoading();
  }

  state.isAnalyzing = false;
}

// 计算自定义天数
function getCustomDays() {
  const start = new Date(dateStart.value);
  const end = new Date(dateEnd.value);
  const diff = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
  return diff > 0 ? diff : 7;
}

// 调用验证 API
async function callVerifyAPI(params) {
  const response = await fetch('/api/verify-claim', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      claim: params.claim,
      time_window: params.timeWindow,
      min_confidence: 0,
      llm_model: params.model
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '请求失败');
  }

  return await response.json();
}

// 显示加载状态
function showLoading() {
  loadingSection.classList.remove('hidden');
  resultSection.classList.add('hidden');
  verifyBtn.disabled = true;

  // 模拟进度
  updateLoadingProgress();
}

// 更新加载进度
function updateLoadingProgress() {
  const steps = document.querySelectorAll('.step');
  let current = 0;

  const interval = setInterval(() => {
    steps.forEach((step, index) => {
      step.classList.remove('active');
      if (index <= current) {
        step.classList.add('active');
      }
    });

    current++;
    if (current >= 4) {
      clearInterval(interval);
    }
  }, 500);
}

// 隐藏加载状态
function hideLoading() {
  loadingSection.classList.add('hidden');
  verifyBtn.disabled = false;
}

// 显示结果
function showResult(result) {
  hideLoading();
  resultSection.classList.remove('hidden');

  // 更新结论卡片
  updateVerdictCard(result);

  // 更新证据摘要
  document.getElementById('count-supporting').textContent =
    result.stats.supporting_count;
  document.getElementById('count-refuting').textContent =
    result.stats.refuting_count;
  document.getElementById('count-neutral').textContent =
    result.stats.neutral_count;

  // 渲染证据列表
  renderEvidenceList(result.evidence);

  // 滚动到结果区
  resultSection.scrollIntoView({ behavior: 'smooth' });
}

// 更新结论卡片
function updateVerdictCard(result) {
  // 移除旧类
  verdictCard.classList.remove('verdict-supported', 'verdict-refuted', 'verdict-inconclusive');

  // 添加新类
  const verdictClass = 'verdict-' + result.verdict.toLowerCase();
  verdictCard.classList.add(verdictClass);

  // 更新图标
  const icons = {
    'SUPPORTED': '✓',
    'REFUTED': '✗',
    'INCONCLUSIVE': '?'
  };
  verdictIcon.textContent = icons[result.verdict] || '?';

  // 更新标题
  const titles = {
    'SUPPORTED': '高度可能',
    'REFUTED': '证伪',
    'INCONCLUSIVE': '无法判断'
  };
  verdictTitle.textContent = titles[result.verdict] || '未知';

  // 更新置信度
  verdictConfidence.textContent = `置信度: ${result.confidence}%`;
  confidenceFill.style.width = `${result.confidence}%`;

  // 更新推理
  verdictReasoning.textContent = result.reasoning;
}

// 渲染证据列表
function renderEvidenceList(evidence) {
  evidenceList.innerHTML = '';

  const allEvidence = [
    ...evidence.supporting.map(e => ({...e, type: 'supporting'})),
    ...evidence.refuting.map(e => ({...e, type: 'refuting'})),
    ...evidence.neutral.slice(0, 5).map(e => ({...e, type: 'neutral'}))
  ];

  allEvidence.forEach(item => {
    const card = createEvidenceCard(item);
    evidenceList.appendChild(card);
  });
}

// 创建证据卡片
function createEvidenceCard(evidence) {
  const div = document.createElement('div');
  div.className = `evidence-card type-${evidence.type}`;

  const date = new Date(evidence.published_at);
  const dateStr = date.toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });

  const sourceTypeLabels = {
    'official': '⭐ 官方',
    'media': '📰 媒体',
    'social': '🐦 社交',
    'analyst': '📊 分析师',
    'community': '💬 社区'
  };

  div.innerHTML = `
    <h4>${evidence.title}</h4>
    <div class="evidence-meta">
      <span>${sourceTypeLabels[evidence.source_type] || evidence.source}</span>
      <span>${dateStr}</span>
    </div>
    <p class="evidence-summary-text">${evidence.summary || '无摘要'}</p>
    <div class="evidence-actions">
      <a href="${evidence.url}" target="_blank">查看原文 →</a>
    </div>
  `;

  return div;
}

// 保存到历史
function saveToHistory(result) {
  const historyItem = {
    id: Date.now().toString(),
    claim: state.currentClaim,
    verdict: result.verdict,
    confidence: result.confidence,
    createdAt: new Date().toISOString()
  };

  state.history.unshift(historyItem);

  // 只保留最近 20 条
  if (state.history.length > 20) {
    state.history = state.history.slice(0, 20);
  }

  // 保存到 localStorage
  localStorage.setItem('claim_history', JSON.stringify(state.history));

  // 重新渲染历史
  renderHistory();
}

// 渲染历史记录
function renderHistory() {
  if (state.history.length === 0) {
    historyList.innerHTML = '<p class="empty-state">暂无历史记录</p>';
    return;
  }

  historyList.innerHTML = '';

  state.history.forEach(item => {
    const div = document.createElement('div');
    div.className = 'history-item';

    const verdictLabels = {
      'SUPPORTED': '✓ 证明',
      'REFUTED': '✗ 证伪',
      'INCONCLUSIVE': '? 无法判断'
    };

    const date = new Date(item.createdAt);
    const dateStr = date.toLocaleDateString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });

    div.innerHTML = `
      <h4>${item.claim}</h4>
      <div class="meta">
        <span>${verdictLabels[item.verdict]}</span>
        <span>置信度: ${item.confidence}%</span>
        <span>${dateStr}</span>
      </div>
    `;

    div.addEventListener('click', () => {
      loadHistoryItem(item);
    });

    historyList.appendChild(div);
  });
}

// 加载历史项
function loadHistoryItem(item) {
  claimInput.value = item.claim;
  charCurrent.textContent = item.claim.length;

  // TODO: 从存储的完整结果中恢复
  alert('加载历史记录功能开发中...\n\n论点: ' + item.claim);
}

// 处理保存
function handleSave() {
  if (!state.currentResult) {
    alert('没有可保存的结果');
    return;
  }

  // TODO: 实现保存功能（收藏到数据库）
  alert('保存功能开发中...');
}

// 处理发布到博客
async function handlePublish() {
  if (!state.currentResult) {
    alert('没有可发布的结果');
    return;
  }

  const confirmed = confirm(
    '确定要发布到你的 GitHub 博客吗？\n\n' +
    '仓库: soar4ever/blog-test\n' +
    '论点: ' + state.currentClaim
  );

  if (!confirmed) return;

  try {
    // TODO: 实现实际的博客发布逻辑
    alert('博客发布功能开发中...\n\n将生成 Markdown 文件并提交到你的博客仓库。');
  } catch (error) {
    alert('发布失败: ' + error.message);
  }
}

// 页面加载完成后初始化
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
