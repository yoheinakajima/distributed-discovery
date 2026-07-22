# Frozen analysis plan

Primary analyses are intent-to-treat regressions of the registered outcome on the
registered treatment contrast and randomization-block fixed effects, with session-
clustered uncertainty. Participant-averaged outcomes handle repeated rounds. Holm
correction applies within frozen multiplicity families; the power study uses the
more conservative Bonferroni family alpha.

The fixed sample rule prohibits outcome-dependent stopping. Duplicate synthetic IDs,
assignments outside the manifest, and pre-treatment simulator failures are the only
registered exclusions. Missing outcomes remain missing in ITT; inverse-probability
weighting is sensitivity-only. No primary model controls for a post-treatment variable.

The v2 attention contrasts use the same ITT, fixed-sample, session-clustered
framework. H9, H10, H13, and H14 are corrected within the attention family;
H11 and H12 are corrected within the implementation family. Public-signal use,
one-reader alignment, off-signal rescue, and contrarian action are outcomes,
never exclusions or post-treatment controls. All eleven response scenarios and
every below-threshold power row remain reported.

V3 preserves those families and adds three threshold hypotheses (H15–H17) and
three dynamic hypotheses (H18–H20). Bonferroni power thresholds are calculated
within the frozen families. Fourteen response scenarios, six sample sizes, and
1,000 replications are fixed in advance; all calibration failures remain in
the public table. The stopping treatment changes the synthetic task horizon,
not the fixed simulation sample or the prohibition on outcome-dependent study
stopping.
