'use strict';
const CONFIG = {
  BACKEND_URL: 'http://127.0.0.1:5500',
  GUEST_USER_ID: 1,
  USE_BACKEND_CHAT: false,
};


/* Language Detection */
const LANG_MARKERS = {
  rw: ['ndashaka','nshobora','mfasha','amakuru','indangamuntu','icyemezo','ubwishingizi',
       'amavuko','umurenge','ese','gusaba','kwishyura','murakoze','nde','mbese',
       'uko','bite','nyuma','kuri','nta','imodoka','uruhushya','umuryango'],
  fr: ['bonjour','merci','comment','voudrais','besoin','pouvez','certificat','carte',
       'identité','où','quand','combien','acte','naissance','permis','conduire',
       'les','des','une','comment','faire','je','mariage','mutuelle'],
  en: ['hello','please','need','want','how','what','where','when','certificate',
       'application','help','driving','license','birth','national','insurance',
       'health','marriage','renewal','apply'],
};

function detectLanguage(text) {
  const tokens = (text.toLowerCase().match(/[a-zàâäéèêëïîôöùûüç']+/g) || []);
  const scores = { rw: 0, fr: 0, en: 0 };
  tokens.forEach(tok => {
    if (LANG_MARKERS.rw.includes(tok)) scores.rw += 2;
    if (LANG_MARKERS.fr.includes(tok)) scores.fr += 1;
    if (LANG_MARKERS.en.includes(tok)) scores.en += 1;
  });
  const rwClusters = (text.toLowerCase().match(/(shy|nyi|mwa|cya|nya|ubw)/g) || []).length;
  scores.rw += rwClusters;
  const total = scores.rw + scores.fr + scores.en;
  if (total === 0) return currentLang;
  return Object.entries(scores).sort((a, b) => b[1] - a[1])[0][0];
}

/* Retrieval */
function tokenize(str) {
  return new Set((str.toLowerCase().match(/[a-zàâäéèêëïîôöùûüç']+/g) || []));
}

function retrieveServices(query, lang) {
  const qTokens = tokenize(query);
  if (qTokens.size === 0) return [];
  const scored = [];
  Object.values(KB).forEach(svc => {
    const nameText = [svc.name.en, svc.name.rw, svc.name.fr].join(' ');
    const bodyText = [
      svc.requirements.map(r => r[lang] || r.en).join(' '),
      svc.steps.map(s => s[lang] || s.en).join(' '),
      svc.category[lang] || svc.category.en,
    ].join(' ');
    const nameTokens = tokenize(nameText);
    const bodyTokens = tokenize(bodyText);
    let nameHits = 0, bodyHits = 0;
    qTokens.forEach(tok => {
      if (nameTokens.has(tok)) nameHits++;
      if (bodyTokens.has(tok)) bodyHits++;
    });
    const score = 3 * nameHits + bodyHits;
    if (score > 0) scored.push({ svc, score });
  });
  return scored.sort((a, b) => b.score - a.score).slice(0, 2).map(s => s.svc);
}

/* Generating Response */
const TEMPLATES = {
  intro:      { rw: n => `Ngufasha gusaba **${n}** kuri Irembo. Dore amakuru akenewe:`,     en: n => `I can help you with **${n}** on Irembo. Here is what you need:`,              fr: n => `Je peux vous aider pour **${n}** sur Irembo. Voici ce qu'il vous faut :` },
  reqHeader:  { rw: () => 'Ibisabwa:',                                                       en: () => 'Requirements:',                                                              fr: () => 'Pièces requises :' },
  stepHeader: { rw: () => 'Intambwe zo gukurikiza:',                                         en: () => 'Steps to follow:',                                                           fr: () => 'Étapes à suivre :' },
  fee:        { rw: a => `Igiciro: ${Number(a).toLocaleString()} RWF (wishyurwa ukoresheje Mobile Money).`, en: a => `Fee: ${Number(a).toLocaleString()} RWF, paid via Mobile Money.`, fr: a => `Frais : ${Number(a).toLocaleString()} FRW, payés via Mobile Money.` },
  optional:   { rw: ' (si itegeko)', en: ' (optional)', fr: ' (optionnel)' },
  closing:    { rw: () => 'Ufite ikibazo ikindi? Nzabishingiraho.',                           en: () => 'Do you have any other questions? I\'m here to help.',                         fr: () => 'Avez-vous d\'autres questions ? Je suis là pour vous aider.' },
  multiMatch: { rw: names => `Nabonye serivisi nyinshi zihuje:\n${names}.\nNi iyihe ushaka kumenya?`, en: names => `I found a few matching services:\n${names}.\nWhich one would you like to know about?`, fr: names => `J'ai trouvé plusieurs services correspondants :\n${names}.\nLequel souhaitez-vous connaître ?` },
};

function buildLocalResponse(matches, lang) {
  const ui = UI[lang];
  if (matches.length === 0) return ui.noMatch;
  if (matches.length > 1) {
    const names = matches.map((s, i) => `  ${i + 1}. ${s.name[lang]}`).join('\n');
    return TEMPLATES.multiMatch[lang](names);
  }
  const svc = matches[0];
  const opt = TEMPLATES.optional[lang];
  const lines = [
    TEMPLATES.intro[lang](svc.name[lang]), '',
    TEMPLATES.reqHeader[lang](),
    ...svc.requirements.map(r => `  - ${r[lang] || r.en}${r.mandatory ? '' : opt}`),
    '', TEMPLATES.stepHeader[lang](),
    ...svc.steps.map((s, i) => `  ${i + 1}. ${s[lang] || s.en}`),
    '', TEMPLATES.fee[lang](svc.fee_rwf),
    '', TEMPLATES.closing[lang](),
  ];
  return lines.join('\n');
}

/* Session */
const SESSION = {
  STORAGE_KEY_USER: 'govagent_user_id',

  getUserId() {
    const stored = localStorage.getItem(this.STORAGE_KEY_USER);
    if (stored) return Number(stored);
    return null;
  },

  saveUserId(id) {
    localStorage.setItem(this.STORAGE_KEY_USER, String(id));
  },
  conversationId: null,

  async initUser() {
    const existing = this.getUserId();
    if (existing) return existing;
    this.saveUserId(CONFIG.GUEST_USER_ID);
    return CONFIG.GUEST_USER_ID;
  },

  updateSessionDisplay() {
    const userEl = document.getElementById('session-user-id');
    const convEl = document.getElementById('session-conv-id');
    if (userEl) userEl.textContent = `${UI[currentLang].sessionLabel} #${this.getUserId() ?? '—'}`;
    if (convEl) convEl.textContent = this.conversationId
      ? `${UI[currentLang].convLabel} #${this.conversationId}`
      : '';
  },
};

/* API */
const API = {
  async _fetch(method, path, body = null) {
    const url = `${CONFIG.BACKEND_URL}${path}`;
    const opts = {
      method,
      headers: { 'Content-Type': 'application/json' },
    };
    if (body !== null) opts.body = JSON.stringify(body);
    const res = await fetch(url, opts);
    if (!res.ok) {
      console.warn(`[API] ${method} ${path} → ${res.status}`);
      return null;
    }
    return res.json();
  },

  async _fetchMultipart(path, formData) {
    const url = `${CONFIG.BACKEND_URL}${path}`;
    const res = await fetch(url, { method: 'POST', body: formData });
    if (!res.ok) {
      console.warn(`[API] POST ${path} → ${res.status}`);
      return null;
    }
    return res.json();
  },

  async checkHealth() {
    try {
      const data = await this._fetch('GET', '/health');
      return data?.status === 'ok';
    } catch {
      return false;
    }
  },

/* Chat */
  async startConversation(userId) {
    try {
      return await this._fetch('POST', '/chat/start', { user_id: userId });
    } catch (err) {
      console.error('[API] startConversation failed:', err);
      return null;
    }
  },

  async saveMessage(conversationId, role, content) {
    try {
      return await this._fetch(
        'POST',
        `/chat/${conversationId}/messages`,
        { role, content }
      );
    } catch (err) {
      console.error('[API] saveMessage failed:', err);
      return null;
    }
  },

/* Application */
  async createApplication(userId, serviceId, conversationId) {
    try {
      return await this._fetch('POST', '/applications', {
        user_id: userId,
        service_id: serviceId,
        conversation_id: conversationId ?? null,
      });
    } catch (err) {
      console.error('[API] createApplication failed:', err);
      return null;
    }
  },

  async getApplication(applicationId) {
    try {
      return await this._fetch('GET', `/applications/${applicationId}`);
    } catch (err) {
      console.error('[API] getApplication failed:', err);
      return null;
    }
  },

  async saveApplicationData(applicationId, requirementId, value) {
    try {
      return await this._fetch(
        'PUT',
        `/applications/${applicationId}/data/${requirementId}`,
        { requirement_id: requirementId, value }
      );
    } catch (err) {
      console.error('[API] saveApplicationData failed:', err);
      return null;
    }
  },

  /* Payment */
  async createPayment(applicationId, amount, gatewayReference = null) {
    try {
      return await this._fetch('POST', `/payments/${applicationId}`, {
        payment_method: 'mobile_money',
        amount,
        gateway_reference: gatewayReference,
      });
    } catch (err) {
      console.error('[API] createPayment failed:', err);
      return null;
    }
  },

  /* Document upload */
  async uploadDocument(applicationId, file, requirementId = null) {
    try {
      const fd = new FormData();
      fd.append('file', file);
      if (requirementId !== null) fd.append('requirement_id', String(requirementId));
      return await this._fetchMultipart(`/uploads/${applicationId}`, fd);
    } catch (err) {
      console.error('[API] uploadDocument failed:', err);
      return null;
    }
  },

  // Will be added when the users and services endpoints are ready from Davy.
};

/* Chat Pipeline */
let currentLang  = 'en';
let isBusy       = false;
let backendOnline = false;

async function ensureConversation() {
  if (SESSION.conversationId) return SESSION.conversationId;
  const userId = SESSION.getUserId() ?? CONFIG.GUEST_USER_ID;
  const conv = await API.startConversation(userId);
  if (conv?.id) {
    SESSION.conversationId = conv.id;
    SESSION.updateSessionDisplay();
  }
  return SESSION.conversationId;
}

async function sendMessage() {
  const raw = textInput.value.trim();
  if (!raw || isBusy) return;

  textInput.value = '';
  autoGrow(textInput);
  isBusy = true;
  sendBtn.disabled = true;

  const detected = detectLanguage(raw);
  if (detected !== currentLang) setLanguage(detected, false);

  appendMessage('citizen', raw);
  showTyping();

  const convId = await ensureConversation();
  if (convId) {
    API.saveMessage(convId, 'user', raw).catch(() => {});
  }
  await new Promise(r => setTimeout(r, 600 + Math.random() * 400));
const matches  = retrieveServices(raw, currentLang);
  const replyText = buildLocalResponse(matches, currentLang);

  hideTyping();

  const showBadge = matches.length === 1;
  appendMessage('assistant', replyText, { badge: showBadge ? true : undefined });

  if (convId) {
    API.saveMessage(convId, 'assistant', replyText).catch(() => {});
  }

  if (matches.length === 1) showServiceCard(matches[0]);
  speak(replyText, currentLang);
  isBusy = false;
  sendBtn.disabled = false;
  textInput.focus();
}

/* Text-to-Speech */
let speakEnabled = true;

function speak(text, lang) {
  if (!speakEnabled || !('speechSynthesis' in window)) return;
  const clean = text.replace(/\*\*([^*]+)\*\*/g, '$1');
  try {
    window.speechSynthesis.cancel();
    const utter  = new SpeechSynthesisUtterance(clean);
    utter.lang   = LANG_CODES[lang] || 'en-US';
    utter.rate   = 0.95;
    const voices = window.speechSynthesis.getVoices();
    const match  = voices.find(v => v.lang === utter.lang)
                || voices.find(v => v.lang.startsWith(lang));
    if (match) utter.voice = match;
    window.speechSynthesis.speak(utter);
  } catch (_) {}
}

/* Speech-to-text */
let isRecording = false;
let recognizer  = null;

function initSpeechRecognition() {
  const SRImpl = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SRImpl) return;

  recognizer = new SRImpl();
  recognizer.continuous     = false;
  recognizer.interimResults = false;

  recognizer.onstart = () => {
    isRecording = true;
    micBtn.classList.add('recording');
    micBtn.setAttribute('aria-pressed', 'true');
    voiceNoteEl.textContent = UI[currentLang].listening;
  };

  recognizer.onresult = event => {
    textInput.value = event.results[0][0].transcript;
    sendMessage();
  };

  recognizer.onerror = event => {
    voiceNoteEl.textContent = event.error;
  };

  recognizer.onend = () => {
    isRecording = false;
    micBtn.classList.remove('recording');
    micBtn.setAttribute('aria-pressed', 'false');
    setTimeout(() => { voiceNoteEl.textContent = ''; }, 2500);
  };
}

function toggleMic() {
  if (!recognizer) {
    voiceNoteEl.textContent = UI[currentLang].noSpeech;
    return;
  }
  if (isRecording) {
    recognizer.stop();
  } else {
    recognizer.lang = LANG_CODES[currentLang] || 'en-US';
    try { recognizer.start(); } catch (_) {}
  }
}

/* DOM Helpers */
function formatTime(date) {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function autoGrow(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}

function renderMarkdown(container, text) {
  text.split(/(\*\*[^*]+\*\*)/g).forEach(part => {
    if (part.startsWith('**') && part.endsWith('**')) {
      const s = document.createElement('strong');
      s.textContent = part.slice(2, -2);
      container.appendChild(s);
    } else {
      container.appendChild(document.createTextNode(part));
    }
  });
}

function appendMessage(sender, text, opts = {}) {
  const msg    = document.createElement('div');
  msg.className = `msg ${sender}`;

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';
  sender === 'assistant' ? renderMarkdown(bubble, text) : (bubble.textContent = text);
  msg.appendChild(bubble);

  if (opts.badge !== undefined) {
    const badge = document.createElement('span');
    badge.className = `grounding-badge ${opts.badge ? 'verified' : 'general'}`;
    badge.textContent = opts.badge ? UI[currentLang].badgeVerified : UI[currentLang].badgeGeneral;
    msg.appendChild(badge);
  }

  if (sender !== 'system') {
    const time = document.createElement('span');
    time.className = 'msg-time';
    time.textContent = formatTime(new Date());
    msg.appendChild(time);
  }

  messagesEl.appendChild(msg);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return msg;
}

function showTyping() {
  typingRow.hidden = false;
  typingRow.removeAttribute('aria-hidden');
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function hideTyping() {
  typingRow.hidden = true;
  typingRow.setAttribute('aria-hidden', 'true');
}

function setStatusBar(online) {
  backendOnline = online;
  const indicator = document.querySelector('.status-indicator');
  if (indicator) {
    indicator.style.background = online ? 'var(--success)' : '#e8a800';
  }
  if (statusText) {
    statusText.textContent = online
      ? UI[currentLang].statusOnline
      : UI[currentLang].statusOffline;
  }
}

/* Sidebar */
function showServiceCard(svc) {
  const ui = UI[currentLang];
  const L  = currentLang;

  serviceCard.dataset.serviceId = svc.id;
  serviceCard.hidden = false;
  quickPanel.hidden  = true;

  scLabel.textContent         = ui.scLabel;
  scTitle.textContent         = svc.name[L];
  scFee.textContent           = Number(svc.fee_rwf).toLocaleString() + ui.feeSuffix;
  scReqHeading.textContent    = ui.scReqHeading;
  scStepsHeading.textContent  = ui.scStepsHeading;
  scSourceText.textContent    = ui.scSource;

  scRequirements.innerHTML = '';
  svc.requirements.forEach(r => {
    const li = document.createElement('li');
    if (!r.mandatory) li.classList.add('optional');
    li.textContent = (r[L] || r.en) + (r.mandatory ? '' : ` ${ui.optional}`);
    scRequirements.appendChild(li);
  });

  scSteps.innerHTML = '';
  svc.steps.forEach(s => {
    const li = document.createElement('li');
    li.textContent = s[L] || s.en;
    scSteps.appendChild(li);
  });
}

function buildQuickList() {
  quickList.innerHTML = '';
  Object.values(KB).forEach(svc => {
    const btn = document.createElement('button');
    btn.className = 'quick-chip';
    btn.type      = 'button';
    btn.setAttribute('role', 'listitem');
    btn.innerHTML = `${svc.name[currentLang]}<span class="quick-chip-category">${svc.category[currentLang]}</span>`;
    btn.addEventListener('click', () => {
      textInput.value = svc.name[currentLang];
      sendMessage();
    });
    quickList.appendChild(btn);
  });
}

/* Switching Languages */
function setLanguage(lang) {
  currentLang = lang;

  document.querySelectorAll('.lang-btn').forEach(btn => {
    const active = btn.dataset.lang === lang;
    btn.classList.toggle('active', active);
    btn.setAttribute('aria-pressed', String(active));
  });

  const ui = UI[lang];
  textInput.placeholder           = ui.placeholder;
  statusText.textContent          = backendOnline ? ui.statusOnline : ui.statusOffline;
  quickHeading.textContent        = ui.quickHeading;
  voicePanelHeading.textContent   = ui.voiceHeading;
  voicePanelNote.textContent      = ui.voiceNote;
  infoHeading.textContent         = ui.infoHeading;
  infoNote.textContent            = ui.infoNote;
  voiceToggleLabel.textContent    = speakEnabled ? ui.voiceOn : ui.voiceOff;

  buildQuickList();
  SESSION.updateSessionDisplay();

  if (!serviceCard.hidden) {
    const id = serviceCard.dataset.serviceId;
    if (id && KB[id]) showServiceCard(KB[id]);
  }
}

const messagesEl        = document.getElementById('messages');
const typingRow         = document.getElementById('typing-row');
const textInput         = document.getElementById('text-input');
const sendBtn           = document.getElementById('send-btn');
const micBtn            = document.getElementById('mic-btn');
const voiceNoteEl       = document.getElementById('voice-note');
const statusText        = document.getElementById('status-text');
const serviceCard       = document.getElementById('service-card');
const quickPanel        = document.getElementById('quick-panel');
const quickList         = document.getElementById('quick-list');
const quickHeading      = document.getElementById('quick-heading');
const scLabel           = document.getElementById('sc-label');
const scTitle           = document.getElementById('sc-title');
const scFee             = document.getElementById('sc-fee');
const scRequirements    = document.getElementById('sc-requirements');
const scSteps           = document.getElementById('sc-steps');
const scReqHeading      = document.getElementById('sc-req-heading');
const scStepsHeading    = document.getElementById('sc-steps-heading');
const scSourceText      = document.getElementById('sc-source-text');
const voiceToggle       = document.getElementById('voice-toggle');
const voiceToggleLabel  = document.getElementById('voice-toggle-label');
const voicePanelHeading = document.getElementById('voice-panel-heading');
const voicePanelNote    = document.getElementById('voice-panel-note');
const infoHeading       = document.getElementById('info-heading');
const infoNote          = document.getElementById('info-note');

sendBtn.addEventListener('click', sendMessage);

textInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});

textInput.addEventListener('input', () => autoGrow(textInput));

document.querySelectorAll('.lang-btn').forEach(btn => {
  btn.addEventListener('click', () => setLanguage(btn.dataset.lang));
});

micBtn.addEventListener('click', toggleMic);

voiceToggle.addEventListener('click', () => {
  speakEnabled = !speakEnabled;
  voiceToggle.setAttribute('aria-pressed', String(speakEnabled));
  voiceToggleLabel.textContent = speakEnabled ? UI[currentLang].voiceOn : UI[currentLang].voiceOff;
  if (!speakEnabled && 'speechSynthesis' in window) window.speechSynthesis.cancel();
});

async function init() {
  initSpeechRecognition();
  if (window.speechSynthesis) window.speechSynthesis.onvoiceschanged = () => {};
  const online = await API.checkHealth();
  setStatusBar(online);
  await SESSION.initUser();
  setLanguage('en');
  appendMessage('assistant', UI.en.greeting);

  SESSION.updateSessionDisplay();
}

init();