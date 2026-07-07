'use strict';
const CONFIG = {
  BACKEND_URL: 'http://127.0.0.1:5500',
  GUEST_USER_ID: 1,
  USE_BACKEND_CHAT: false,
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
    try {
      const res = await fetch(url, opts);
      if (!res.ok) {
        console.warn(`[API] ${method} ${path} → ${res.status}`);
        return null;
      }
      return await res.json();
    } catch (err) {
      console.warn(`[API] ${method} ${path} failed:`, err.message);
      return null;
    }
  },

  async _fetchMultipart(path, formData) {
    const url = `${CONFIG.BACKEND_URL}${path}`;
    try {
      const res = await fetch(url, { method: 'POST', body: formData });
      if (!res.ok) {
      console.warn(`[API] POST ${path} → ${res.status}`);
      return null;
      }
      return res.json();
    } catch (err) {
    console.warn(`[API] POST ${path} failed:`, err.message);
    return null;
    }
  },

  async checkHealth() {
    const data = await this._fetch('GET', '/health');
    return data?.status === 'ok';
  },

/* Users */
  createUser(payload) {  
    return this._fetch('POST', '/users', payload);
  },
  lookupUser(payload) {
    return this._fetch('POST', '/users/lookup', payload);
  },

/* Services */
  listServices() {
    return this._fetch('GET', '/services');
  },
  getService(serviceId) {
    return this._fetch('GET', `/services/${serviceId}`);
  },

/* Chat */
  chat(userId, conversationId, message, language) {
    return this._fetch('POST', '/chat', {
      user_id: userId,
      conversation_id: conversationId ?? null,
      message,
      language,
    });
  },
  startConversation(userId) {
    return this._fetch('POST', '/chat/start', { user_id: userId });
  },
  saveMessage(conversationId, role, content) {
    return this._fetch('POST',`/chat/${conversationId}/messages`,{ role, content });
  },

/* Application */
  startApplication(userId, serviceId, conversationId) {
    return this._fetch('POST', '/applications', {
      user_id: userId,
      service_id: serviceId,
      conversation_id: conversationId ?? null,
    });
  },
  createApplication(userId, serviceId, conversationId) { 
    return this._fetch('POST', '/applications', {
      user_id: userId,
      service_id: serviceId,
      conversation_id: conversationId ?? null,
    });
  },
  getApplication(applicationId) {
    return this._fetch('GET', `/applications/${applicationId}`);
  },
  getApplicationDetail(applicationId) {
    return this._fetch('GET', `/applications/${applicationId}/detail`);
  },  
  saveApplicationData(applicationId, requirementId, value) {
    return this._fetch('PUT',`/applications/${applicationId}/data/${requirementId}`,
      { requirement_id: requirementId, value });
  },

  /* Payment */
  createPayment(applicationId, amount, gatewayReference = null) {
    return this._fetch('POST', `/payments/${applicationId}`, {payment_method: 'mobile_money',amount,gateway_reference: gatewayReference,});
  },

  /* Document upload */
  uploadDocument(applicationId, file, requirementId = null) {
    const fd = new FormData();
    fd.append('file', file);
    if (requirementId !== null) fd.append('requirement_id', String(requirementId));
    return this._fetchMultipart(`/uploads/${applicationId}`, fd);
  },
};

/* Session */
  async function initUser() {
    const existing = this.getUserId();
    if (existing) return existing;

    if (backendOnline) {
     const created = await API.createUser({ language: currentLang, guest: true });
      if (created?.id != null) {
        this.saveUserId(created.id);
        return created.id;
      }
    }  
    this.saveUserId(CONFIG.GUEST_USER_ID);
    return CONFIG.GUEST_USER_ID;
  } 

async function identify(phoneNumber) {
  let user = await API.lookupUser(phoneNumber); 
  if (!user) user = await API.createUser(phoneNumber, currentLang);
  if (user?.id != null) {
    this.saveUserId(user.id);
    this.updateSessionDisplay();
    return user.id;
  }
  return this.getUserId();
}

async function hydrateServices() {
  if (!backendOnline) return;
  const services = await API.listServices();
  if (!Array.isArray(services)) return;

  const byName = new Map(
    services.map(s => [String(s.name ?? '').trim().toLowerCase(), s])
  );
  Object.values(KB).forEach(svc => {
    const match = byName.get(svc.backendName.trim().toLowerCase());
    if (match?.id != null) svc.backendId = match.id;
  });
}
function kbFromBackendId(backendId) {
  if (backendId == null) return null;
  return Object.values(KB).find(svc => svc.backendId === backendId) ?? null;
}

async function beginApplication(svc) {
  const userId    = SESSION.getUserId() ?? CONFIG.GUEST_USER_ID;
  const serviceId = svc.backendId; 
  if (serviceId == null) {
    console.warn(`[APP] No backend service_id for "${svc.id}"— is hydrateServices() done?`);
    return null;
  }
  return API.startApplication(userId, serviceId, SESSION.conversationId);
}

async function sendMessage() {
  const raw = textInput.value.trim();
  if (!raw || isBusy) return;

  textInput.value = '';
  autoGrow(textInput);
  isBusy = true;
  sendBtn.disabled = true;

  const detected = detectLanguage(raw);
  if (detected !== currentLang) setLanguage(detected);

  appendMessage('citizen', raw);
  showTyping();

  const localMatches = retrieveServices(raw, currentLang);

  let replyText   = null;
  let cardService = null;
  let grounded    = false;
  let usedBackend = false;

  if (CONFIG.USE_BACKEND_CHAT && backendOnline) {
    const userId  = SESSION.getUserId() ?? CONFIG.GUEST_USER_ID;
    const openSvc = (!serviceCard.hidden && KB[serviceCard.dataset.serviceId]) || null;
    const res = await API.chat(
      userId, SESSION.conversationId, raw, currentLang, openSvc?.backendId ?? null
    );

    if (res?.assistant_message) {
      usedBackend = true;
      replyText   = res.assistant_message;

      if (res.conversation_id) {
        SESSION.conversationId = res.conversation_id;
        SESSION.updateSessionDisplay();
      }
      if (res.user_id != null) SESSION.saveUserId(res.user_id);
      cardService = kbFromBackendId(res.service_id) ||
                    (localMatches.length === 1 ? localMatches[0] : null);
      grounded    = res.service_id != null || cardService != null;
    }
  }

  if (!usedBackend) {
    const convId = await ensureConversation();
    if (convId) API.saveMessage(convId, 'user', raw).catch(() => {});
    await new Promise(r => setTimeout(r, 600 + Math.random() * 400));
    replyText   = buildLocalResponse(localMatches, currentLang);
    cardService = localMatches.length === 1 ? localMatches[0] : null;
    grounded    = localMatches.length === 1;
    if (convId) API.saveMessage(convId, 'assistant', replyText).catch(() => {});
  }

  hideTyping();

  appendMessage('assistant', replyText, { badge: grounded ? true : undefined });
  if (cardService) showServiceCard(cardService);
  speak(replyText, currentLang);

  isBusy = false;
  sendBtn.disabled = false;
  textInput.focus();
}
async function init() {
  initSpeechRecognition();
  if (window.speechSynthesis) window.speechSynthesis.onvoiceschanged = () => {};
  const online = await API.checkHealth();
  setStatusBar(online);
  await hydrateServices();
  await SESSION.initUser();
  setLanguage('en');
  appendMessage('assistant', UI.en.greeting);

  SESSION.updateSessionDisplay();
}

init();