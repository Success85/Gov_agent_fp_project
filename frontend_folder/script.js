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
/* Language Detection and Retrieval */
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

/* Local Response */
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
    return await res.json();
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

/* Users */
  async createUser(phoneNumber = null, preferredLanguage = 'rw') {  
  try {
    return await this._fetch('POST', '/users', {
        phone_number:       phoneNumber,
        preferred_language: preferredLanguage,
      });
    } catch (err) {
      console.error('[API] createUser failed:', err);
      return null;
    }
  },
  async lookupUser(phonenumber) {
    try {
      return await this._fetch('POST', '/users/lookup', {phonenumber: phoneNumber});
    } catch (err) {
      console.error('[API] lookupUser failed:', err);
      return null;
    }
  },

/* Services */
  async listServices() {
    try {
      return await this._fetch('GET', '/services');
    } catch (err) {
      console.error('[API] listServices failed:', err);
      return null;
    }
  },
  async getService(serviceId) {
    try {
      return await this._fetch('GET', `/services/${serviceId}`);
    } catch (err) {
      console.error('[API] getService failed:', err);
      return null;
    }
  },

/* Chat */
  async startConversation(userId) {
    try {
      return await this._fetch('POST', '/chat/start', { user_id: userId });
    } catch (err) {
      console.error('[API] startCoversation failed:', err);
      return null;
    }
  },
  saveMessage(conversationId, role, content, language = currentLang) {
    try {
      return await this._fetch('POST',`/chat/${conversationId}/messages`,{ role, content, language });
    } catch (err) {
      console.error('[API] saveMessage failed:', err);
      return null;
    }
  },

/* Application */
  async startApplication(userId, serviceId, conversationId = null) {
    try {
      return await this._fetch('POST', '/applications/start', {
        user_id: userId,
        service_id: serviceId,
        conversation_id: conversationId,
      });
    } catch (err) {
      console.error('[API] startApplicationFlow failed:', err);
      return null;
    }
  },
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
  async getApplicationDetail(applicationId) {
    try {
      return await this._fetch('GET', `/applications/${applicationId}/detail`);
    } catch (err) {
      console.error('[API] getApplication failed:', err);
      return null;
    }
  },  

  async saveApplicationData(applicationId, requirementId, value) {
    try {
      return await this._fetch('PUT',`/applications/${applicationId}/data/${requirementId}`,
      { requirement_id: requirementId, value });
    } catch (err) {
      console.error('[API] saveApplicationData failed:', err);
      return null;
    }
  },

  /* Payment */
  async createPayment(applicationId, amount, gatewayReference = null) {
    try {
      return await this._fetch('POST', `/payments/${applicationId}`, {payment_method: 'mobile_money',amount,gateway_reference: gatewayReference,});
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
};

/* Load Service */
async function loadServicesFromBackend() {
  const services = await API.listServices();
  if (!Array.isArray(services)) return;
  services.forEach(backendSvc => {
    const localEntry = Object.values(KB).find(
      k => k.backendName.toLowerCase() === backendSvc.name.toLowerCase()
    );
    if (localEntry) {
      localEntry.backendId = backendSvc.id;
      if (backendSvc.fee != null) {
        localEntry.fee_rwf = Number(backendSvc.fee);
      }
    }
  });
  console.log('[KB] backendId values synced from GET /services');
}

/* Chat Pipeline */
let currentLang   = 'en';
let isBusy        = false;
let backendOnline = false;

async function ensureConversation() {
  if (SESSION.conversationId) return SESSION.conversationId;
  const userId = SESSION.getUserId() ?? CONFIG.GUEST_USER_ID;
  const conv   = await API.startConversation(userId);
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
  isBusy           = true;
  sendBtn.disabled = true;

  const detected = detectLanguage(raw);
  if (detected !== currentLang) setLanguage(detected, false);

  appendMessage('citizen', raw);
  showTyping();
  const convId = await ensureConversation();
  if (convId) {
    API.saveMessage(convId, 'user', raw, currentLang).catch(() => {});
  }

  let replyText; 
  let grounded   = false;
  let usedBackend = false;

  if (convId && backendOnline) {
    try {
      const backendReply = await API.getChatReply(convId, raw, currentLang);
      if (backendReply?.content) {
        replyText   = backendReply.content;
        grounded    = true;
        usedBackend = true;
      }
    } catch (err) {
      console.warn('[chat] getChatReply failed, using local fallback:', err);
    }
  }
  if (!usedBackend) {
    await new Promise(r => setTimeout(r, 600 + Math.random() * 400));
    const matches = retrieveServices(raw, currentLang);
    replyText = buildLocalResponse(matches, currentLang);
    grounded  = matches.length === 1;
    if (matches.length === 1) showServiceCard(matches[0]);
  }

  hideTyping();
  appendMessage('assistant', replyText, { badge: grounded });

  if (convId) {
    API.saveMessage(convId, 'assistant', replyText, currentLang).catch(() => {});
  }

  speak(replyText, currentLang);
  isBusy           = false;
  sendBtn.disabled = false;
  textInput.focus();
}

/* Text-to-Speech and Speech-to-Text */
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
let isRecording = false;
let recognizer  = null;

function initSpeechRecognition() {
  const SRImpl = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SRImpl) return;

  recognizer                = new SRImpl();
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
  if (!recognizer) { voiceNoteEl.textContent = UI[currentLang].noSpeech; return; }
  if (isRecording) {
    recognizer.stop();
  } else {
    recognizer.lang = LANG_CODES[currentLang] || 'en-US';
    try { recognizer.start(); } catch (_) {}
  }
}

/* Session */
  const SESSION = {
  STORAGE_KEY_USER:  'govagent_user_id',
  STORAGE_KEY_PHONE: 'govagent_phone',   

  getUserId() {
    const stored = localStorage.getItem(this.STORAGE_KEY_USER);
    if (stored) return Number(stored);
    return null;
  },

  saveUserId(id) {
    localStorage.setItem(this.STORAGE_KEY_USER, String(id));
  },
  getPhone() {
    return localStorage.getItem(this.STORAGE_KEY_PHONE) || null;
  },
  savePhone(phone) {
    localStorage.setItem(this.STORAGE_KEY_PHONE, phone);
  },

  conversationId: null,

  async initUser() {
    const existingId = this.getUserId();
    if (existingId) return existingId;
    const phone = this.getPhone();

    try {
      if (phone) {
        const found = await API.lookupUser(phone);
        if (found?.id) {
          this.saveUserId(found.id);
          return found.id;
        }
      }

    const created = await API.createUser({ language: currentLang, guest: true });
      if (created?.id) {
        this.saveUserId(created.id);
        return created.id;
      }
    } catch (err) {
        console.warn('[SESSION] initUser failed, falling back to GUEST_USER_ID:', err);
    }
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

/* Sidebar */
function setLanguage(lang) {
  currentLang = lang;

  document.querySelectorAll('.lang-btn').forEach(btn => {
    const active = btn.dataset.lang === lang;
    btn.classList.toggle('active', active);
    btn.setAttribute('aria-pressed', String(active));
  });

  const ui = UI[lang];
  textInput.placeholder         = ui.placeholder;
  statusText.textContent        = backendOnline ? ui.statusOnline : ui.statusOffline;
  quickHeading.textContent      = ui.quickHeading;
  voicePanelHeading.textContent = ui.voiceHeading;
  voicePanelNote.textContent    = ui.voiceNote;
  infoHeading.textContent       = ui.infoHeading;
  infoNote.textContent          = ui.infoNote;
  voiceToggleLabel.textContent  = speakEnabled ? ui.voiceOn : ui.voiceOff;

  buildQuickList();
  SESSION.updateSessionDisplay();

  if (!serviceCard.hidden) {
    const id = serviceCard.dataset.serviceId;
    if (id && KB[id]) showServiceCard(KB[id]);
  }
}

/* Language Switcher */
function setLanguage(lang) {
  currentLang = lang;

  document.querySelectorAll('.lang-btn').forEach(btn => {
    const active = btn.dataset.lang === lang;
    btn.classList.toggle('active', active);
    btn.setAttribute('aria-pressed', String(active));
  });

  const ui = UI[lang];
  textInput.placeholder         = ui.placeholder;
  statusText.textContent        = backendOnline ? ui.statusOnline : ui.statusOffline;
  quickHeading.textContent      = ui.quickHeading;
  voicePanelHeading.textContent = ui.voiceHeading;
  voicePanelNote.textContent    = ui.voiceNote;
  infoHeading.textContent       = ui.infoHeading;
  infoNote.textContent          = ui.infoNote;
  voiceToggleLabel.textContent  = speakEnabled ? ui.voiceOn : ui.voiceOff;

  buildQuickList();
  SESSION.updateSessionDisplay();

  if (!serviceCard.hidden) {
    const id = serviceCard.dataset.serviceId;
    if (id && KB[id]) showServiceCard(KB[id]);
  }
}

/* DOM Helpers and references */
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
  const msg     = document.createElement('div');
  msg.className = `msg ${sender}`;

  const bubble     = document.createElement('div');
  bubble.className = 'msg-bubble';
  sender === 'assistant' ? renderMarkdown(bubble, text) : (bubble.textContent = text);
  msg.appendChild(bubble);

  if (opts.badge !== undefined) {
    const badge       = document.createElement('span');
    badge.className   = `grounding-badge ${opts.badge ? 'verified' : 'general'}`;
    badge.textContent = opts.badge ? UI[currentLang].badgeVerified : UI[currentLang].badgeGeneral;
    msg.appendChild(badge);
  }

  if (sender !== 'system') {
    const time       = document.createElement('span');
    time.className   = 'msg-time';
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
  if (indicator) indicator.style.background = online ? 'var(--success)' : '#e8a800';
  if (statusText) {
    statusText.textContent = online
      ? UI[currentLang].statusOnline
      : UI[currentLang].statusOffline;
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