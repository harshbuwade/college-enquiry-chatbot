/* ═══════════════════════════════════════════════════════════════════════════
   College Enquiry Chatbot — script.js
   ═══════════════════════════════════════════════════════════════════════════ */

'use strict';

// ── Config ─────────────────────────────────────────────────────────────────
// Auto-detect: use localhost when running locally, Render URL in production
const IS_LOCAL = ['localhost', '127.0.0.1', ''].includes(window.location.hostname);
const API_URL  = IS_LOCAL
  ? 'http://127.0.0.1:5000'
  : 'https://college-enquiry-chatbot-1-enxg.onrender.com';

// ── DOM refs ────────────────────────────────────────────────────────────────
const chatMessages   = document.getElementById('chatMessages');
const userInput      = document.getElementById('userInput');
const sendBtn        = document.getElementById('sendBtn');
const typingWrapper  = document.getElementById('typingWrapper');
const themeToggle    = document.getElementById('themeToggle');
const clearChat      = document.getElementById('clearChat');
const historyBtn     = document.getElementById('historyBtn');
const hamburgerBtn   = document.getElementById('hamburgerBtn');
const sidebar        = document.getElementById('sidebar');
const sidebarClose   = document.getElementById('sidebarClose');
const charCount      = document.getElementById('charCount');
const statusText     = document.getElementById('statusText');
const toastContainer = document.getElementById('toastContainer');

// ── State ───────────────────────────────────────────────────────────────────
let isDarkMode       = localStorage.getItem('darkMode') === 'true';
let isWaiting        = false;    // prevent double-sends
let sidebarOpen      = false;

// ── Init ────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  applyTheme();
  attachEventListeners();
  checkBackendHealth();
});

// ── Theme ────────────────────────────────────────────────────────────────────
function applyTheme() {
  document.body.classList.toggle('dark', isDarkMode);
  themeToggle.innerHTML = isDarkMode
    ? '<i class="fas fa-sun"></i>'
    : '<i class="fas fa-moon"></i>';
  themeToggle.title = isDarkMode ? 'Switch to light mode' : 'Switch to dark mode';
}

function toggleTheme() {
  isDarkMode = !isDarkMode;
  localStorage.setItem('darkMode', isDarkMode);
  applyTheme();
  showToast(isDarkMode ? '🌙 Dark mode on' : '☀️ Light mode on', 'info');
}

// ── Event listeners ──────────────────────────────────────────────────────────
function attachEventListeners() {
  // Send
  sendBtn.addEventListener('click', sendMessage);
  userInput.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!sendBtn.disabled) sendMessage();
    }
  });

  // Input state
  userInput.addEventListener('input', () => {
    const len = userInput.value.length;
    const hasText = userInput.value.trim().length > 0;
    sendBtn.disabled = !hasText || isWaiting;
    charCount.textContent = `${len}/500`;
    charCount.style.color = len > 450 ? 'var(--danger)' : '';
    autoResize();
  });

  // Header buttons
  themeToggle.addEventListener('click', toggleTheme);
  clearChat.addEventListener('click', confirmClear);
  historyBtn.addEventListener('click', loadHistory);

  // Sidebar
  hamburgerBtn.addEventListener('click', openSidebar);
  sidebarClose.addEventListener('click', closeSidebar);

  // Nav items in sidebar
  document.querySelectorAll('.nav-item').forEach(btn => {
    btn.addEventListener('click', () => {
      const q = btn.dataset.query;
      if (q) triggerQuery(q);
      document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      if (window.innerWidth <= 768) closeSidebar();
    });
  });

  // Quick chips in welcome message (event delegation)
  chatMessages.addEventListener('click', e => {
    const chip = e.target.closest('.chip');
    if (chip && chip.dataset.query) {
      triggerQuery(chip.dataset.query);
    }
  });

  // Sidebar overlay (mobile)
  document.addEventListener('click', e => {
    if (sidebarOpen && !sidebar.contains(e.target) && e.target !== hamburgerBtn) {
      closeSidebar();
    }
  });
}

function autoResize() {
  userInput.style.height = 'auto';
  userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
}

// ── Sidebar ──────────────────────────────────────────────────────────────────
function openSidebar() {
  sidebar.classList.add('open');
  sidebarOpen = true;
  // Overlay
  let overlay = document.querySelector('.sidebar-overlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';
    overlay.addEventListener('click', closeSidebar);
    document.body.appendChild(overlay);
  }
  overlay.classList.add('visible');
}

function closeSidebar() {
  sidebar.classList.remove('open');
  sidebarOpen = false;
  const overlay = document.querySelector('.sidebar-overlay');
  if (overlay) overlay.classList.remove('visible');
}

// ── Trigger a query programmatically ─────────────────────────────────────────
function triggerQuery(text) {
  userInput.value = text;
  userInput.dispatchEvent(new Event('input'));
  sendMessage();
}

// ── Send message ──────────────────────────────────────────────────────────────
async function sendMessage() {
  const msg = userInput.value.trim();
  if (!msg || isWaiting) return;

  isWaiting = true;
  sendBtn.disabled = true;
  userInput.value = '';
  charCount.textContent = '0/500';
  autoResize();

  appendMessage(msg, 'user');
  showTyping();

  try {
    const res = await fetch(`${API_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg }),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    hideTyping();
    setTimeout(() => appendMessage(data.response, 'bot', data), 150);

  } catch (err) {
    hideTyping();
    console.error('Chat error:', err);
    appendMessage(
      '⚠️ Unable to reach the server. Please check your connection or try again later.',
      'bot',
      null,
      true  // isError
    );
    showToast('Connection error — backend may be sleeping (Render free tier)', 'error');
  } finally {
    isWaiting = false;
    sendBtn.disabled = userInput.value.trim().length === 0;
  }
}

// ── Append message to DOM ─────────────────────────────────────────────────────
function appendMessage(text, sender, meta = null, isError = false) {
  const wrap = document.createElement('div');
  wrap.className = `message ${sender}`;

  const time = formatTime(new Date());
  const formattedHTML = formatResponse(text);
  const intentBadge = (meta && meta.intent && meta.intent !== 'unknown' && sender === 'bot')
    ? `<span class="intent-badge">${meta.intent.replace(/_/g, ' ')}</span>`
    : '';

  const avatarIcon = sender === 'bot' ? 'fa-robot' : 'fa-user';
  const avatarClass = sender === 'bot' ? 'bot-av' : 'user-av';
  const bubbleClass = sender === 'bot' ? 'bot-bubble' : 'user-bubble';
  const contentClass = isError ? 'bubble-content error-bubble' : 'bubble-content';

  wrap.innerHTML = `
    <div class="avatar ${avatarClass}"><i class="fas ${avatarIcon}"></i></div>
    <div class="message-bubble ${bubbleClass}">
      <div class="${contentClass}">${formattedHTML}</div>
      <div class="message-meta">
        ${intentBadge}
        <span class="msg-time">${time}</span>
      </div>
    </div>
  `;

  chatMessages.appendChild(wrap);
  smoothScrollToBottom();
}

// ── Typing indicator ──────────────────────────────────────────────────────────
function showTyping() {
  typingWrapper.classList.add('visible');
  chatMessages.appendChild(typingWrapper);  // keep it at bottom
  smoothScrollToBottom();
}

function hideTyping() {
  typingWrapper.classList.remove('visible');
}

// ── Format response text → HTML ───────────────────────────────────────────────
function formatResponse(raw) {
  if (!raw) return '';

  let html = raw
    // Bold: **text**
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // Italic: *text*
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    // Backtick code
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // Newlines → <br>
    .replace(/\n/g, '<br>');

  return html;
}

// ── Load chat history ─────────────────────────────────────────────────────────
async function loadHistory() {
  showToast('Loading history…', 'info');
  try {
    const res  = await fetch(`${API_URL}/api/history`);
    const data = await res.json();

    if (!Array.isArray(data) || data.length === 0) {
      showToast('No history found for this session', 'info');
      return;
    }

    // Reset display
    chatMessages.innerHTML = '';
    data.forEach(item => {
      if (item.question) appendMessage(item.question, 'user');
      if (item.answer)   appendMessage(item.answer,   'bot');
    });
    showToast(`Loaded ${data.length} past exchanges`, 'success');

  } catch (e) {
    showToast('Could not load history', 'error');
  }
}

// ── Clear chat ────────────────────────────────────────────────────────────────
function confirmClear() {
  if (!confirm('Clear the current chat display?')) return;
  restoreWelcome();
  showToast('Chat cleared', 'info');
}

function restoreWelcome() {
  chatMessages.innerHTML = `
    <div class="message bot" id="welcomeMsg">
      <div class="avatar bot-av"><i class="fas fa-robot"></i></div>
      <div class="message-bubble bot-bubble">
        <div class="bubble-content">
          <p>Hello! 👋 Welcome back to <strong>College Enquiry Chatbot</strong>.</p>
          <p>What would you like to know?</p>
        </div>
        <div class="quick-chips">
          <button class="chip" data-query="Tell me about the admission process">📋 Admissions</button>
          <button class="chip" data-query="What courses do you offer?">📚 Courses</button>
          <button class="chip" data-query="What is the fee structure?">💰 Fees</button>
          <button class="chip" data-query="Tell me about placements">📊 Placements</button>
          <button class="chip" data-query="Find route from Home to Office">🗺️ Route Finder</button>
          <button class="chip" data-query="Tell me about scholarships">🏅 Scholarships</button>
        </div>
        <div class="message-meta"><span class="msg-time">Just now</span></div>
      </div>
    </div>
  `;
}

// ── Health check ──────────────────────────────────────────────────────────────
async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_URL}/api/health`, { signal: AbortSignal.timeout(6000) });
    if (res.ok) {
      statusText.textContent = 'Connected';
    } else {
      throw new Error('Non-OK');
    }
  } catch {
    statusText.textContent = 'Offline';
    document.querySelector('.status-dot').style.background = 'var(--danger)';
    showToast('Backend offline — responses unavailable', 'error');
  }
}

// ── Toast ─────────────────────────────────────────────────────────────────────
function showToast(message, type = 'info', duration = 3500) {
  const icons = { success: 'fa-check-circle', error: 'fa-times-circle', info: 'fa-info-circle' };
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<i class="fas ${icons[type] || icons.info}"></i> ${message}`;
  toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.style.transition = 'opacity .4s ease, transform .4s ease';
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(60px)';
    setTimeout(() => toast.remove(), 450);
  }, duration);
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function smoothScrollToBottom() {
  requestAnimationFrame(() => {
    chatMessages.scrollTo({ top: chatMessages.scrollHeight, behavior: 'smooth' });
  });
}

function formatTime(date) {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true });
}