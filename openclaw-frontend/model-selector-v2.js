// OpenClaw 模型选择器插件 v2
// 兼容Shadow DOM，独立于OpenClaw组件树
(function() {
  'use strict';

  const FALLBACK_MODELS = [
    { id: 'dashscope-qwen/qwen-max-latest', name: 'Qwen-Max', group: '阿里云·通用', alias: 'qwen-max' },
    { id: 'dashscope-qwen/qwen-plus-latest', name: 'Qwen-Plus', group: '阿里云·通用', alias: 'qwen-plus' },
    { id: 'dashscope-qwen/qwen-turbo-latest', name: 'Qwen-Turbo', group: '阿里云·通用', alias: 'qwen-turbo' },
    { id: 'dashscope-qwen/qwen-long', name: 'Qwen-Long (超长文本)', group: '阿里云·通用', alias: 'qwen-long' },
    { id: 'dashscope-qwen/qwen-max-2025-01-25', name: 'Qwen-Max-0125 (稳定版)', group: '阿里云·通用', alias: '' },
    { id: 'dashscope-qwen-coder/qwen2.5-coder-32b-instruct', name: 'Qwen2.5-Coder-32B', group: '阿里云·编程', alias: 'qwen-coder' },
    { id: 'dashscope-qwen-coder/qwen2.5-coder-14b-instruct', name: 'Qwen2.5-Coder-14B', group: '阿里云·编程', alias: '' },
    { id: 'dashscope-reasoning/qwq-32b', name: 'QwQ-32B', group: '阿里云·推理', alias: 'qwq' },
    { id: 'dashscope-reasoning/qwen3-235b-a22b', name: 'Qwen3-235B (最强)', group: '阿里云·推理', alias: 'qwen3' },
    { id: 'dashscope-reasoning/qwen3-32b', name: 'Qwen3-32B', group: '阿里云·推理', alias: '' },
    { id: 'dashscope-deepseek/deepseek-r1', name: 'DeepSeek-R1', group: '阿里云·DeepSeek', alias: 'deepseek-r1' },
    { id: 'dashscope-deepseek/deepseek-v3', name: 'DeepSeek-V3', group: '阿里云·DeepSeek', alias: 'deepseek-v3' },
    { id: 'dashscope-vision/qwen-vl-max-latest', name: 'Qwen-VL-Max', group: '阿里云·视觉', alias: 'qwen-vl' },
    { id: 'dashscope-vision/qwen-vl-plus-latest', name: 'Qwen-VL-Plus', group: '阿里云·视觉', alias: '' },
    { id: 'dashscope-vision/qwen2.5-vl-72b-instruct', name: 'Qwen2.5-VL-72B', group: '阿里云·视觉', alias: '' },
    { id: 'stepfun/step-2-16k', name: 'Step-2-16K (旗舰)', group: '阶跃星辰', alias: 'step-2' },
    { id: 'stepfun/step-1-8k', name: 'Step-1-8K', group: '阶跃星辰', alias: 'step-1' },
    { id: 'stepfun/step-1-32k', name: 'Step-1-32K', group: '阶跃星辰', alias: '' },
    { id: 'stepfun/step-1-128k', name: 'Step-1-128K', group: '阶跃星辰', alias: '' },
    { id: 'stepfun/step-1-256k', name: 'Step-1-256K', group: '阶跃星辰', alias: '' },
    { id: 'stepfun/step-2-16k-exp', name: 'Step-2-16K-Exp', group: '阶跃星辰', alias: '' },
    { id: 'stepfun/step-1v-8k', name: 'Step-1V-8K (视觉)', group: '阶跃星辰', alias: '' },
    { id: 'stepfun/step-1.5v-mini', name: 'Step-1.5V-Mini (视觉)', group: '阶跃星辰', alias: '' },
    { id: 'siliconflow/deepseek-ai/DeepSeek-R1', name: 'DeepSeek-R1', group: '硅基流动', alias: 'sf-deepseek-r1' },
    { id: 'siliconflow/deepseek-ai/DeepSeek-V3', name: 'DeepSeek-V3', group: '硅基流动', alias: 'sf-deepseek-v3' },
    { id: 'siliconflow/Qwen/Qwen2.5-72B-Instruct', name: 'Qwen2.5-72B', group: '硅基流动', alias: '' },
    { id: 'siliconflow/Qwen/Qwen2.5-7B-Instruct', name: 'Qwen2.5-7B (免费)', group: '硅基流动', alias: '' },
    { id: 'siliconflow/THUDM/glm-4-9b-chat', name: 'GLM-4-9B (免费)', group: '硅基流动', alias: '' },
    { id: 'siliconflow/internlm/internlm2_5-7b-chat', name: 'InternLM2.5-7B (免费)', group: '硅基流动', alias: '' },
    { id: 'openrouter/openai/gpt-4o', name: 'GPT-4o', group: 'OpenRouter·OpenAI', alias: 'gpt-4o' },
    { id: 'openrouter/openai/gpt-4o-mini', name: 'GPT-4o-Mini', group: 'OpenRouter·OpenAI', alias: 'gpt-4o-mini' },
    { id: 'openrouter/openai/o1', name: 'O1 (推理)', group: 'OpenRouter·OpenAI', alias: '' },
    { id: 'openrouter/openai/o3-mini', name: 'O3-Mini (推理)', group: 'OpenRouter·OpenAI', alias: 'o3-mini' },
    { id: 'openrouter/anthropic/claude-3.5-sonnet', name: 'Claude-3.5-Sonnet', group: 'OpenRouter·Anthropic', alias: 'claude-sonnet' },
    { id: 'openrouter/anthropic/claude-3-opus', name: 'Claude-3-Opus', group: 'OpenRouter·Anthropic', alias: '' },
    { id: 'openrouter/anthropic/claude-3-haiku', name: 'Claude-3-Haiku (快速)', group: 'OpenRouter·Anthropic', alias: '' },
    { id: 'openrouter/google/gemini-2.0-flash-001', name: 'Gemini-2.0-Flash', group: 'OpenRouter·Google', alias: 'gemini-flash' },
    { id: 'openrouter/google/gemini-2.0-pro-exp-02-05', name: 'Gemini-2.0-Pro (实验)', group: 'OpenRouter·Google', alias: '' },
    { id: 'openrouter/meta-llama/llama-3.3-70b-instruct', name: 'Llama-3.3-70B', group: 'OpenRouter·Meta', alias: '' },
    { id: 'openrouter/mistralai/mistral-large-2411', name: 'Mistral-Large', group: 'OpenRouter·Mistral', alias: '' },
  ];

  let currentModel = '';
  let panelOpen = false;

  // 深度搜索textarea（包括Shadow DOM）
  function deepQuerySelector(root, selector) {
    let el = root.querySelector(selector);
    if (el) return el;
    const allEls = root.querySelectorAll('*');
    for (const e of allEls) {
      if (e.shadowRoot) {
        el = deepQuerySelector(e.shadowRoot, selector);
        if (el) return el;
      }
    }
    return null;
  }

  function findTextarea() {
    // 先在document中找
    let ta = document.querySelector('textarea');
    if (ta) return ta;
    // 在Shadow DOM中找
    ta = deepQuerySelector(document, 'textarea');
    if (ta) return ta;
    // 尝试input
    ta = deepQuerySelector(document, 'input[type="text"]');
    return ta;
  }

  function sendModelCommand(modelId) {
    const ta = findTextarea();
    if (ta) {
      const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value')?.set
        || Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set;
      if (setter) setter.call(ta, '/model ' + modelId);
      else ta.value = '/model ' + modelId;
      ta.dispatchEvent(new Event('input', { bubbles: true, composed: true }));
      setTimeout(() => {
        ta.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true, composed: true }));
        ta.dispatchEvent(new KeyboardEvent('keyup', { key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true, composed: true }));
      }, 150);
    } else {
      alert('提示：请在聊天输入框中手动输入：/model ' + modelId);
    }
    currentModel = modelId;
    updateBadge();
    togglePanel(false);
  }

  function updateBadge() {
    const badge = document.getElementById('oc-ms-badge');
    if (badge) {
      const m = FALLBACK_MODELS.find(m => m.id === currentModel);
      badge.textContent = m ? m.name : (currentModel || '默认');
    }
  }

  function togglePanel(force) {
    panelOpen = force !== undefined ? force : !panelOpen;
    const panel = document.getElementById('oc-ms-panel');
    if (panel) {
      panel.style.display = panelOpen ? 'flex' : 'none';
      if (panelOpen) {
        const s = document.getElementById('oc-ms-search');
        if (s) { s.value = ''; s.focus(); }
        renderList('');
      }
    }
  }

  function renderList(filter) {
    const list = document.getElementById('oc-ms-list');
    if (!list) return;
    const lf = (filter || '').toLowerCase();
    const filtered = lf
      ? FALLBACK_MODELS.filter(m => m.name.toLowerCase().includes(lf) || m.id.toLowerCase().includes(lf) || m.group.toLowerCase().includes(lf) || (m.alias && m.alias.toLowerCase().includes(lf)))
      : FALLBACK_MODELS;

    if (!filtered.length) { list.innerHTML = '<div style="padding:20px;text-align:center;color:#888;font-size:13px">未找到匹配的模型</div>'; return; }

    const groups = {};
    filtered.forEach(m => { if (!groups[m.group]) groups[m.group] = []; groups[m.group].push(m); });

    let html = '';
    for (const [g, ms] of Object.entries(groups)) {
      html += '<div style="padding:8px 16px 4px;font-size:11px;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:0.5px;position:sticky;top:0;background:#1e1e2e">' + g + '</div>';
      ms.forEach(m => {
        const active = m.id === currentModel ? 'background:rgba(99,102,241,0.25);border-left:3px solid #6366f1;' : '';
        const aliasHtml = m.alias ? '<span style="font-size:10px;color:#888;margin-left:8px;flex-shrink:0">' + m.alias + '</span>' : '';
        html += '<div class="oc-ms-item" data-mid="' + m.id + '" style="padding:8px 16px;cursor:pointer;display:flex;align-items:center;justify-content:space-between;font-size:13px;color:#e0e0e0;transition:background 0.15s;' + active + '">'
          + '<span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">' + m.name + '</span>'
          + aliasHtml + '</div>';
      });
    }
    list.innerHTML = html;
    list.querySelectorAll('.oc-ms-item').forEach(el => {
      el.addEventListener('mouseenter', () => { el.style.background = 'rgba(99,102,241,0.15)'; });
      el.addEventListener('mouseleave', () => { el.style.background = el.dataset.mid === currentModel ? 'rgba(99,102,241,0.25)' : ''; });
      el.addEventListener('click', () => sendModelCommand(el.dataset.mid));
    });
  }

  function createUI() {
    // 浮动按钮
    const btn = document.createElement('div');
    btn.id = 'oc-ms-btn';
    btn.innerHTML = '\u{1F916}';
    btn.title = '切换AI模型';
    Object.assign(btn.style, {
      position: 'fixed', bottom: '80px', right: '24px', zIndex: '999999',
      width: '52px', height: '52px', borderRadius: '50%',
      background: 'linear-gradient(135deg, #4f46e5, #7c3aed)',
      border: '2px solid rgba(99,102,241,0.6)',
      color: 'white', cursor: 'pointer',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontSize: '24px', boxShadow: '0 4px 15px rgba(79,70,229,0.4)',
      transition: 'all 0.3s ease', userSelect: 'none'
    });
    btn.addEventListener('mouseenter', () => { btn.style.transform = 'scale(1.1)'; btn.style.boxShadow = '0 6px 20px rgba(79,70,229,0.6)'; });
    btn.addEventListener('mouseleave', () => { btn.style.transform = 'scale(1)'; btn.style.boxShadow = '0 4px 15px rgba(79,70,229,0.4)'; });
    btn.addEventListener('click', (e) => { e.stopPropagation(); togglePanel(); });
    document.body.appendChild(btn);

    // 面板
    const panel = document.createElement('div');
    panel.id = 'oc-ms-panel';
    Object.assign(panel.style, {
      display: 'none', position: 'fixed', bottom: '140px', right: '24px', zIndex: '999998',
      width: '400px', maxHeight: '520px',
      background: '#1e1e2e', border: '1px solid #333', borderRadius: '12px',
      boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
      flexDirection: 'column', overflow: 'hidden',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    });
    panel.innerHTML = ''
      + '<div style="padding:14px 16px;border-bottom:1px solid #333;display:flex;align-items:center;justify-content:space-between">'
      + '  <span style="font-size:15px;font-weight:600;color:#e0e0e0">\u{1F504} 切换模型</span>'
      + '  <span id="oc-ms-badge" style="font-size:11px;padding:3px 8px;border-radius:6px;background:rgba(99,102,241,0.2);color:#a5b4fc;max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">默认</span>'
      + '</div>'
      + '<input id="oc-ms-search" type="text" placeholder="\u{1F50D} 搜索模型名称、平台或别名..." style="width:100%;padding:10px 16px;border:none;border-bottom:1px solid #333;background:#2a2a3e;color:#e0e0e0;font-size:13px;outline:none;box-sizing:border-box" />'
      + '<div id="oc-ms-list" style="overflow-y:auto;flex:1;max-height:380px;padding:4px 0"></div>'
      + '<div style="padding:8px 16px;border-top:1px solid #333;font-size:11px;color:#666;text-align:center">共 ' + FALLBACK_MODELS.length + ' 个模型 | 点击选择即可切换</div>';
    document.body.appendChild(panel);

    // 搜索
    document.getElementById('oc-ms-search').addEventListener('input', (e) => renderList(e.target.value));

    // 点击外部关闭
    document.addEventListener('click', (e) => {
      if (panelOpen && !panel.contains(e.target) && e.target !== btn && !btn.contains(e.target)) {
        togglePanel(false);
      }
    });

    // ESC关闭
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && panelOpen) togglePanel(false); });

    renderList('');
    console.log('[ModelSelector] v2 已加载，共', FALLBACK_MODELS.length, '个模型');
  }

  // 等待页面完全加载后初始化
  function waitAndInit() {
    if (document.body) {
      setTimeout(createUI, 2000);
    } else {
      document.addEventListener('DOMContentLoaded', () => setTimeout(createUI, 2000));
    }
  }

  waitAndInit();
})();
