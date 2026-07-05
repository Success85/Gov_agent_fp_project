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
  