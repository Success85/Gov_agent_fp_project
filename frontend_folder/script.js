'use strict';
const CONFIG = {
  BACKEND_URL: 'http://127.0.0.1:5500',
  GUEST_USER_ID: 1,
  USE_BACKEND_CHAT: false,
};
/*Knowlegde Base [KB] */
const KB = {
  national_id: {
    id: 'national_id',
    backendName: 'National ID',
    backendId: null,
    name:     { en: 'National ID Application',         rw: 'Gusaba Indangamuntu',             fr: 'Demande de carte d\'identité' },
    category: { en: 'Identification',                  rw: 'Imyambabanire',                   fr: 'Identification' },
    fee_rwf: 500,
    requirements: [
      { en: 'Birth certificate',        rw: 'Icyemezo cy\'amavuko',    fr: 'Acte de naissance',        mandatory: true  },
      { en: 'Passport-size photo',      rw: 'Ifoto ya pasiporo',        fr: 'Photo d\'identité',        mandatory: true  },
      { en: 'Proof of residence',       rw: 'Icyemezo cy\'aho utuye',   fr: 'Justificatif de domicile', mandatory: false },
    ],
    steps: [
      { en: 'Provide your personal details',         rw: 'Tanga amakuru yawe bwite',                    fr: 'Fournir vos informations personnelles'       },
      { en: 'Upload the required documents',         rw: 'Ohereza inyandiko zisabwa',                   fr: 'Téléverser les documents requis'            },
      { en: 'Pay 500 RWF via Mobile Money',          rw: 'Ishyura amafaranga 500 RWF ukoresheje MoMo',  fr: 'Payer 500 RWF via Mobile Money'             },
      { en: 'Receive your reference number by SMS',  rw: 'Akire nimero y\'ibimenyetso kuri SMS',        fr: 'Recevoir votre numéro de référence par SMS' },
      { en: 'Collect your ID at the sector office',  rw: 'Hera indangamuntu yawe ku biro by\'umurenge', fr: 'Récupérer votre carte au bureau du secteur' },
    ],
  },
  birth_certificate: {
    id: 'birth_certificate',
    backendName: 'Birth Certificate',
    backendId: null,
    name:     { en: 'Birth Certificate',  rw: 'Icyemezo cy\'amavuko', fr: 'Acte de naissance' },
    category: { en: 'Family',             rw: 'Umuryango',             fr: 'Famille' },
    fee_rwf: 500,
    requirements: [
      { en: 'National ID numbers of both parents', rw: 'Nimero z\'indangamuntu y\'ababyeyi', fr: 'Numéros de carte d\'identité des parents', mandatory: true  },
      { en: 'Hospital birth notification letter',  rw: 'Ibaruwa y\'ibitaro cy\'amavuko',     fr: 'Lettre de naissance de l\'hôpital',        mandatory: false },
    ],
    steps: [
      { en: 'Enter the child\'s and parents\' details', rw: 'Injiza amakuru y\'umwana n\'ababyeyi',            fr: 'Saisir les informations de l\'enfant et des parents' },
      { en: 'Upload supporting documents',               rw: 'Ohereza inyandiko zishyigikira',                 fr: 'Téléverser les documents justificatifs'             },
      { en: 'Submit for sector office review',           rw: 'Ohereza ku biro by\'umurenge kugira ngo birebwe',fr: 'Soumettre pour examen au bureau du secteur'        },
      { en: 'Pay 500 RWF via Mobile Money',              rw: 'Ishyura amafaranga 500 RWF ukoresheje MoMo',     fr: 'Payer 500 RWF via Mobile Money'                    },
      { en: 'Download the certified certificate',        rw: 'Manura icyemezo cyemejwe',                       fr: 'Télécharger le certificat certifié'                 },
    ],
  },
  health_insurance: {
    id: 'health_insurance',
    backendName: 'Health Insurance',
    backendId: null,
    name:     { en: 'Mutuelle (Health Insurance) Renewal', rw: 'Kwishyura Ubwishingizi bw\'Ubuzima', fr: 'Renouvellement de la mutuelle de santé' },
    category: { en: 'Health',                              rw: 'Ubuzima',                             fr: 'Santé' },
    fee_rwf: 3000,
    requirements: [
      { en: 'National ID number',                      rw: 'Nimero y\'indangamuntu',         fr: 'Numéro de carte d\'identité',           mandatory: true },
      { en: 'List of household members to be covered', rw: 'Urutonde rw\'abagize umuryango', fr: 'Liste des membres du ménage à couvrir', mandatory: true },
    ],
    steps: [
      { en: 'Log in with your National ID number',           rw: 'Injira ukoresheje nimero y\'indangamuntu',          fr: 'Se connecter avec votre numéro de carte d\'identité' },
      { en: 'Confirm the household members to be covered',   rw: 'Emeza abagize umuryango bazishingirwa',             fr: 'Confirmer les membres du ménage à couvrir'          },
      { en: 'Review the total amount due',                   rw: 'Reba amafaranga yose agomba kwishyurwa',            fr: 'Vérifier le montant total dû'                       },
      { en: 'Pay via Mobile Money using the displayed code', rw: 'Ishyura ukoresheje MoMo ukoresheje kode igaragara', fr: 'Payer via Mobile Money avec le code affiché'        },
      { en: 'Receive your coverage confirmation',            rw: 'Akire icyemezo cy\'ubwishingizi bwawe',             fr: 'Recevoir la confirmation de votre couverture'       },
    ],
  },
  marriage_certificate: {
    id: 'marriage_certificate',
    backendName: 'Marriage Certificate',
    backendId: null,
    name:     { en: 'Marriage Certificate', rw: 'Icyemezo cy\'Ubukwe', fr: 'Acte de mariage' },
    category: { en: 'Family',               rw: 'Umuryango',            fr: 'Famille' },
    fee_rwf: 500,
    requirements: [
      { en: 'National IDs of both partners',           rw: 'Indangamuntu z\'ababiri bashakanye', fr: 'Cartes d\'identité des deux conjoints', mandatory: true },
      { en: 'Certificate of celibacy (no impediment)', rw: 'Icyemezo ko utarashakanye',          fr: 'Certificat de célibat',                 mandatory: true },
    ],
    steps: [
      { en: 'Both partners submit their personal details',      rw: 'Ababiri bashakanye batange amakuru yabo',          fr: 'Les deux conjoints soumettent leurs informations'   },
      { en: 'Upload all required documents',                    rw: 'Ohereza inyandiko zose zisabwa',                   fr: 'Téléverser tous les documents requis'               },
      { en: 'Schedule the civil ceremony at the sector office', rw: 'Gena itariki y\'umuhango ku biro by\'umurenge',    fr: 'Planifier la cérémonie civile au bureau du secteur' },
      { en: 'Attend the civil ceremony',                        rw: 'Taha mu muhango w\'ubukwe bw\' Leta',              fr: 'Assister à la cérémonie civile'                     },
      { en: 'Collect the certified marriage certificate',       rw: 'Hera icyemezo cy\'ubukwe cyemejwe',               fr: 'Récupérer l\'acte de mariage certifié'              },
    ],
  },
  driving_license: {
    id: 'driving_license',
    backendName: 'Driving License',
    backendId: null,
    name:     { en: 'Driving License Application',    rw: 'Gusaba Uruhushya rwo Gutwara Imodoka', fr: 'Demande de permis de conduire' },
    category: { en: 'Transport',                      rw: 'Ubutwererane',                         fr: 'Transport' },
    fee_rwf: 30000,
    requirements: [
      { en: 'National ID',                        rw: 'Indangamuntu',                     fr: 'Carte d\'identité nationale',    mandatory: true  },
      { en: 'Medical fitness certificate',        rw: 'Icyemezo cy\'ubuzima bwiza',        fr: 'Certificat d\'aptitude médicale',mandatory: true  },
      { en: 'Proof of driving school completion', rw: 'Icyemezo cyo kurangiza amasomo',    fr: 'Preuve de fin d\'auto-école',    mandatory: false },
    ],
    steps: [
      { en: 'Register for the theory exam online', rw: 'Iyandikishe ku kizamini cy\'amategeko kuri interineti', fr: 'S\'inscrire à l\'examen théorique en ligne' },
      { en: 'Pass the theory exam',                rw: 'Tsinda ikizamini cy\'amategeko',                        fr: 'Réussir l\'examen théorique'                },
      { en: 'Pass the practical driving test',     rw: 'Tsinda ikizamini cy\'imyitozo',                         fr: 'Réussir le test de conduite pratique'        },
      { en: 'Pay the license fee of 30,000 RWF',   rw: 'Ishyura amafaranga 30,000 RWF y\'uruhushya',            fr: 'Payer les frais de permis de 30 000 RWF'    },
      { en: 'Collect your driving license',        rw: 'Hera uruhushya rwawe rwo gutwara',                      fr: 'Récupérer votre permis de conduire'          },
    ],
  },
};

/* TEXT */
const LANG_CODES = { rw: 'rw-RW', en: 'en-US', fr: 'fr-FR' };

const UI = {
  rw: {
    placeholder:    'Andika ikibazo cyawe hano…',
    statusOnline:   'Wahuye kuri GovAgent — amakuru ashingiye ku byemejwe bya Irembo',
    statusOffline:  'Imikorere yo hanze ntiboneka — gukorana mu buryo bwo hanze',
    greeting:       'Muraho! Ndi GovAgent, umufasha wawe muri serivisi za Leta kuri Irembo.\n\nBaza ikibazo cyawe mu Kinyarwanda, Icyongereza, cyangwa Igifaransa — nzakumenyesha uko usabwa gutera intambwe.',
    quickHeading:   'Serivisi zihari',
    voiceHeading:   'Gusoma ibisubizo mu mvugo',
    voiceOn:        'Rya',
    voiceOff:       'Siyo',
    voiceNote:      'Ibisubizo bizasomwa mu mvugo nyuma y\'igisubizo cyose.',
    infoHeading:    'Ibisobanuro',
    infoNote:       'GovAgent igufasha mu serivisi za Irembo mu Kinyarwanda, Icyongereza, cyangwa Igifaransa. Amakuru yose avuye mu nyandiko yemejwe za Irembo.',
    scLabel:        'Amabwiriza ya Serivisi',
    scSource:       'Inkomoko: amakuru yemejwe ya Irembo',
    scReqHeading:   'Ibisabwa',
    scStepsHeading: 'Intambwe',
    feeSuffix:      ' RWF',
    badgeVerified:  'Bishingiye ku makuru yemejwe',
    badgeGeneral:   'Ibisubizo rusange',
    listening:      'Ndumva… vuga ikibazo cyawe.',
    noSpeech:       'Ubwo buryo bwo kuvuga ntibushoboka muri iyi porogaramu.',
    noMatch:        'Mbabarira, ntibonetse amakuru ku kibazo cyawe. Gerageza uviburitsaho nk\'aya: "gusaba indangamuntu" cyangwa "kwishyura ubwishingizi".',
    optional:       '(si itegeko)',
    sessionLabel:   'Umukoresha',
    convLabel:      'Ikiganiro',
  },
  en: {
    placeholder:    'Type your question here…',
    statusOnline:   'Connected to GovAgent — answers grounded in verified Irembo data',
    statusOffline:  'Backend unreachable — running in local mode',
    greeting:       'Hello! I\'m GovAgent, your assistant for Rwandan government services on Irembo.\n\nAsk your question in Kinyarwanda, English, or French and I will guide you step by step.',
    quickHeading:   'Available services',
    voiceHeading:   'Read replies aloud',
    voiceOn:        'On',
    voiceOff:       'Off',
    voiceNote:      'Replies will be read aloud after each response.',
    infoHeading:    'About GovAgent',
    infoNote:       'GovAgent guides you through Irembo government services in Kinyarwanda, English, or French. All service data is sourced from verified Irembo documentation.',
    scLabel:        'Service Guide',
    scSource:       'Source: verified Irembo data',
    scReqHeading:   'Requirements',
    scStepsHeading: 'Steps',
    feeSuffix:      ' RWF',
    badgeVerified:  'Grounded in verified data',
    badgeGeneral:   'General response',
    listening:      'Listening… please speak your question.',
    noSpeech:       'Voice input is not supported in this browser.',
    noMatch:        'I couldn\'t find a specific match for that. Try asking about a service like "national ID", "birth certificate", or "health insurance".',
    optional:       '(optional)',
    sessionLabel:   'User',
    convLabel:      'Conversation',
  },
  fr: {
    placeholder:    'Tapez votre question ici…',
    statusOnline:   'Connecté à GovAgent — réponses basées sur les données vérifiées d\'Irembo',
    statusOffline:  'Serveur inaccessible — mode local actif',
    greeting:       'Bonjour ! Je suis GovAgent, votre assistant pour les services gouvernementaux rwandais sur Irembo.\n\nPosez votre question en kinyarwanda, anglais ou français et je vous guiderai pas à pas.',
    quickHeading:   'Services disponibles',
    voiceHeading:   'Lire les réponses à voix haute',
    voiceOn:        'Actif',
    voiceOff:       'Inactif',
    voiceNote:      'Les réponses seront lues à voix haute après chaque réponse.',
    infoHeading:    'À propos de GovAgent',
    infoNote:       'GovAgent vous guide à travers les services Irembo en kinyarwanda, anglais ou français. Toutes les informations sont issues de la documentation officielle Irembo.',
    scLabel:        'Guide de service',
    scSource:       'Source : données Irembo vérifiées',
    scReqHeading:   'Pièces requises',
    scStepsHeading: 'Étapes',
    feeSuffix:      ' FRW',
    badgeVerified:  'Basé sur des données vérifiées',
    badgeGeneral:   'Réponse générale',
    listening:      'Écoute en cours… posez votre question.',
    noSpeech:       'La saisie vocale n\'est pas prise en charge dans ce navigateur.',
    noMatch:        'Je n\'ai pas trouvé de correspondance précise. Essayez de demander un service comme "carte d\'identité", "acte de naissance" ou "mutuelle".',
    optional:       '(optionnel)',
    sessionLabel:   'Utilisateur',
    convLabel:      'Conversation',
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

/* DOM references */
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
  await hydrateServices();
  await Promise.all([
    SESSION.initUser(),
    loadServicesFromBackend(),
]);
  setLanguage('en');
  appendMessage('assistant', UI.en.greeting);

  SESSION.updateSessionDisplay();
}

init();