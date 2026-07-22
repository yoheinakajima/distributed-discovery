# Research governance

## Purpose

Distributed Discovery is the umbrella research program on collective search
under dispersed information. Its formal object is a discovery architecture:
the rules that convert evidence into a portfolio of search actions. This
document governs how research evidence becomes a theorem family, manuscript,
program synthesis, or reusable infrastructure. It does not create evidence or
change the status of any claim.

## Output hierarchy

1. **Research program.** Distributed Discovery is the only umbrella program.
   “Discovery architecture” remains the common-noun formal object, not a new
   program name.
2. **Theorem family.** A durable mathematical question that can contain
   several studies and may eventually support an archival paper.
3. **Program or work package.** A sequential research arc with a bounded
   execution order and explicit promotion gates.
4. **Registered study.** The smallest evidence-producing unit. A study owns
   its model, configuration, source, run, proof or certificate, claim records,
   and report.
5. **Archival theorem paper.** A manuscript that owns one substantial theorem
   family and passes the admission rule below.
6. **Working note.** A useful intermediate, expository, or synthetic document
   that need not be submitted as standalone original research.
7. **Living synthesis.** *The Architecture of Distributed Discovery:
   Foundations, Results, and Open Problems* is the maintained account of the
   complete program. It cites and organizes theorem papers and studies; it does
   not automatically claim their novelty.
8. **Infrastructure.** DiscoveryBench, Labs, schemas, exact verifiers, claim
   ledgers, and audit tooling support evidence and reuse without becoming
   theorem papers merely because they are substantial.

A registered study is evidence infrastructure, not automatically a paper. A
program orders work; a theorem family owns a mathematical question; a paper
owns an editorial argument; the synthesis owns the program-level account.

## Archival-paper admission rule

A study or program becomes an archival-paper candidate only when all five
conditions hold:

1. it has a distinct central question;
2. it has a title-level result capable of carrying the abstract;
3. it has a natural literature and referee set;
4. it has a self-contained reason to exist if every other project document is
   ignored; and
5. it is unlikely, before the next declared theorem gate, to become merely a
   preliminary section of an already active theorem program.

None of the following is sufficient: an exact run, a large claim count, a
polished website, twenty pages, a parameter extension, or a collection of
bounded examples without a distinct theorem-family result.

Admission creates an editorial candidate, not a submission decision. Paper
status, submission authority, DOI authority, and release authority remain
separate.

## Editorial workflow

1. A registered study produces evidence.
2. Its theorem family decides whether one or several studies belong together.
3. The admission gate decides whether an archival manuscript is justified.
4. The living synthesis integrates results regardless of paper status.
5. No manuscript is submitted, released, or assigned a DOI without explicit
   owner authorization.
6. Every paper has one primary theorem-family owner.
7. Supporting claims may appear in several documents, but their primary
   ownership and source provenance remain explicit.
8. A theorem gate, not a calendar date, determines whether a working paper is
   held for generalization.

## Evidence and mapping rules

Research-evidence outputs name a registered study ID, and generated numerical
claims name immutable run IDs. Program governance and synthesis documents need
not invent a study ID; whenever they surface a scientific claim they map it to
existing study and claim IDs. Definitions, analytic results, exact bounded
computations, independent reproductions, certified bounds, estimates,
conjectures, nulls, failures, and editorial recommendations retain their
distinct labels.

The machine-readable ownership view is
[`paper-family-map.yml`](paper-family-map.yml). The living-synthesis maps are
under [`synthesis/architecture-of-distributed-discovery/`](../synthesis/architecture-of-distributed-discovery/).

## Single-lane execution

Only one substantive branch and pull request may be active. Roadmap and
documentation closeout branches merge before the next substantive branch
starts. Study registration, evidence execution, claim audit, editorial
disposition, and public integration therefore occur sequentially, even when
they contribute to the same theorem family.
