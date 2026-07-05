'use strict';
const CONFIG = {
  BACKEND_URL: 'http://127.0.0.1:5500',
  GUEST_USER_ID: 1,
};

const KB = {
  national_id: {
    id: 'national_id',
    backendName: 'National ID',
    backendId: null,
    name:     { en: 'National ID Application',         rw: 'Gusaba Indangamuntu',             fr: 'Demande de carte d\'identité' },
    category: { en: 'Identification',                  rw: 'Imyambabanire',                   fr: 'Identification' },
    fee_rwf: 500,
    requirements: [
      { en: 'Birth certificate',           rw: 'Icyemezo cy\'amavuko',         fr: 'Acte de naissance',          mandatory: true  },
      { en: 'Passport-size photo',         rw: 'Ifoto ya pasiporo',             fr: 'Photo d\'identité',          mandatory: true  },
      { en: 'Proof of residence',          rw: 'Icyemezo cy\'aho utuye',        fr: 'Justificatif de domicile',   mandatory: false },
    ],
    steps: [
      { en: 'Provide your personal details',        rw: 'Tanga amakuru yawe bwite',                   fr: 'Fournir vos informations personnelles'       },
      { en: 'Upload the required documents',        rw: 'Ohereza inyandiko zisabwa',                  fr: 'Téléverser les documents requis'            },
      { en: 'Pay 500 RWF via Mobile Money',         rw: 'Ishyura amafaranga 500 RWF ukoresheje MoMo', fr: 'Payer 500 RWF via Mobile Money'             },
      { en: 'Receive your reference number by SMS', rw: 'Akire nimero y\'ibimenyetso kuri SMS',       fr: 'Recevoir votre numéro de référence par SMS' },
      { en: 'Collect your ID at the sector office', rw: 'Hera indangamuntu yawe ku biro by\'umurenge',fr: 'Récupérer votre carte au bureau du secteur' },
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
      { en: 'National ID numbers of both parents',    rw: 'Nimero z\'indangamuntu y\'ababyeyi', fr: 'Numéros de carte d\'identité des parents', mandatory: true  },
      { en: 'Hospital birth notification letter',     rw: 'Ibaruwa y\'ibitaro cy\'amavuko',     fr: 'Lettre de naissance de l\'hôpital',        mandatory: false },
    ],
    steps: [
      { en: 'Enter the child\'s and parents\' details', rw: 'Injiza amakuru y\'umwana n\'ababyeyi',           fr: 'Saisir les informations de l\'enfant et des parents' },
      { en: 'Upload supporting documents',               rw: 'Ohereza inyandiko zishyigikira',                fr: 'Téléverser les documents justificatifs'             },
      { en: 'Submit for sector office review',           rw: 'Ohereza ku biro by\'umurenge kugira ngo birebwe',fr: 'Soumettre pour examen au bureau du secteur'        },
      { en: 'Pay 500 RWF via Mobile Money',              rw: 'Ishyura amafaranga 500 RWF ukoresheje MoMo',    fr: 'Payer 500 RWF via Mobile Money'                    },
      { en: 'Download the certified certificate',        rw: 'Manura icyemezo cyemejwe',                      fr: 'Télécharger le certificat certifié'                 },
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
      { en: 'Log in with your National ID number',           rw: 'Injira ukoresheje nimero y\'indangamuntu',         fr: 'Se connecter avec votre numéro de carte d\'identité' },
      { en: 'Confirm the household members to be covered',   rw: 'Emeza abagize umuryango bazishingirwa',            fr: 'Confirmer les membres du ménage à couvrir'          },
      { en: 'Review the total amount due',                   rw: 'Reba amafaranga yose agomba kwishyurwa',           fr: 'Vérifier le montant total dû'                       },
      { en: 'Pay via Mobile Money using the displayed code', rw: 'Ishyura ukoresheje MoMo ukoresheje kode igaragara',fr: 'Payer via Mobile Money avec le code affiché'        },
      { en: 'Receive your coverage confirmation',            rw: 'Akire icyemezo cy\'ubwishingizi bwawe',            fr: 'Recevoir la confirmation de votre couverture'       },
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
    name:     { en: 'Driving License Application',       rw: 'Gusaba Uruhushya rwo Gutwara Imodoka', fr: 'Demande de permis de conduire' },
    category: { en: 'Transport',                         rw: 'Ubutwererane',                         fr: 'Transport' },
    fee_rwf: 30000,
    requirements: [
      { en: 'National ID',                           rw: 'Indangamuntu',                      fr: 'Carte d\'identité nationale',   mandatory: true  },
      { en: 'Medical fitness certificate',           rw: 'Icyemezo cy\'ubuzima bwiza',         fr: 'Certificat d\'aptitude médicale',mandatory: true  },
      { en: 'Proof of driving school completion',    rw: 'Icyemezo cyo kurangiza amasomo',     fr: 'Preuve de fin d\'auto-école',   mandatory: false },
    ],
    steps: [
      { en: 'Register for the theory exam online',  rw: 'Iyandikishe ku kizamini cy\'amategeko kuri interineti', fr: 'S\'inscrire à l\'examen théorique en ligne' },
      { en: 'Pass the theory exam',                 rw: 'Tsinda ikizamini cy\'amategeko',                        fr: 'Réussir l\'examen théorique'                },
      { en: 'Pass the practical driving test',      rw: 'Tsinda ikizamini cy\'imyitozo',                         fr: 'Réussir le test de conduite pratique'        },
      { en: 'Pay the license fee of 30,000 RWF',    rw: 'Ishyura amafaranga 30,000 RWF y\'uruhushya',            fr: 'Payer les frais de permis de 30 000 RWF'    },
      { en: 'Collect your driving license',         rw: 'Hera uruhushya rwawe rwo gutwara',                      fr: 'Récupérer votre permis de conduire'          },
    ],
  },
};

const LANG_CODES = { rw: 'rw-RW', en: 'en-US', fr: 'fr-FR' };

const UI = {
  rw: {
    placeholder:      'Andika ikibazo cyawe hano…',
    statusOnline:     'Wahuye kuri GovAgent — amakuru ashingiye ku byemejwe bya Irembo',
    statusOffline:    'Imikorere yo hanze ntiboneka — gukorana mu buryo bwo hanze',
    greeting:         'Muraho! Ndi GovAgent, umufasha wawe muri serivisi za Leta kuri Irembo.\n\nBaza ikibazo cyawe mu Kinyarwanda, Icyongereza, cyangwa Igifaransa — nzakumenyesha uko usabwa gutera intambwe.',
    quickHeading:     'Serivisi zihari',
    voiceHeading:     'Gusoma ibisubizo mu mvugo',
    voiceOn:          'Rya',
    voiceOff:         'Siyo',
    voiceNote:        'Ibisubizo bizasomwa mu mvugo nyuma y\'igisubizo cyose.',
    infoHeading:      'Ibisobanuro',
    infoNote:         'GovAgent igufasha mu serivisi za Irembo mu Kinyarwanda, Icyongereza, cyangwa Igifaransa. Amakuru yose avuye mu nyandiko yemejwe za Irembo.',
    scLabel:          'Amabwiriza ya Serivisi',
    scSource:         'Inkomoko: amakuru yemejwe ya Irembo',
    scReqHeading:     'Ibisabwa',
    scStepsHeading:   'Intambwe',
    feeSuffix:        ' RWF',
    badgeVerified:    'Bishingiye ku makuru yemejwe',
    badgeGeneral:     'Ibisubizo rusange',
    listening:        'Ndumva… vuga ikibazo cyawe.',
    noSpeech:         'Ubwo buryo bwo kuvuga ntibushoboka muri iyi porogaramu.',
    noMatch:          'Mbabarira, ntibonetse amakuru ku kibazo cyawe. Gerageza uviburitsaho nk\'aya: "gusaba indangamuntu" cyangwa "kwishyura ubwishingizi".',
    optional:         '(si itegeko)',
    sessionLabel:     'Umukoresha',
    convLabel:        'Ikiganiro',
  },
  en: {
    placeholder:      'Type your question here…',
    statusOnline:     'Connected to GovAgent — answers grounded in verified Irembo data',
    statusOffline:    'Backend unreachable — running in local mode',
    greeting:         'Hello! I\'m GovAgent, your assistant for Rwandan government services on Irembo.\n\nAsk your question in Kinyarwanda, English, or French and I will guide you step by step.',
    quickHeading:     'Available services',
    voiceHeading:     'Read replies aloud',
    voiceOn:          'On',
    voiceOff:         'Off',
    voiceNote:        'Replies will be read aloud after each response.',
    infoHeading:      'About GovAgent',
    infoNote:         'GovAgent guides you through Irembo government services in Kinyarwanda, English, or French. All service data is sourced from verified Irembo documentation.',
    scLabel:          'Service Guide',
    scSource:         'Source: verified Irembo data',
    scReqHeading:     'Requirements',
    scStepsHeading:   'Steps',
    feeSuffix:        ' RWF',
    badgeVerified:    'Grounded in verified data',
    badgeGeneral:     'General response',
    listening:        'Listening… please speak your question.',
    noSpeech:         'Voice input is not supported in this browser.',
    noMatch:          'I couldn\'t find a specific match for that. Try asking about a service like "national ID", "birth certificate", or "health insurance".',
    optional:         '(optional)',
    sessionLabel:     'User',
    convLabel:        'Conversation',
  },

  fr: {
    placeholder:      'Tapez votre question ici…',
    statusOnline:     'Connecté à GovAgent — réponses basées sur les données vérifiées d\'Irembo',
    statusOffline:    'Serveur inaccessible — mode local actif',
    greeting:         'Bonjour ! Je suis GovAgent, votre assistant pour les services gouvernementaux rwandais sur Irembo.\n\nPosez votre question en kinyarwanda, anglais ou français et je vous guiderai pas à pas.',
    quickHeading:     'Services disponibles',
    voiceHeading:     'Lire les réponses à voix haute',
    voiceOn:          'Actif',
    voiceOff:         'Inactif',
    voiceNote:        'Les réponses seront lues à voix haute après chaque réponse.',
    infoHeading:      'À propos de GovAgent',
    infoNote:         'GovAgent vous guide à travers les services Irembo en kinyarwanda, anglais ou français. Toutes les informations sont issues de la documentation officielle Irembo.',
    scLabel:          'Guide de service',
    scSource:         'Source : données Irembo vérifiées',
    scReqHeading:     'Pièces requises',
    scStepsHeading:   'Étapes',
    feeSuffix:        ' FRW',
    badgeVerified:    'Basé sur des données vérifiées',
    badgeGeneral:     'Réponse générale',
    listening:        'Écoute en cours… posez votre question.',
    noSpeech:         'La saisie vocale n\'est pas prise en charge dans ce navigateur.',
    noMatch:          'Je n\'ai pas trouvé de correspondance précise. Essayez de demander un service comme "carte d\'identité", "acte de naissance" ou "mutuelle".',
    optional:         '(optionnel)',
    sessionLabel:     'Utilisateur',
    convLabel:        'Conversation',
  },
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

