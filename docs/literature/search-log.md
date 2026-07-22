# Literature search log — DD-000

## Protocol

Searches prioritize publisher, society, institutional repository, DOI, and author/preprint records. Metadata is checked against at least the pinned upstream bibliography and one stable record before entering `bibliography/references.bib`. This M2 pass is an orientation review, not a systematic review or novelty certificate. Access date for all entries below: **2026-07-20 UTC**.

## Searches and screening

| Query/theme | Primary records retained | Relevance decision |
|---|---|---|
| Blackwell comparison of experiments | Blackwell (1953), DOI `10.1214/aoms/1177729032` | Direct foundation for comparing information experiments; frontier monotonicity still needs feasibility/emulation assumptions. |
| Team decision and organizations | Marschak & Radner (1972), Yale Cowles monograph record | Direct prior art for common-payoff agents with decentralized information and decision functions; central to DD-001. |
| Bayesian persuasion / information design | Kamenica & Gentzkow (2011), AEA record, DOI `10.1257/aer.101.6.2590` | Direct adjacent framework for designed disclosure and induced actions; DD-002 adds multi-searcher coverage/equilibrium. |
| Organizational exploration | March (1991), INFORMS, DOI `10.1287/orsc.2.1.71` | Direct adjacent theory of exploration/exploitation and diversity loss; richer dynamic objective than atomic coverage. |
| Division of cognitive labor | Kitcher (1990), Journal of Philosophy record, DOI `10.2307/2026796` | Direct adjacent work on allocating scientific effort across approaches. |
| Epistemic communication networks | Zollman (2007), DOI `10.1086/525605` | Direct adjacent simulation evidence on communication structure, reliability, and convergence; not the same as action protocol design. |
| Collective experiment choice | Rzhetsky et al. (2015), PNAS/PMC, DOI `10.1073/pnas.1509757112` | Direct application-level prior art on redundant/failed scientific experiments and coordinated discovery. |
| Submodular/adaptive coverage | Nemhauser, Wolsey & Fisher (1978), DOI `10.1007/BF01588971`; Golovin & Krause (2011), DOI `10.1613/jair.3278` | Direct mathematical tools for DD-004/DD-005; top-L atomic ranking does not carry over unchanged. |
| Covering games and incentives | Vetta (2002), DOI `10.1109/SFCS.2002.1181966`; Gairing (2009), DOI `10.1007/978-3-642-10841-9_18` | Direct prior art for coverage welfare and price-of-anarchy analysis; avoid general novelty claims for the bound/mechanism family. |
| Information harming congestion outcomes | Acemoglu et al. (2018), INFORMS, DOI `10.1287/opre.2017.1712` | Direct adjacent informational Braess paradox; mechanism differs because costs/route equilibrium replace discovery coverage. |
| Multi-agent/robot coverage redundancy | Hazon & Kaminka (2008), DOI `10.1016/j.robot.2008.01.006` | Adjacent use of redundancy/coverage with robustness tradeoffs; warns that duplication can be useful outside atomic perfect execution. |
| Phrase collision: “distributed discovery” | Wang et al. (2026), arXiv:`2603.14312`; service/resource/news-discovery search results | Material terminology collision. The present project must always define its action-allocation sense and make no unique-name/field claim. |

## Stable records consulted

- https://cowles.yale.edu/research/cfm-22-economic-theory-teams
- https://www.aeaweb.org/articles?id=10.1257/aer.101.6.2590
- https://pubsonline.informs.org/doi/abs/10.1287/orsc.2.1.71
- https://pmc.ncbi.nlm.nih.gov/articles/PMC4664375/
- https://aaai-21.aaai.org/Library/JAIR/Vol42/jair42-012.php
- https://www.pdcnet.org/jphil/content/jphil_1990_0087_0001_0005_0022
- https://arxiv.org/abs/2603.14312

No copyrighted PDF is stored in this repository.

## DD-016 threshold-discovery pass (2026-07-22 UTC)

This focused review retained primary or stable records for threshold public
goods, volunteer dilemmas, congestion games, club formation, hedonic coalition
stability, strong and coalition-proof equilibrium, and mutation-based
selection. The reviewed objects all predate DD-016. The study-specific evidence
map and stable records are in
studies/DD-016-threshold-discovery/literature.md. This is not a systematic
review or novelty certificate.

## DD-011 focused experimental-design pass (2026-07-21 UTC)

This targeted orientation search used publisher, society, PubMed, institutional,
DOI, OSF, and NIST records. It is not a systematic review or novelty certificate.

| Theme | Primary or stable records retained | Design implication |
|---|---|---|
| Costly information acquisition | Brocas, Carrillo & Palfrey (2012), DOI `10.1007/s00199-011-0615-9` | Acquisition can respond strategically to costs; motivates explicit source-price treatments without treating the DD-008 fixture as behavioral evidence. |
| Priority and scientific search | Tiokhin & Derex (2019), DOI `10.1098/rsos.180934` | Priority competition can change sampling in a research game; motivates attribution/protection but does not establish the proposed treatment effect. |
| Information and public goods | Cox & Stoddard (2021), DOI `10.1257/mic.20180275`; Fehr & Gächter (2000), DOI `10.1257/aer.90.4.980` | Communication, truthfulness, and contribution incentives are established experimental topics; disclosure and reward need separate factors. |
| Organizational communication | Evdokimov & Garfagnini (2019), DOI `10.3982/QE809` | Communication/coordination tradeoffs depend on organizational structure; supports separate disclosure and allocation treatments. |
| Group incentives | Nalbantian & Schotter (1997), *AER* 87(3):314–341 | Group-reward experiments are established; the DD-006B treatment is one model-specific mechanism comparison. |
| Venture syndication | Brander, Amit & Antweiler (2002), DOI `10.1111/j.1430-9134.2002.00423.x` | Syndication combines selection and value-added channels; it is an analogy, not evidence for this laboratory design. |
| Preregistration | Nosek et al. (2018), DOI `10.1073/pnas.1708274114`; OSF registration guidance | Predictions, analysis, stopping, and deviations should be frozen, while an unsubmitted template must not be called preregistered. |
| Power and sample justification | Lakens (2022), DOI `10.1525/collabra.33267` | Power is only one sample-size justification and is conditional on assumed effects and variance; report sensitivity and Monte Carlo uncertainty. |
| Fractional designs | NIST/SEMATECH e-Handbook sections 5.3.3.4.3–4 | Fractional designs trade run count for explicit aliasing; compare candidates and identify only registered contrasts. |

Stable records: `https://doi.org/10.1007/s00199-011-0615-9`,
`https://doi.org/10.1098/rsos.180934`, `https://www.aeaweb.org/articles?id=10.1257/mic.20180275`,
`https://doi.org/10.3982/QE809`, `https://doi.org/10.1073/pnas.1708274114`,
`https://doi.org/10.1525/collabra.33267`, and
`https://www.itl.nist.gov/div898/handbook/pri/section3/pri3344.htm`.

## Common-Source Trap paper pass (2026-07-21 UTC)

This focused review used publisher, journal, institutional-repository, and DOI
records. It is a targeted positioning review, not a systematic review or novelty
certificate.

| Theme | Primary records retained | Boundary for the paper |
|---|---|---|
| Private/social value of information | Hirshleifer (1971) | Information-acquisition externalities and differences between private and social value are established; DD-008B contributes a particular exact source-count threshold result. |
| Strategic experimentation as a public good | Bolton & Harris (1999); Keller, Rady & Cripps (2005) | Dynamic experimentation already exhibits free-riding, encouragement, role asymmetry, and inefficient rates; the current model is static and rewards one-shot target coverage. |
| Endogenous source attention and coordination | Hellwig & Veldkamp (2009); Myatt & Wallace (2012); Colombo, Femminis & Pavan (2014) | Strategic complementarity/substitutability and welfare wedges in information acquisition are established. The Common-Source theorem must be presented as a transparent specialization, not the discovery of acquisition inefficiency. |
| Costly social learning and source traps | Ali (2018); Liang & Mu (2020) | Costly information can strengthen herding, and correlated/complementary source choice can create learning traps. DD-008B has neither a social history nor asymptotic learning and therefore cannot inherit those claims. |
| Scientific division of labor | Kitcher (1990); Weisberg & Muldoon (2009); Zollman (2010); Alexander, Himmelreich & Thompson (2015) | Diversity and search allocation are established and model-sensitive; contrary results reinforce the need to state the target law and action technology exactly. |
| Functional problem-solving diversity | Hong & Page (2004); Rzhetsky et al. (2015) | Diverse heuristics and coordinated experiment portfolios have direct prior art; source independence is only one representation of diversity. |

Stable records consulted include DOI/publisher pages for
`10.1111/1468-0262.00022`, `10.1111/j.1468-0262.2005.00564.x`,
`10.1111/j.1467-937X.2008.00515.x`, `10.1093/restud/rdr018`,
`10.1093/restud/rdu015`, `10.1016/j.jet.2018.02.009`,
`10.1093/qje/qjz033`, `10.1086/644786`, `10.1007/s10670-009-9194-6`,
`10.1073/pnas.0403723101`, and `10.1086/681766`. No copyrighted paper is
stored in the repository.

## DD-012 selective-attention pass (2026-07-21 UTC)

This focused positioning pass used journal, publisher, DOI, and bibliographic
records. It is an orientation review, not a systematic review or novelty
certificate.

| Theme | Primary records retained | Boundary for DD-012 |
|---|---|---|
| Strategic ignorance and information avoidance | Carrillo & Mariotti (2000), DOI `10.1111/1467-937X.00142`; Golman, Hagmann & Loewenstein (2017), DOI `10.1257/jel.20151245` | Deliberate non-acquisition and avoidance are established. DD-012 uses a binding ex-ante access gate and does not model psychology or forgetting. |
| Rational inattention | Sims (2003), DOI `10.1016/S0304-3932(03)00029-1` | Scarce attention is established. DD-012 has no information-capacity constraint or endogenous signal precision. |
| Public-information welfare | Morris & Shin (2002), DOI `10.1257/000282802762024610`; Cornand & Heinemann (2008), DOI `10.1111/j.1468-0297.2008.02139.x` | Publicity can interact with coordination, and dissemination to a subset has direct prior art. DD-012's loss is duplicate target coverage under a fixed follow/private action class. |
| Endogenous attention and coordination | Hellwig & Veldkamp (2009); Myatt & Wallace (2012) | Strategic information acquisition and attention externalities are established. DD-012 contributes a finite exact specialization, not a general attention theory. |
| Informational herding and contrarian action | Smith, Sørensen & Tian (2021), DOI `10.1093/restud/rdab001`; Acemoglu et al. (2018) | Contrarianism and information-induced equilibrium losses have adjacent theory. DD-012 excludes contrarian policies; DD-014 is separately registered to study a bounded conditional class. |

Stable records consulted: `https://doi.org/10.1111/1467-937X.00142`,
`https://www.aeaweb.org/articles?id=10.1257/jel.20151245`,
`https://doi.org/10.1016/S0304-3932(03)00029-1`,
`https://www.aeaweb.org/articles?id=10.1257/000282802762024610`,
`https://doi.org/10.1111/j.1468-0297.2008.02139.x`, and
`https://doi.org/10.1093/restud/rdab001`. No copyrighted paper is stored in
the repository.
