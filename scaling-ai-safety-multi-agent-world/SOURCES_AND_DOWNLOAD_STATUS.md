# Sources and Download Status

## Retrieval policy

The canonical inventory was extracted from the Schmidt Sciences call page on 2026-06-19. Duplicate call-page citations to Chan et al. (2025) and Conitzer and Oesterheld (2023) were deduplicated. Open manuscripts were downloaded from the cited source, an author's page, arXiv, OpenReview, PMLR, or the official publisher. A full text was not substituted when the source exposed only a book/article record or when authorization was unclear.

**Call page:** [Scaling AI Safety for a Multi-Agent World](https://schmidtsciences.smapply.io/prog/scaling_ai_safety_for_a_multi_agent_world/)

## Coverage

| Source type | Count | Local treatment |
|---|---:|---|
| Scholarly works with validated open PDFs | 36 | Stored under the primary category's `papers/` directory |
| Scholarly works without an authorized open PDF located | 4 | Canonical source and metadata/summary retained |
| Cited non-paper context source | 1 | Link and summary retained |
| Unique sources represented | 41 | All indexed in `MASTER_PAPER_INDEX.md` |

## Metadata-only scholarly works

| Work | Reason no local PDF is included | Preserved source |
|---|---|---|
| Dafoe et al. (2021), *Cooperative AI: Machines Must Learn to Find Common Ground* | The cited Nature commentary page did not expose a downloadable open manuscript. | [Nature](https://www.nature.com/articles/d41586-021-01170-0) and `metadata/pages/dafoe2021.html` |
| Minsky (1986), *The Society of Mind* | The citation is a copyrighted book record, not an open paper. | [ACM record](https://dl.acm.org/doi/abs/10.5555/22939) and `metadata/pages/minsky1986.html` |
| Huberman, ed. (1988), *The Ecology of Computation* | The citation is a copyrighted edited book record, not an open paper. | [ACM record](https://dl.acm.org/doi/10.5555/59160) and `metadata/pages/huberman1988.html` |
| Szabo and Teo (2015), *Formalization of Weak Emergence in Multiagent Systems* | The institutional and ACM records expose citation metadata and an abstract, but no clearly authorized downloadable manuscript was located. | [ACM](https://dl.acm.org/doi/10.1145/2815502), [Adelaide record](https://digital.library.adelaide.edu.au/dspace/handle/2440/107734), `metadata/crossref_szabo2015.json` |

## Context-only source

Google's [A2A protocol announcement](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/) is included because the call cites it, but it is not counted among the 40 scholarly works.

## Validation

`metadata/extract_pdf_metadata.py` opens every PDF with `pypdf`, records the page count and embedded metadata, and extracts a text sample from the first three pages. The latest run produced 36 records and zero parser errors. `SHA256SUMS.txt` provides a content checksum for each archived PDF.

## Reproducibility cautions

- Publisher landing pages and preprints can change after retrieval; use the checksums and source snapshot when exact version identity matters.
- Several 2026 works were recent preprints or conference versions at retrieval time. Claims should be checked against later camera-ready versions before formal citation.
- A downloadable PDF does not imply permission to redistribute it under a new license. Follow each original license and publisher's terms.
- The category assignment is analytical, not supplied by the paper authors. Cross-category relevance is discussed in the summaries.
