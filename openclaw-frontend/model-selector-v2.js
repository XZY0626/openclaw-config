// OpenClaw 模型选择器插件 v5
// v5: 新增MiniMax模型（MiniMax-Text-01、MiniMax-M1、MiniMax-M2.5、MiniMax-M2.5-highspeed）
(function() {
  'use strict';

  const MODELS = [
    // ===== 阿里云百炼 - 通用 =====
    { id: 'dashscope-qwen/qwen-max-latest', name: 'Qwen-Max (旗舰)', group: '阿里云·通用', alias: 'qwen-max', status: 'ok' },
    { id: 'dashscope-qwen/qwen-plus-latest', name: 'Qwen-Plus (高性能)', group: '阿里云·通用', alias: 'qwen-plus', status: 'ok' },
    { id: 'dashscope-qwen/qwen-turbo-latest', name: 'Qwen-Turbo (快速)', group: '阿里云·通用', alias: 'qwen-turbo', status: 'ok' },
    { id: 'dashscope-qwen/qwen-long', name: 'Qwen-Long (超长文本)', group: '阿里云·通用', alias: 'qwen-long', status: 'ok' },
    { id: 'dashscope-qwen/qwen-max-2025-01-25', name: 'Qwen-Max-0125 (稳定版)', group: '阿里云·通用', alias: '', status: 'ok' },
    // ===== 阿里云百炼 - 编程 =====
    { id: 'dashscope-qwen-coder/qwen2.5-coder-32b-instruct', name: 'Qwen2.5-Coder-32B', group: '阿里云·编程', alias: 'qwen-coder', status: 'ok' },
    { id: 'dashscope-qwen-coder/qwen2.5-coder-14b-instruct', name: 'Qwen2.5-Coder-14B', group: '阿里云·编程', alias: '', status: 'ok' },
    // ===== 阿里云百炼 - 推理 =====
    { id: 'dashscope-reasoning/qwq-32b', name: 'QwQ-32B', group: '阿里云·推理', alias: 'qwq', status: 'ok' },
    { id: 'dashscope-reasoning/qwen3-235b-a22b', name: 'Qwen3-235B (最强)', group: '阿里云·推理', alias: 'qwen3', status: 'ok' },
    { id: 'dashscope-reasoning/qwen3-32b', name: 'Qwen3-32B', group: '阿里云·推理', alias: '', status: 'ok' },
    // ===== 阿里云百炼 - DeepSeek =====
    { id: 'dashscope-deepseek/deepseek-r1', name: 'DeepSeek-R1', group: '阿里云·DeepSeek', alias: 'deepseek-r1', status: 'ok' },
    { id: 'dashscope-deepseek/deepseek-v3', name: 'DeepSeek-V3', group: '阿里云·DeepSeek', alias: 'deepseek-v3', status: 'ok' },
    // ===== 阿里云百炼 - 视觉 =====
    { id: 'dashscope-vision/qwen-vl-max-latest', name: 'Qwen-VL-Max', group: '阿里云·视觉', alias: 'qwen-vl', status: 'ok' },
    { id: 'dashscope-vision/qwen-vl-plus-latest', name: 'Qwen-VL-Plus', group: '阿里云·视觉', alias: '', status: 'ok' },
    { id: 'dashscope-vision/qwen2.5-vl-72b-instruct', name: 'Qwen2.5-VL-72B', group: '阿里云·视觉', alias: '', status: 'ok' },
    // ===== 阶跃星辰 =====
    { id: 'stepfun/step-2-16k', name: 'Step-2-16K (旗舰)', group: '阶跃星辰', alias: 'step-2', status: 'ok' },
    { id: 'stepfun/step-1-8k', name: 'Step-1-8K', group: '阶跃星辰', alias: 'step-1', status: 'ok' },
    { id: 'stepfun/step-1-32k', name: 'Step-1-32K', group: '阶跃星辰', alias: '', status: 'ok' },
    { id: 'stepfun/step-1-128k', name: 'Step-1-128K', group: '阶跃星辰', alias: '', status: 'ok' },
    { id: 'stepfun/step-1-256k', name: 'Step-1-256K', group: '阶跃星辰', alias: '', status: 'ok' },
    { id: 'stepfun/step-2-16k-exp', name: 'Step-2-16K-Exp', group: '阶跃星辰', alias: '', status: 'ok' },
    { id: 'stepfun/step-1v-8k', name: 'Step-1V-8K (视觉)', group: '阶跃星辰', alias: '', status: 'ok' },
    { id: 'stepfun/step-1.5v-mini', name: 'Step-1.5V-Mini (视觉)', group: '阶跃星辰', alias: '', status: 'ok' },
    // ===== 硅基流动 =====
    { id: 'siliconflow/deepseek-ai/DeepSeek-R1', name: 'DeepSeek-R1', group: '硅基流动', alias: 'sf-deepseek-r1', status: 'ok' },
    { id: 'siliconflow/deepseek-ai/DeepSeek-V3', name: 'DeepSeek-V3', group: '硅基流动', alias: 'sf-deepseek-v3', status: 'ok' },
    { id: 'siliconflow/Qwen/Qwen2.5-72B-Instruct', name: 'Qwen2.5-72B', group: '硅基流动', alias: '', status: 'ok' },
    { id: 'siliconflow/Qwen/Qwen2.5-7B-Instruct', name: 'Qwen2.5-7B (免费)', group: '硅基流动', alias: '', status: 'ok' },
    { id: 'siliconflow/THUDM/glm-4-9b-chat', name: 'GLM-4-9B (免费)', group: '硅基流动', alias: '', status: 'ok' },
    { id: 'siliconflow/internlm/internlm2_5-7b-chat', name: 'InternLM2.5-7B (免费)', group: '硅基流动', alias: '', status: 'ok' },
    // ===== OpenRouter - 免费模型 =====
    { id: 'openrouter/stepfun/step-3.5-flash:free', name: '★ Step-3.5-Flash (免费·推理·256K)', group: 'OpenRouter·免费', alias: 'step-flash', status: 'ok' },
    // ===== OpenRouter - OpenAI =====
    { id: 'openrouter/openai/gpt-4o', name: 'GPT-4o', group: 'OpenRouter·OpenAI', alias: 'gpt-4o', status: 'ok' },
    { id: 'openrouter/openai/gpt-4o-mini', name: 'GPT-4o-Mini', group: 'OpenRouter·OpenAI', alias: 'gpt-4o-mini', status: 'ok' },
    { id: 'openrouter/openai/o1', name: 'O1 (推理)', group: 'OpenRouter·OpenAI', alias: '', status: 'ok' },
    { id: 'openrouter/openai/o3-mini', name: 'O3-Mini (推理)', group: 'OpenRouter·OpenAI', alias: 'o3-mini', status: 'ok' },
    // ===== OpenRouter - Anthropic =====
    { id: 'openrouter/anthropic/claude-3.5-sonnet', name: 'Claude-3.5-Sonnet', group: 'OpenRouter·Anthropic', alias: 'claude-sonnet', status: 'ok' },
    { id: 'openrouter/anthropic/claude-3-opus', name: 'Claude-3-Opus', group: 'OpenRouter·Anthropic', alias: '', status: 'ok' },
    { id: 'openrouter/anthropic/claude-3-haiku', name: 'Claude-3-Haiku (快速)', group: 'OpenRouter·Anthropic', alias: '', status: 'ok' },
    // ===== OpenRouter - Google =====
    { id: 'openrouter/google/gemini-2.0-flash-001', name: 'Gemini-2.0-Flash', group: 'OpenRouter·Google', alias: 'gemini-flash', status: 'ok' },
    { id: 'openrouter/google/gemini-2.0-pro-exp-02-05', name: 'Gemini-2.0-Pro (实验)', group: 'OpenRouter·Google', alias: '', status: 'ok' },
    // ===== OpenRouter - Meta & Mistral =====
    { id: 'openrouter/meta-llama/llama-3.3-70b-instruct', name: 'Llama-3.3-70B', group: 'OpenRouter·Meta', alias: '', status: 'ok' },
    { id: 'openrouter/mistralai/mistral-large-2411', name: 'Mistral-Large', group: 'OpenRouter·Mistral', alias: '', status: 'ok' },
    // ===== MiniMax =====
    { id: 'minimax/MiniMax-Text-01', name: 'MiniMax-Text-01 (旗舰通用·100万上下文)', group: 'MiniMax', alias: 'minimax-text', status: 'ok' },
    { id: 'minimax/MiniMax-M1', name: 'MiniMax-M1 (推理旗舰·100万上下文)', group: 'MiniMax', alias: 'minimax-m1', status: 'ok' },
    { id: 'minimax/MiniMax-M2.5', name: '★ MiniMax-M2.5 (最新旗舰·推理)', group: 'MiniMax', alias: 'minimax', status: 'ok' },
    { id: 'minimax/MiniMax-M2.5-highspeed', name: 'MiniMax-M2.5-HighSpeed (快速·推理)', group: 'MiniMax', alias: 'minimax-fast', status: 'ok' },
  ];

  let currentModel = '';
  let panelOpen = false;

  // 通过WebSocket发送/model命令（OpenClaw原生方式）
  function sendModelViaWS(modelId) {
    // 方法1：找到OpenClaw的WebSocket连接并发送
    // 方法2：模拟在输入框输入/model命令
    const ta = findInput();
    if (ta) {
      // 清空输入框
      setInputValue(ta, '/model ' + modelId);
      // 等待一帧后按Enter
      requestAnimationFrame(() => {
        setTimeout(() => {
          // 触发Enter键
          const enterDown = new KeyboardEvent('keydown', {
            key: 'Enter', code: 'Enter', keyCode: 13, which: 13,
            bubbles: true, cancelable: true, composed: true
          });
          ta.dispatchEvent(enterDown);
          // 有些框架监听keypress
          const enterPress = new KeyboardEvent('keypress', {
            key: 'Enter', code: 'Enter', keyCode: 13, which: 13,
            bubbles: true, cancelable: true, composed: true
          });
          ta.dispatchEvent(enterPress);
          const enterUp = new KeyboardEvent('keyup', {
            key: 'Enter', code: 'Enter', keyCode: 13, which: 13,
            bubbles: true, cancelable: true, composed: true
          });
          ta.dispatchEvent(enterUp);

          // 方法3：如果上面不行，尝试找发送按钮并点击
          setTimeout(() => {
            const sendBtn = findSendButton();
            if (sendBtn) sendBtn.click();
          }, 200);
        }, 50);
      });
    } else {
      // 最后手段：提示用户手动输入
      const msg = '/model ' + modelId;
      if (navigator.clipboard) {
        navigator.clipboard.writeText(msg).then(() => {
          showToast('已复制到剪贴板，请粘贴到输入框并发送：' + msg);
        });
      } else {
        showToast('请在输入框中输入：' + msg);
      }
    }
  }

  function setInputValue(el, value) {
    // React/Vue兼容的值设置
    const proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
    const setter = Object.getOwnPropertyDescriptor(proto, 'value')?.set;
    if (setter) {
      setter.call(el, value);
    } else {
      el.value = value;
    }
    el.dispatchEvent(new Event('input', { bubbles: true, composed: true }));
    el.dispatchEvent(new Event('change', { bubbles: true, composed: true }));
  }

  // 深度搜索输入框（包括Shadow DOM）
  function findInput() {
    // 常规DOM
    let el = document.querySelector('textarea') || document.querySelector('input[type="text"]');
    if (el) return el;
    // Shadow DOM
    const all = document.querySelectorAll('*');
    for (const e of all) {
      if (e.shadowRoot) {
        el = e.shadowRoot.querySelector('textarea') || e.shadowRoot.querySelector('input[type="text"]');
        if (el) return el;
        // 二级Shadow DOM
        const inner = e.shadowRoot.querySelectorAll('*');
        for (const ie of inner) {
          if (ie.shadowRoot) {
            el = ie.shadowRoot.querySelector('textarea') || ie.shadowRoot.querySelector('input[type="text"]');
            if (el) return el;
          }
        }
      }
    }
    return null;
  }

  function findSendButton() {
    // 找发送按钮
    const btns = document.querySelectorAll('button');
    for (const b of btns) {
      const text = (b.textContent || '').toLowerCase();
      const aria = (b.getAttribute('aria-label') || '').toLowerCase();
      if (text.includes('send') || text.includes('发送') || aria.includes('send')) return b;
    }
    // Shadow DOM
    const all = document.querySelectorAll('*');
    for (const e of all) {
      if (e.shadowRoot) {
        const sbtns = e.shadowRoot.querySelectorAll('button');
        for (const b of sbtns) {
          const text = (b.textContent || '').toLowerCase();
          if (text.includes('send') || text.includes('发送')) return b;
        }
      }
    }
    return null;
  }

  function showToast(msg) {
    const toast = document.createElement('div');
    Object.assign(toast.style, {
      position: 'fixed', bottom: '200px', right: '24px', zIndex: '9999999',
      padding: '12px 20px', borderRadius: '8px',
      background: '#333', color: '#fff', fontSize: '13px',
      boxShadow: '0 4px 12px rgba(0,0,0,0.3)', maxWidth: '350px',
      transition: 'opacity 0.3s'
    });
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 300); }, 4000);
  }

  function selectModel(modelId, status) {
    if (status === 'key_invalid') {
      showToast('⚠️ OpenRouter API Key已失效，请更新后再使用此模型');
      return;
    }
    sendModelViaWS(modelId);
    currentModel = modelId;
    updateBadge();
    togglePanel(false);
    showToast('✅ 模型已切换为: ' + modelId);
  }

  function updateBadge() {
    const badge = document.getElementById('oc-ms-badge');
    if (badge) {
      const m = MODELS.find(m => m.id === currentModel);
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
      ? MODELS.filter(m => m.name.toLowerCase().includes(lf) || m.id.toLowerCase().includes(lf) || m.group.toLowerCase().includes(lf) || (m.alias && m.alias.toLowerCase().includes(lf)))
      : MODELS;

    if (!filtered.length) {
      list.innerHTML = '<div style="padding:20px;text-align:center;color:#888;font-size:13px">未找到匹配的模型</div>';
      return;
    }

    const groups = {};
    filtered.forEach(m => { if (!groups[m.group]) groups[m.group] = []; groups[m.group].push(m); });

    let html = '';
    const okCount = MODELS.filter(m => m.status === 'ok').length;
    const badCount = MODELS.filter(m => m.status !== 'ok').length;

    for (const [g, ms] of Object.entries(groups)) {
      const isWarning = g.includes('⚠️');
      const groupColor = isWarning ? '#f59e0b' : '#888';
      html += '<div style="padding:8px 16px 4px;font-size:11px;font-weight:700;color:' + groupColor + ';text-transform:uppercase;letter-spacing:0.5px;position:sticky;top:0;background:#1e1e2e">' + g + '</div>';
      ms.forEach(m => {
        const active = m.id === currentModel ? 'background:rgba(99,102,241,0.25);border-left:3px solid #6366f1;' : '';
        const disabled = m.status !== 'ok';
        const opacity = disabled ? 'opacity:0.5;' : '';
        const cursor = disabled ? 'cursor:not-allowed;' : 'cursor:pointer;';
        const aliasHtml = m.alias ? '<span style="font-size:10px;color:#888;margin-left:8px;flex-shrink:0">' + m.alias + '</span>' : '';
        const statusIcon = disabled ? '<span style="font-size:10px;color:#f59e0b;margin-left:4px" title="API Key无效">⚠️</span>' : '';
        html += '<div class="oc-ms-item" data-mid="' + m.id + '" data-status="' + m.status + '" style="padding:8px 16px;display:flex;align-items:center;justify-content:space-between;font-size:13px;color:#e0e0e0;transition:background 0.15s;' + active + opacity + cursor + '">'
          + '<span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">' + m.name + statusIcon + '</span>'
          + aliasHtml + '</div>';
      });
    }
    list.innerHTML = html;

    list.querySelectorAll('.oc-ms-item').forEach(el => {
      const status = el.dataset.status;
      if (status === 'ok') {
        el.addEventListener('mouseenter', () => { el.style.background = 'rgba(99,102,241,0.15)'; });
        el.addEventListener('mouseleave', () => { el.style.background = el.dataset.mid === currentModel ? 'rgba(99,102,241,0.25)' : ''; });
      }
      el.addEventListener('click', () => selectModel(el.dataset.mid, el.dataset.status));
    });
  }

  function createUI() {
    const okCount = MODELS.filter(m => m.status === 'ok').length;

    // 浮动按钮
    const btn = document.createElement('div');
    btn.id = 'oc-ms-btn';
    btn.innerHTML = '\u{1F916}';
    btn.title = '切换AI模型 (' + okCount + '个可用)';
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
      width: '420px', maxHeight: '560px',
      background: '#1e1e2e', border: '1px solid #333', borderRadius: '12px',
      boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
      flexDirection: 'column', overflow: 'hidden',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    });
    panel.innerHTML = ''
      + '<div style="padding:14px 16px;border-bottom:1px solid #333;display:flex;align-items:center;justify-content:space-between">'
      + '  <span style="font-size:15px;font-weight:600;color:#e0e0e0">\u{1F504} 切换模型</span>'
      + '  <span id="oc-ms-badge" style="font-size:11px;padding:3px 8px;border-radius:6px;background:rgba(99,102,241,0.2);color:#a5b4fc;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">默认</span>'
      + '</div>'
      + '<input id="oc-ms-search" type="text" placeholder="\u{1F50D} 搜索模型名称、平台或别名..." style="width:100%;padding:10px 16px;border:none;border-bottom:1px solid #333;background:#2a2a3e;color:#e0e0e0;font-size:13px;outline:none;box-sizing:border-box" />'
      + '<div id="oc-ms-list" style="overflow-y:auto;flex:1;max-height:400px;padding:4px 0"></div>'
      + '<div style="padding:8px 16px;border-top:1px solid #333;font-size:11px;color:#666;text-align:center">'
      + okCount + ' 个可用 | 点击选择即可切换</div>';
    document.body.appendChild(panel);

    document.getElementById('oc-ms-search').addEventListener('input', (e) => renderList(e.target.value));
    document.addEventListener('click', (e) => {
      if (panelOpen && !panel.contains(e.target) && e.target !== btn && !btn.contains(e.target)) togglePanel(false);
    });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && panelOpen) togglePanel(false); });

    renderList('');
    console.log('[ModelSelector] v4 loaded -', okCount, 'models available');
  }

  if (document.body) setTimeout(createUI, 2000);
  else document.addEventListener('DOMContentLoaded', () => setTimeout(createUI, 2000));
})();
