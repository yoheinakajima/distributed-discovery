# arXiv freeze checklist

This is a readiness checklist, not a submission workflow. No arXiv submission,
identifier reservation, endorsement request, or external contact is
authorized.

For each paper:

- confirm one central question and paper-admission status;
- verify self-contained theorem statements and proofs;
- resolve every `logical-required` dependency;
- complete primary-source related work and conditional contribution language;
- preserve limitations, negative results, and counterboundaries;
- remove internal lab/process prose from the scholarly narrative while keeping
  evidence provenance;
- build a deterministic PDF and portable source bundle with no host paths;
- include every figure, bibliography input, and required style file;
- audit manuscript/figure/source licensing;
- validate current metadata and checksum;
- recheck current category, cross-list, endorsement, moderation, source, and
  license rules from official arXiv sources;
- record freeze blockers and exact next file.

Policy observations checked 2026-07-23:

- arXiv expects topical, refereeable, self-contained scholarly contributions;
- all submissions are moderated and may be reclassified or declined;
- first submission or a new category may require endorsement;
- TeX/LaTeX source is preferred and TeX-generated PDFs are not accepted as a
  PDF-only submission;
- `cs.AI` explicitly excludes Multiagent Systems, while `cs.MA` covers
  intelligent agents and coordinated interactions; `cs.GT` covers computer
  science/game-theory intersections.

Sources:

- <https://info.arxiv.org/help/submit/index.html>
- <https://info.arxiv.org/help/submit_tex.html>
- <https://info.arxiv.org/help/endorsement.html>
- <https://info.arxiv.org/help/moderation/index.html>
- <https://arxiv.org/category_taxonomy>

Category hypotheses are provisional. The current memo's `cs.AI` hypothesis
must not be hard-coded; a software-agent benchmark may fit `cs.MA`, while
theorem papers may fit `cs.GT` or another category depending on their actual
frozen content.
