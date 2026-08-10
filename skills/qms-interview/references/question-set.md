# Interview question set

Ask conversationally, in roughly this order. Skip anything already present
in `qms.config.json`; confirm stored values instead. Answers marked (config)
map directly into the config schema; the rest inform Phase C drafting.

## 1. Products

- What devices do you make or sell? Names and one-line descriptions. (config: company.device_types)
- What is each device's intended use, and who are the intended users?
- Single-use or reusable? Sterile or non-sterile?
- Does any device contain software, or is the device itself software
  (standalone/SaMD vs embedded)? (config: scope.software_in_product)

## 2. Classification and regulatory pathway

- For each target market: what class is the device, and under which rule or
  pathway (EU MDR class and rule, US 510(k)/De Novo/PMA, UK)? Record
  answers with `[verify: classification to be confirmed]` unless the user
  states it has been formally determined.
- Who is the legal manufacturer? Any authorised representatives, importers,
  or distributors in the chain? (config: company.regulatory_role)

## 3. Lifecycle activities

- Do you design and develop the devices yourselves? (config: scope.design)
- Who manufactures: in-house, contract manufacturer, or both?
- Do you install devices at customer sites? (config: scope.installation)
- Do you service or maintain devices after sale? (config: scope.servicing)
- How are devices distributed (direct, distributors, online)?

## 4. Processes and outsourcing

- Walk through production from incoming materials to shipped product. What
  are the key steps?
- Which processes are outsourced? (config: scope.outsourced_processes)
- Are any process outputs impossible to fully verify afterwards, so the
  process itself must be validated - e.g. sterilisation, welding, sealing,
  moulding? (config: scope.process_validation)
- Is any product supplied sterile, or do you sterilise (in-house or
  subcontracted)? What method? (config: scope.sterilisation)

## 5. Environment and equipment

- Do the devices need a controlled work environment - cleanroom, ESD
  control, particulate or bioburden limits? (config: scope.contamination_control)
- Do you use measuring or monitoring equipment whose accuracy affects
  whether product conforms - gauges, testers, fixtures? (config: scope.measuring_equipment)
- Do you hold customer property - materials, equipment, designs,
  confidential information? (config: scope.customer_property)
- Do devices need special storage, handling, or transport conditions -
  cold chain, humidity, shelf life? (config: scope.special_preservation)

## 6. People and sites

- Who is the quality manager / management representative? (config: quality_manager)
- Company registration number and registered office? (config: company.registration_number, company.registered_office)
- What sites do you operate, and what happens at each? (config: company.operating_sites)
- Roughly how many people, and who wears the quality and regulatory hats?

## 7. Post-market

- Which markets do you sell into today, and which are planned? (config: company.markets)
- How do complaints reach you (channels), and who handles them?
- Are you aware of the vigilance reporting obligations in each market? Note
  gaps with `[verify: ...]` for SOP-16 drafting.

## 8. Standards landscape

- Which standards do you already work to or hold certificates for? Typical
  set: ISO 14971 (risk), IEC 62304 (software), IEC 60601 family
  (electrical), ISO 10993 (biocompatibility).
- Is ISO 27001 / information security management in scope for this QMS?
  (config: scope.isms_in_scope)

## 9. Records and tooling

- Where do quality records live today (paper, shared drive, other systems)?
- Any retention-period expectations from customers or regulators?
- Is the vault under git, or on a shared drive? (config: doc_control_mode)
