# Service Data Sources

This file records where the verified service data in `data/services/` comes from, so
every requirement, step, and fee can be traced back to an official source. Where sources
disagreed, the judgment call made is documented here.

**Platform note:** all services are delivered through IremboGov
(https://irembo.gov.rw), the Rwandan government's official e-services platform. Figures
below were confirmed as of the research date; fees and processing times can change, so
re-check before a final submission or public demo.

Research date: 2026-07

---

## National ID (`national_id.json`)

- **Issuing body:** National Identification Agency (NIDA)
- **Fee:** 500 RWF
- **Processing time:** ~30 days
- **Eligibility:** Rwandan citizen, 16 years and above
- **Requirements:** Citizen Application Number (Child ID), a valid phone number, an email address
- **Application channel:** online via IremboGov, followed by biometric capture and
  collection at the applicant's chosen sector office

**Sources:**
- IremboGov — National ID service page (https://irembo.gov.rw)
- NIDA — National Identification Agency (https://nida.gov.rw)

---

## Birth Certificate (`birth_certificate.json`)

- **Issuing body:** Ministry of Local Government (MINALOC), processed at sector level
- **Fee:** 500 RWF
- **Processing time:** ~1 working day
- **Requirements:** National ID number or Citizen Application Number, a valid phone number, an email address
- **Format:** downloadable e-certificate with lifetime validity; can be requested for
  oneself or on behalf of a child
- **Application channel:** online via IremboGov; issued after the sector Executive
  Secretary approves the request

**Sources:**
- IremboGov — Birth Certificate service page (https://irembo.gov.rw)
- MINALOC — Ministry of Local Government (https://minaloc.gov.rw)

---

## Documented judgment calls

Real sources were not always fully consistent. Where they differed, the following
decisions were made and applied to the data:

1. **Phone number vs. email (both services).** Some official pages list "a valid phone
   number and an email address" as required, while others phrase it as "a phone number,
   an email address, or both." We marked **both** as `mandatory: true` — the stricter
   reading — because requesting both is safe and matches the requirement stated on at
   least one authoritative page. If a teammate confirms only one is truly required, the
   `mandatory` flag on the email requirement can be relaxed.

2. **No document uploads for either service.** The real IremboGov flows for both services
   retrieve the applicant's details from their ID / Citizen Application Number rather than
   taking document uploads. Every requirement is therefore `needs_upload: false`. This is
   an accuracy decision, not an oversight — a service requiring a genuine upload will be
   introduced as the third service in a later sprint.

3. **Facts without a database column.** The data model has no field for issuing body or
   processing time. To keep these verified facts available to the assistant, they were
   folded into each service's `description` and `steps` text rather than dropped.