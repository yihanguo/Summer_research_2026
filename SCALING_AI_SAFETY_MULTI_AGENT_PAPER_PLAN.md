# Planned Next Steps: Scaling AI Safety for a Multi-Agent World

Source call: [Schmidt Sciences, *Scaling AI Safety for a Multi-Agent World*](https://schmidtsciences.smapply.io/prog/scaling_ai_safety_for_a_multi_agent_world/)

Status: **Planning only.** No cited papers have been downloaded, categorized into final records, summarized, committed, or pushed yet.

## Objective

Build a complete, reproducible reading package for every scholarly paper or research report cited by the funding call. The package will:

1. preserve the call's four official research clusters;
2. assign every paper to a primary category and one or more subcategories;
3. download openly accessible paper files where permitted;
4. provide concise and technical Markdown summaries;
5. record unresolved, paywalled, superseded, or non-paper references explicitly; and
6. commit and push the categorized corpus and summaries to the GitHub repository associated with the Group Meeting directory.

## Planned Taxonomy

The four large categories below follow the research agenda on the source page.

### 1. Sandboxes and Testbeds

Subcategories:

- **Stylized games and simulated societies:** game-based, social-simulation, and generative-agent environments.
- **High-fidelity frontier-agent environments:** persistent tool use, memory, economic constraints, and realistic communication.
- **Scalability, fidelity, and external validity:** proxy models, simulation-to-deployment validity, and population scaling.
- **Reproducibility, interoperability, and logging:** common interfaces, cross-testbed compatibility, and multi-agent trace collection.

### 2. The Science of Agent Networks

Subcategories:

- **Individual-to-system safety:** how individual objectives, capabilities, cooperation, defection, and manipulability shape collective outcomes.
- **Network vulnerabilities and cascading failures:** adversarial sub-populations, attack propagation, robustness, and red teaming.
- **Emergent capabilities, communication, and scaling laws:** topology, heterogeneity, population size, tools, resources, volatility, and phase transitions.
- **Collective agency foundations:** formal definitions and operational measures of collective goals, agency, and capability.
- **Dangerous emergent capabilities and goals:** shutdown resistance, safety-filter decomposition, covert channels, resource accumulation, and collective influence.

### 3. Strengthening Agent Infrastructure

Subcategories:

- **Identity, authentication, and admission control:** agent IDs, proof-of-agent, proof-of-human, revocation, cloning, merging, and platform access.
- **Verifiable attributes, actions, and provenance:** authorization scope, output attribution, watermarking, proofs of inference, and privacy-preserving verification.
- **Reputation, accountability, and dispute resolution:** behavior aggregation, gaming resistance, incident tracking, renegotiation, and termination.
- **Commitments and delegation:** credible and conditional commitments, delegation chains, scope attenuation, revocation, contract compliance, Sybil resistance, and malicious delegates.

### 4. Multi-Agent Oversight and Control

Subcategories:

- **Collusion and covert-communication detection:** undesirable coordination, emergent languages, steganography, and partial-observation monitoring.
- **Failure attribution and oversight interfaces:** responsible-agent, interaction, step, and delegation-chain attribution; runtime visualization and querying.
- **Multi-agent control and scalable oversight:** secure harnesses, task allocation, cross-principal trust boundaries, red/blue-team control evaluations, and intervention policies.
- **Mechanism and information design:** cooperation-promoting mechanisms, anti-collusion mechanisms, selective information disclosure, circuit breakers, desynchronization, and action-rate limits.

## Phase 1: Build the Citation Inventory

1. Extract every linked citation from the overview, inspiration papers, earlier-work paragraph, and all four research clusters.
2. Record each source-page citation label, displayed author/year, link target, and the section/subcategory in which it appears.
3. Resolve each item to canonical metadata: full title, complete authors, year, venue or preprint status, DOI/arXiv/OpenReview identifier, and canonical landing page.
4. Deduplicate papers cited in multiple parts of the call while retaining every category relationship.
5. Separate the corpus into:
   - scholarly papers and technical reports to download and summarize;
   - programme theses and research-agenda reports to summarize separately;
   - protocols, blog posts, policies, and other non-paper links to inventory but not mislabel as papers.
6. Produce an audit table showing retrieved, inaccessible, ambiguous, duplicate, superseded, and non-paper items.

## Phase 2: Download and Organize the Papers

Planned repository layout:

```text
scaling-ai-safety-multi-agent-world/
├── README.md
├── CITATION_INVENTORY.md
├── CATEGORY_INDEX.md
├── SOURCES.md
├── 01_sandboxes_testbeds/
│   ├── papers/
│   └── SUMMARY.md
├── 02_science_agent_networks/
│   ├── papers/
│   └── SUMMARY.md
├── 03_strengthening_agent_infrastructure/
│   ├── papers/
│   └── SUMMARY.md
└── 04_multi_agent_oversight_control/
    ├── papers/
    └── SUMMARY.md
```

Download rules:

- Prefer author, arXiv, OpenReview, conference, institutional, or other openly accessible canonical PDFs.
- Preserve the original publication file when available; do not manufacture a PDF from a landing page.
- Use stable filenames: `YEAR_FirstAuthor_ShortTitle.pdf`.
- Do not bypass paywalls or access controls. For inaccessible papers, retain metadata and an official source link with an explicit access note.
- Store one physical copy of a paper under its primary category. Record secondary-category relationships in the indexes to avoid duplicate binaries.
- Verify that every downloaded file opens, has a plausible page count, and matches the intended title and authors.

## Phase 3: Categorize the Corpus

For each paper:

1. assign one **primary large category**;
2. assign at least one **subcategory**;
3. optionally assign secondary categories when the contribution genuinely spans clusters;
4. record why the paper belongs there in one sentence; and
5. distinguish papers cited as motivation, evidence, benchmark/testbed, infrastructure primitive, or proposed control mechanism.

Borderline cases will be resolved according to the paper's primary technical contribution, not merely the paragraph in which the funding call cites it.

## Phase 4: Read and Summarize Every Paper

Each paper record will include:

| Field | Planned content |
|---|---|
| Citation | Canonical title, authors, year, and venue/status |
| Category | Primary category, subcategory, and secondary tags |
| Motivation | The multi-agent safety problem being addressed |
| Scenario | Number/type of agents, principals, environment, tools, observability, and interaction topology |
| Threat or failure model | Collusion, conflict, cascade, manipulation, covert communication, infrastructure abuse, oversight failure, or other risk |
| Method | Core theoretical, experimental, cryptographic, benchmark, monitoring, or control approach |
| Benchmarks/data | Environments, datasets, tasks, baselines, and evaluation protocol |
| Metrics | Safety, capability, detection, attribution, robustness, cost, scalability, or validity metrics |
| Main findings | Quantified results where available |
| Limitations | Assumptions, external-validity gaps, scale limits, and missing controls |
| Relevance to the call | Exact connection to the cited research cluster |
| Reproducibility | Code, data, model, project page, license, and replication notes |
| Source links | Paper, PDF, code, data, and project links |

Summary deliverables:

- one `SUMMARY.md` per large category;
- one compact table covering every paper;
- one deeper subsection per paper;
- a cross-category synthesis in `README.md` describing gaps, overlaps, benchmark coverage, and promising proposal directions.

## Phase 5: Quality Assurance

Before committing:

1. compare the final citation inventory against every scholarly link on the source page;
2. confirm that each inventory item is either summarized or explicitly marked non-paper/inaccessible/ambiguous;
3. validate titles, authors, years, venues, and canonical URLs against primary sources;
4. verify every local PDF against its metadata;
5. check that all four categories contain coherent subcategories and that cross-listed papers are traceable;
6. check Markdown links and relative PDF paths;
7. distinguish confirmed conference papers from preprints and reports;
8. avoid presenting inferred interpretations as claims made by the source paper; and
9. review the repository diff so unrelated local changes are not staged.

## Phase 6: GitHub Delivery

1. inspect the Group Meeting repository status and remote;
2. add only the new paper package and summary files;
3. leave unrelated files such as `.DS_Store` untouched;
4. commit with a focused message such as `Add categorized multi-agent safety paper corpus`;
5. push the current repository branch to its configured GitHub remote; and
6. report the commit hash, branch, remote, paper count, download count, inaccessible count, and generated Markdown files.

## Completion Criteria

The later retrieval task will be complete only when:

- every scholarly paper/report cited by the call has an inventory disposition;
- every accessible paper has been downloaded and verified;
- every paper has a category, subcategory, summary, benchmark/data description, and source links;
- the four category summaries and overall synthesis are present;
- inaccessible and non-paper references are transparent rather than silently omitted; and
- the scoped changes have been committed and pushed successfully.

## Planned Execution Order

1. Citation extraction and canonicalization.
2. Four-category assignment with subcategories.
3. Open-access PDF retrieval and file verification.
4. Paper reading and structured summaries.
5. Cross-paper synthesis and repository indexes.
6. Completeness and link QA.
7. Scoped Git commit and push.

Execution will begin only after this plan is reviewed or the user asks to proceed.
