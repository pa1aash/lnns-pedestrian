# E1 data

- `E1_runs.jsonl`: one record per run (job_id `<mode>_<seed>`, modes E1a published-reproduction, E1b corrected-forward; seeds 42-241). Written by `experiments/E1/e1_library.py` in the pilot phase; snapshot paths `exec/data/library/...` refer to the copies in `library/` (`e1lib.snap_path`).
  The field `deadlock_type` (contact-cluster grouping) is superseded by the keystone classes in `data/derived/E1_keystone.json` (plan change C12) and is not used in the text.
- `library/`: deadlock snapshots (393).
- `keystone.jsonl`: keystone test (`experiments/E1/keystone.py`), jobs K1 / K2 / K1b per snapshot.
