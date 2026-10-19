# ATSight Experiments - Systems Paper Harness

Experiment harness for a systems paper on ATSight, an AI resume-job
matching engine with ATS simulation. Tests whether the scorer is
deterministic, how scores distribute across resume quality tiers, and
what the scorer actually relies on.

## Results (verified Oct 2026)

- **Determinism**: one resume scored 10 times, all 10 runs returned 95.0.
  The scorer is fully deterministic.
- **Distribution** (50-resume synthetic corpus, 5 tiers of 10):
  strong 94.9, average 77.3, thin 39.0, poor_format 16.4.
  Headline finding: **keyword-stuffed resumes score lower than balanced
  ones (69.0 vs 77.3)**. Stuffing keywords backfires.
- **Ablation** (one strong resume, one degradation at a time):
  nonstandard section headers hurt most (-15.0), then removing the skills
  section (-13.5), then removing contact email or quantified numbers
  (-8.0 each).

Raw numbers live in `results/` (scores.csv, determinism.csv, ablation.csv).

**Not done yet**: Experiment 3, a human ranking study (materials in
`human-study/`), has not been run. No human-study results are reported here.

## What's here

- `run_experiments.py` - the harness (imports `ats_scorer` from the
  ATSight repo; see Reproducing below).
- `corpus/` - the 50-resume synthetic corpus plus `generate_corpus.py`
  and `manifest.csv`. All resumes are synthetic; no real personal data.
- `results/` - the verified result CSVs.
- `human-study/` - ranking sheet and 10 sample resumes for the
  not-yet-run human study, plus the answer key.

## Reproducing

Needs Python 3.9+ (stdlib only). The harness imports the ATS scorer:

1. Get `ats_scorer.py` from the ATSight repo
   (github.com/SuryaG12/resume-analyzer, `backend/ats_scorer.py`)
   and place it next to `run_experiments.py`, or adjust the
   `sys.path` line at the top of the script.
2. Run `python run_experiments.py`.

## License

MIT - see LICENSE.
