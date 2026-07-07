# Labeling Quality (Noise Control)

Problem
- Simple keyword labeling tends to produce "label bags" (many tags) which degrades retrieval precision in RAG systems.

Baseline solution in this pack
- LABELING_MIN_V2 adds deterministic scoring on top of rule-based matching:
  - weighted occurrences (title/headings/body)
  - minimum occurrences per label
  - cap max labels per label_type
  - deduplication
  - primary label selection (highest score per type)

Where output goes
- To keep strict schemas unchanged, primary labels and scoring details are emitted under:
  - chunk_record.extensions.labeling

Determinism
- All scoring is rule-based, reproducible, and stable across runs given identical text.
