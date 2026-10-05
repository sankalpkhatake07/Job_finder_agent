/**
 * CareerMatch Agent v2.0 - Futuristic Client Controller & Cyber HUD Engine
 * - Web Audio API Sci-Fi Synthesizer (Procedural SFX with mute toggle)
 * - 3D Holographic Tilt with dynamic specular glare
 * - Autonomous Radar Scope Canvas HUD
 * - Live System Telemetry & Clock
 * - Token Vault & Cyber Toasts
 */

// Procedural Sci-Fi Web Audio Synthesizer (Zero external audio assets)
const AudioFX = {
  ctx: null,
  enabled: localStorage.getItem('career_sfx_enabled') !== 'false',

  init() {
    if (!this.ctx && typeof window !== 'undefined' && (window.AudioContext || window.webkitAudioContext)) {
      this.ctx = new (window.AudioContext || window.webkitAudioContext)();
    }
  },

  toggle() {
    this.enabled = !this.enabled;
    localStorage.setItem('career_sfx_enabled', this.enabled ? 'true' : 'false');
    this.updateButton();
    if (this.enabled) {
      this.blip(880, 'sine', 0.08);
      CareerAgent.showToast('Audio Telemetry: ONLINE', 'info', 1800);
    } else {
      CareerAgent.showToast('Audio Telemetry: MUTED', 'warning', 1800);
    }
  },

  updateButton() {
    const btn = document.getElementById('sfx-toggle-btn');
    if (btn) {
      btn.innerHTML = this.enabled ? '<span>🔊 SFX: ON</span>' : '<span>🔇 SFX: OFF</span>';
      btn.className = this.enabled ? 'sfx-pill active' : 'sfx-pill';
    }
  },

  blip(freq = 800, type = 'sine', duration = 0.04, gainVal = 0.025) {
    if (!this.enabled) return;
    try {
      this.init();
      if (!this.ctx) return;
      if (this.ctx.state === 'suspended') this.ctx.resume();
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
      gain.gain.setValueAtTime(gainVal, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + duration);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + duration);
    } catch (e) {}
  },

  click() {
    this.blip(950, 'triangle', 0.04, 0.03);
  },

  hover() {
    this.blip(1400, 'sine', 0.015, 0.008);
  },

  scan() {
    if (!this.enabled) return;
    try {
      this.init();
      if (!this.ctx) return;
      if (this.ctx.state === 'suspended') this.ctx.resume();
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(300, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(1600, this.ctx.currentTime + 0.35);
      gain.gain.setValueAtTime(0.04, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + 0.35);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + 0.35);
    } catch (e) {}
  },

  success() {
    if (!this.enabled) return;
    setTimeout(() => this.blip(784, 'sine', 0.12, 0.035), 0);
    setTimeout(() => this.blip(1046, 'sine', 0.18, 0.035), 100);
  },

  error() {
    if (!this.enabled) return;
    this.blip(220, 'sawtooth', 0.22, 0.04);
  }
};

const CareerAgent = {
  // Token Vault
  getToken() {
    return localStorage.getItem('career_agent_token') || '';
  },

  setToken(val) {
    if (val && val.trim()) {
      localStorage.setItem('career_agent_token', val.trim());
      this.updateTokenBadge();
      AudioFX.success();
      return true;
    }
    return false;
  },

  clearToken() {
    localStorage.removeItem('career_agent_token');
    this.updateTokenBadge();
    AudioFX.click();
    this.showToast('Security token cleared', 'warning');
  },

  updateTokenBadge() {
    const badge = document.getElementById('token-status-badge');
    const hasToken = !!this.getToken();
    if (badge) {
      if (hasToken) {
        badge.className = 'token-pill active';
        badge.innerHTML = '<span class="pulse-dot green"></span> TOKEN: ARMED';
        badge.title = 'Admin token saved in browser. Click to change.';
      } else {
        badge.className = 'token-pill warning';
        badge.innerHTML = '<span class="pulse-dot amber"></span> TOKEN: UNSET';
        badge.title = 'No token set. Click to configure.';
      }
    }
  },

  async promptTokenIfNeeded() {
    let token = this.getToken();
    if (token) return token;

    return new Promise((resolve) => {
      const modal = document.getElementById('token-modal');
      const input = document.getElementById('token-input');
      const submit = document.getElementById('token-submit-btn');
      const cancel = document.getElementById('token-cancel-btn');

      if (!modal) {
        token = prompt('Enter Admin Token:');
        if (token) this.setToken(token);
        resolve(token);
        return;
      }

      AudioFX.click();
      modal.classList.add('visible');
      input.value = '';
      input.focus();

      const onKey = (e) => {
        if (e.key === 'Enter') submit.click();
        if (e.key === 'Escape') cancel.click();
      };
      input.addEventListener('keydown', onKey);

      submit.onclick = () => {
        const val = input.value.trim();
        if (val) {
          this.setToken(val);
          modal.classList.remove('visible');
          input.removeEventListener('keydown', onKey);
          resolve(val);
        } else {
          AudioFX.error();
          this.showToast('Please provide a valid token', 'warning');
        }
      };

      cancel.onclick = () => {
        AudioFX.click();
        modal.classList.remove('visible');
        input.removeEventListener('keydown', onKey);
        resolve(null);
      };
    });
  },

  openTokenManager() {
    AudioFX.click();
    const modal = document.getElementById('token-modal');
    const input = document.getElementById('token-input');
    if (modal && input) {
      input.value = this.getToken();
      modal.classList.add('visible');
      input.focus();
    }
  },

  closeTokenManager() {
    AudioFX.click();
    const modal = document.getElementById('token-modal');
    if (modal) modal.classList.remove('visible');
  },

  // Cyber Toast System
  showToast(message, type = 'info', duration = 3600) {
    let container = document.getElementById('cyber-toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'cyber-toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `cyber-toast toast-${type}`;
    
    const iconMap = {
      success: '⚡',
      error: '✖',
      warning: '⚠',
      info: '◈'
    };

    toast.innerHTML = `
      <div class="toast-content">
        <span class="toast-icon">${iconMap[type] || '◈'}</span>
        <span class="toast-text">${message}</span>
      </div>
      <div class="toast-bar"></div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
      toast.classList.add('fade-out');
      setTimeout(() => toast.remove(), 400);
    }, duration);
  },

  // Scan HUD with telemetry
  async runScan() {
    AudioFX.click();
    const token = await this.promptTokenIfNeeded();
    if (!token) return;

    AudioFX.scan();
    const overlay = document.getElementById('scan-hud-overlay');
    const logEl = document.getElementById('scan-log-stream');
    const btn = document.getElementById('scan-btn');

    if (btn) btn.classList.add('loading');
    if (overlay) overlay.classList.add('visible');

    const logs = [
      'INITIALIZING SCANNER ENGINE v2.0...',
      'CONNECTING TO VERIFIED REPOSITORIES & ATS ENDPOINTS...',
      'FETCHING NEW LISTINGS (GREENHOUSE, LEVER, ASHBY, RSS, HTML)...',
      'VECTORIZING CANDIDATE RESUME PROFILE & SKILL MATRICES...',
      'RUNNING TF-IDF COSINE SIMILARITY & 6-DIMENSIONAL FIT SCORING...',
      'FILTERING KEYWORDS, LOCATIONS & WORK PREFERENCES...'
    ];

    let logIdx = 0;
    const interval = setInterval(() => {
      if (logEl && logIdx < logs.length) {
        AudioFX.hover();
        const item = document.createElement('div');
        item.className = 'log-item';
        item.innerHTML = `<span class="log-time">[${new Date().toLocaleTimeString()}]</span> ${logs[logIdx]}`;
        logEl.appendChild(item);
        logEl.scrollTop = logEl.scrollHeight;
        logIdx++;
      }
    }, 400);

    try {
      const res = await fetch('/scan', {
        method: 'POST',
        headers: { 'X-Admin-Token': token }
      });

      clearInterval(interval);

      if (!res.ok) {
        AudioFX.error();
        const err = await res.json().catch(() => ({ detail: 'Scan request failed' }));
        if (overlay) overlay.classList.remove('visible');
        if (btn) btn.classList.remove('loading');
        this.showToast(`Scan Failed: ${err.detail || 'Unauthorized or error'}`, 'error');
        return;
      }

      const data = await res.json();
      AudioFX.success();

      if (logEl) {
        const finalLog = document.createElement('div');
        finalLog.className = 'log-item success';
        finalLog.innerHTML = `<span class="log-time">[${new Date().toLocaleTimeString()}]</span> SCAN COMPLETE: Discovered ${data.jobs || 0} jobs | ${data.high || 0} HIGH matches | ${data.medium || 0} MEDIUM`;
        logEl.appendChild(finalLog);
        logEl.scrollTop = logEl.scrollHeight;
      }

      this.showToast(`Scan completed: ${data.jobs || 0} jobs processed (${data.high || 0} HIGH)`, 'success', 3000);

      setTimeout(() => {
        location.reload();
      }, 1200);

    } catch (e) {
      clearInterval(interval);
      AudioFX.error();
      if (overlay) overlay.classList.remove('visible');
      if (btn) btn.classList.remove('loading');
      this.showToast('Network error during scan execution', 'error');
    }
  },

  // Set Application Status
  async setStatus(id, status) {
    AudioFX.click();
    const token = await this.promptTokenIfNeeded();
    if (!token) return;

    try {
      const res = await fetch('/api/applications/' + id, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Admin-Token': token
        },
        body: JSON.stringify({ status })
      });

      if (!res.ok) {
        AudioFX.error();
        const err = await res.json().catch(() => ({ detail: 'Update failed' }));
        this.showToast(`Failed: ${err.detail || 'Unauthorized'}`, 'error');
        return;
      }

      AudioFX.success();
      this.showToast(`Status updated to ${status}`, 'success');
      setTimeout(() => location.reload(), 600);
    } catch (e) {
      AudioFX.error();
      this.showToast('Connection error', 'error');
    }
  },

  // Live Table Filtering
  initTableFilter() {
    const searchInput = document.getElementById('job-search-input');
    const table = document.getElementById('jobs-table');
    const counter = document.getElementById('filter-match-count');
    if (!searchInput || !table) return;

    searchInput.addEventListener('input', () => {
      AudioFX.hover();
      const q = searchInput.value.toLowerCase().trim();
      const rows = table.querySelectorAll('tbody tr:not(.empty-row)');
      let visible = 0;

      rows.forEach(row => {
        const text = row.innerText.toLowerCase();
        if (!q || text.includes(q)) {
          row.style.display = '';
          visible++;
        } else {
          row.style.display = 'none';
        }
      });

      if (counter) {
        counter.textContent = `${visible} displayed`;
      }
    });
  },

  // Score Detail Modal
  openScoreDetail(jobTitle, score, category, skillScore, expScore, eduScore, respScore, techScore, prefScore, matched, missing, explanation) {
    AudioFX.click();
    const modal = document.getElementById('score-detail-modal');
    if (!modal) return;

    document.getElementById('modal-job-title').textContent = jobTitle;
    document.getElementById('modal-score-value').textContent = score + '%';
    document.getElementById('modal-category-tag').textContent = category;
    document.getElementById('modal-category-tag').className = `pill ${category.toLowerCase()}`;

    // Dimensions
    this.renderBar('meter-skill', skillScore);
    this.renderBar('meter-exp', expScore);
    this.renderBar('meter-edu', eduScore);
    this.renderBar('meter-resp', respScore);
    this.renderBar('meter-tech', techScore);
    this.renderBar('meter-pref', prefScore);

    // Tags
    const matchedEl = document.getElementById('modal-matched-skills');
    matchedEl.innerHTML = '';
    const matchedList = Array.isArray(matched) ? matched : (matched ? matched.split(',') : []);
    if (matchedList.length) {
      matchedList.forEach(s => {
        const tag = document.createElement('span');
        tag.className = 'cyber-tag match';
        tag.textContent = '✓ ' + s.trim();
        matchedEl.appendChild(tag);
      });
    } else {
      matchedEl.innerHTML = '<span class="muted-text">None</span>';
    }

    const missingEl = document.getElementById('modal-missing-skills');
    missingEl.innerHTML = '';
    const missingList = Array.isArray(missing) ? missing : (missing ? missing.split(',') : []);
    if (missingList.length) {
      missingList.forEach(s => {
        const tag = document.createElement('span');
        tag.className = 'cyber-tag missing';
        tag.textContent = '✕ ' + s.trim();
        missingEl.appendChild(tag);
      });
    } else {
      missingEl.innerHTML = '<span class="muted-text">None</span>';
    }

    document.getElementById('modal-explanation').textContent = explanation || 'No extended breakdown provided.';
    modal.classList.add('visible');
  },

  renderBar(id, val) {
    const el = document.getElementById(id);
    const label = document.getElementById(id + '-val');
    const num = Math.min(100, Math.max(0, Number(val) || 0));
    if (el) el.style.width = num + '%';
    if (label) label.textContent = num.toFixed(0) + '%';
  },

  closeScoreDetail() {
    AudioFX.click();
    const modal = document.getElementById('score-detail-modal');
    if (modal) modal.classList.remove('visible');
  },

  // 3D Holographic Card Tilt with dynamic specular reflection
  initHoloTilt() {
    const cards = document.querySelectorAll('.card-hud, .panel, .funnel-card');
    cards.forEach(card => {
      // Create glare overlay
      let glare = card.querySelector('.holo-glare');
      if (!glare) {
        glare = document.createElement('div');
        glare.className = 'holo-glare';
        card.appendChild(glare);
      }

      card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        const rotateX = ((y - centerY) / centerY) * -5.5;
        const rotateY = ((x - centerX) / centerX) * 5.5;

        card.style.transform = `perspective(1000px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) translateY(-2px)`;
        glare.style.background = `radial-gradient(circle at ${x}px ${y}px, rgba(0, 240, 255, 0.18) 0%, transparent 65%)`;
        glare.style.opacity = '1';
      });

      card.addEventListener('mouseleave', () => {
        card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0)';
        glare.style.opacity = '0';
      });

      card.addEventListener('mouseenter', () => {
        AudioFX.hover();
      });
    });

    // Add audio feedback to buttons
    document.querySelectorAll('.btn-cyber, .btn-cyber-outline, .pill, .mini-btn, .category-tab').forEach(el => {
      el.addEventListener('mouseenter', () => AudioFX.hover());
    });
  },

  // Live Circular Radar Scope Widget
  initRadarScope() {
    const canvas = document.getElementById('radar-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const size = canvas.width = canvas.height = 140;
    const center = size / 2;
    const radius = size * 0.44;
    let angle = 0;

    // Simulated radar targets (blips)
    const targets = [
      { r: radius * 0.45, a: 0.8, alpha: 1, ping: false },
      { r: radius * 0.72, a: 2.1, alpha: 1, ping: false },
      { r: radius * 0.88, a: 4.3, alpha: 1, ping: false },
      { r: radius * 0.60, a: 5.5, alpha: 1, ping: false }
    ];

    function drawRadar() {
      ctx.clearRect(0, 0, size, size);

      // Radar base circle
      ctx.strokeStyle = 'rgba(0, 240, 255, 0.2)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(center, center, radius, 0, Math.PI * 2);
      ctx.stroke();

      // Concentric rings (25%, 50%, 75%)
      [0.25, 0.5, 0.75].forEach(frac => {
        ctx.beginPath();
        ctx.arc(center, center, radius * frac, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(0, 240, 255, 0.08)';
        ctx.stroke();
      });

      // Crosshairs
      ctx.beginPath();
      ctx.moveTo(center - radius, center);
      ctx.lineTo(center + radius, center);
      ctx.moveTo(center, center - radius);
      ctx.lineTo(center, center + radius);
      ctx.strokeStyle = 'rgba(0, 240, 255, 0.12)';
      ctx.stroke();

      // Sweeping radar beam
      angle = (angle + 0.04) % (Math.PI * 2);
      const sweepX = center + Math.cos(angle) * radius;
      const sweepY = center + Math.sin(angle) * radius;

      // Sweep gradient fan
      const sweepGrad = ctx.createRadialGradient(center, center, 0, center, center, radius);
      sweepGrad.addColorStop(0, 'rgba(0, 240, 255, 0.25)');
      sweepGrad.addColorStop(1, 'rgba(0, 240, 255, 0.02)');

      ctx.beginPath();
      ctx.moveTo(center, center);
      ctx.arc(center, center, radius, angle - 0.4, angle);
      ctx.closePath();
      ctx.fillStyle = sweepGrad;
      ctx.fill();

      // Radar beam line
      ctx.beginPath();
      ctx.moveTo(center, center);
      ctx.lineTo(sweepX, sweepY);
      ctx.strokeStyle = 'rgba(0, 240, 255, 0.8)';
      ctx.lineWidth = 1.5;
      ctx.shadowColor = '#00f0ff';
      ctx.shadowBlur = 6;
      ctx.stroke();
      ctx.shadowBlur = 0;

      // Draw blips
      targets.forEach(t => {
        const tX = center + Math.cos(t.a) * t.r;
        const tY = center + Math.sin(t.a) * t.r;

        // Check if sweep hit the target
        const diff = Math.abs(angle - t.a);
        if (diff < 0.06) {
          t.alpha = 1.0;
        } else {
          t.alpha = Math.max(0.2, t.alpha - 0.008);
        }

        ctx.beginPath();
        ctx.arc(tX, tY, 2.5, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(16, 185, 129, ${t.alpha})`;
        ctx.shadowColor = '#10b981';
        ctx.shadowBlur = 8 * t.alpha;
        ctx.fill();
        ctx.shadowBlur = 0;
      });

      requestAnimationFrame(drawRadar);
    }

    drawRadar();
  },

  // Live Telemetry & UTC Clock
  initTelemetry() {
    const clockEl = document.getElementById('hud-utc-clock');
    if (clockEl) {
      setInterval(() => {
        const now = new Date();
        clockEl.textContent = now.toISOString().slice(11, 19) + ' UTC';
      }, 1000);
    }
  }
};

document.addEventListener('DOMContentLoaded', () => {
  AudioFX.updateButton();
  CareerAgent.updateTokenBadge();
  CareerAgent.initTableFilter();
  CareerAgent.initHoloTilt();
  CareerAgent.initRadarScope();
  CareerAgent.initTelemetry();
});
