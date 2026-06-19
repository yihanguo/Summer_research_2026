# Scaling AI Safety for a Multi-Agent World: Reading Package

This package organizes every scholarly work cited on the Schmidt Sciences call page, **Scaling AI Safety for a Multi-Agent World**, into the call's four research themes and their subcategories. It also includes the cited Google A2A announcement as a non-paper context source.

## Corpus at a glance

- **40 scholarly works:** research papers, technical reports, programme theses, commentaries, and two foundational books.
- **36 locally archived open PDFs:** each was opened and text-validated with `pypdf`.
- **4 metadata-only scholarly works:** Dafoe et al. (2021), Minsky (1986), Huberman (1988), and Szabo and Teo (2015). No clearly authorized open full-text PDF was exposed by the cited source, so the package preserves source metadata rather than an unofficial copy.
- **1 non-paper context source:** Google's A2A interoperability announcement.
- **Source snapshot date:** 2026-06-19.

The cited publication year and the year printed in a downloaded version can differ. For example, the call links a 2025 preprint of *Causal Foundations of Collective Agency*, while the archived manuscript identifies its PMLR/CLeaR publication as 2026. The index records the version found at retrieval time.

## Navigation

| File | Purpose |
|---|---|
| [MASTER_PAPER_INDEX.md](MASTER_PAPER_INDEX.md) | One-row-per-source map of category, subcategory, local artifact, and canonical link. |
| [01 Sandboxes and Testbeds](01_sandboxes_testbeds/SUMMARY.md) | Games, simulated societies, open-world evaluations, and testbed design. |
| [02 Science of Agent Networks](02_science_agent_networks/SUMMARY.md) | System-level risk, network failures, emergence, collective agency, and dangerous collective behavior. |
| [03 Strengthening Agent Infrastructure](03_strengthening_agent_infrastructure/SUMMARY.md) | Identity, verification, attribution, accountability, markets, commitments, and delegation. |
| [04 Multi-Agent Oversight and Control](04_multi_agent_oversight_control/SUMMARY.md) | Collusion detection, failure attribution, control protocols, and system-level security. |
| [SOURCES_AND_DOWNLOAD_STATUS.md](SOURCES_AND_DOWNLOAD_STATUS.md) | Coverage, access status, provenance, and validation notes. |
| [metadata/pdf_extracts.json](metadata/pdf_extracts.json) | Machine-readable page counts, embedded metadata, and first-three-page text samples. |

## Classification method

Each item is assigned one **primary** category and subcategory according to the problem it most directly helps solve, not merely the application used in its experiments. Many papers span themes. For example, secret collusion is scientifically a network-level emergent risk and operationally an oversight problem; Motwani et al. is placed under network vulnerabilities because its central contribution is a threat model, while Rose et al. is placed under oversight because its central contribution is a detector.

The summaries distinguish four evidence types:

1. **Conceptual or agenda-setting:** defines a field, risk model, or research programme.
2. **Formal:** proves properties in a mathematical model or gives a formal definition.
3. **Controlled empirical:** evaluates agents in games, benchmarks, or simulations.
4. **Open-world empirical:** studies a long-horizon task with real deployment constraints.

## Reading path

For a fast field overview, read Hammond et al. (2025), Chan et al. (2025), and Shah et al. (2025), then use the category summaries to move from diagnosis to evaluation and control. For work on step-level estimates of undesirable multi-agent behavior, the most relevant bridge is:

`network-risk model -> sandbox/testbed -> calibrated detector or attribution score -> thresholded intervention -> system-level evaluation`

The current corpus contains strong pieces of this chain, especially failure attribution, suspiciousness-threshold control, mutual-information collusion detection, and activation-based group detection. It does not yet supply one general algorithm that unifies calibrated per-step risk prediction with reinforcement-learning self-correction across arbitrary MAS environments; that remains a credible research gap.

## Reuse and citation

The PDFs remain subject to their publishers' and authors' licenses. This repository is a research index, not a relicensing of the papers. Cite the original work through the canonical links in the master index.
