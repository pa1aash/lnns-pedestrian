# CroMa human data (E10): provenance

Checked 2026-11-10 against DataCite, doi.org content negotiation, the archive landing page, the archive run-overview PDF, Adrian et al. 2020 (Europe PMC full text PMC7211470) and Boomers et al. (arXiv:2303.02319v2). BibTeX as fetched is in paper/refs.bib (fzj_ped20219, boomers2023data).

## 1. How the data were obtained (repo)

- `data/ext/croma/` (tracked): five PeTrack text exports plus `README.md`. README names the dataset as DOI 10.34735/ped.2021.9, CC BY 4.0, 25 fps, columns id, frame, x, y, z, markerID; it says the downloaded archive (`2021bottleneck_trajecories_txt.zip`) ships no readme or licence file.
- File headers: `# PeTrack project: 4D030_w080_l200_h0.pet`, etc.
- Used by `experiments/E10/e10_croma.py` (RUNS list), `experiments/E10/analyze.py`, `experiments/pilot/w28_croma.py`; human reference output `data/E10/human.json`. Same files under `/Users/palaash/Developer/lnns-pedestrian/data/ext/croma`.
- `code/sim/scenarios/croma.py`: geometry inferred from trajectory extents; "the archive has no geometry file".

## 2. The five runs (archive run overview PDF = Boomers et al. Table 19, App. A.9)

All on Monday 11.10.2021, Duesseldorf (Mitsubishi Electric Halle, path `2021.10.08_Duesseldorf_MEH_CroMa`), experimental site D, day 4.

| run | descriptive name | width w | length l | motivation | line-up | N (table) | ids in our file |
|---|---|---|---|---|---|---|---|
| 4D030 | w080_l200_h0 | 0.80 m | 2.00 m | h0 normal | 2 m semi-circle | 161 | 135 |
| 4D040 | w080_l200_h1 | 0.80 m | 2.00 m | h1 hurried | 2 m semi-circle | 160 | 136 |
| 4D110 | w080_l021_h0 | 0.80 m | 0.20 m | h0 normal | 2 m semi-circle (note: "mix up: first row queue behind") | 132 | 131 |
| 4D120 | w080_l021_h1 | 0.80 m | 0.20 m | h1 hurried | 2 m semi-circle | 132 | 129 |
| 4D130 | w080_l021_h2 | 0.80 m | 0.20 m | h2 full commitment | directly at bottleneck | 129 | 128 |

Points to note:
- The varied parameters are bottleneck width w and bottleneck **length** l, not a corridor width. The "2.0 m corridor" is a 2.0 m long bottleneck; the short one is a wall-like bottleneck of length **0.2 m** in both the overview PDF and Table 19. "l021" is only the run-name code; neither source gives 0.21 m.
- Motivation: 4D130 is h2 "full commitment" (instruction includes "pushes their way through"), not "hurried". The paper's "walked normally or hurried" omits it.
- "in four runs kept a 2 m semicircle clear": consistent with the table (4D030, 4D040, 4D110, 4D120); 4D130 lined up directly at the bottleneck.
- Participant numbers in the table (161, 160, 132, 132, 129) exceed the tracked ids in our files (135, 136, 131, 129, 128). Not resolved here; the hdf5/json metadata on the archive may explain it (likely persons not crossing / not tracked, unverified).
- Boomers Sec. 3.7: bottleneck widths 0.6, 0.7, 0.8, 1.0, 1.2, 1.6 m; lengths 0.2, 2.0 m; construction 4 m x 2 m x 1 m frames, visually extended to 6 m; finish line 8 m behind the bottleneck; coordinate origin at the front of the bottleneck walls, centred.

## 3. Dataset DOI 10.34735/PED.2021.9 (DataCite, fetched)

- Title: "Bottleneck experiments with varying motivation levels"
- Creators (8): Adrian, Juliane; Boomers, Ann Katrin; Feldmann, Sina; Kandler, Alica; Küpper, Mira; Wings, Carina; Boltes, Maik; Seyfried, Armin.
- Publisher: Forschungszentrum Jülich. Publication year: 2026 (DOI record created/registered 2026-03-24). Resource type: Collection.
- URL: https://ped.fz-juelich.de/da/2021bottleneck (site title "Pedestrian Dynamics Data Archive").
- rightsList: empty in DataCite. Licence on the landing page: wiki footer "content on this wiki is licensed under ... CC Attribution 4.0 International" (https://creativecommons.org/licenses/by/4.0/). No dataset-specific licence statement.
- Citation requested: none. The landing page has no "please cite" text; it points to the data guidance paper [1] (Boomers et al., Collective Dynamics 8, 2023) "for further information", and to an "Experiment outline and participant statistics" report (DOI 10.13140/RG.2.2.22099.07205).
- Landing page lists one results paper: Küpper & Adrian 2026 (PED2025 proceedings, Acta Polytechnica CTU Proceedings 57:209-215, DOI 10.14311/app.2026.57.0209). That paper analyses 0.7 m, l = 0.2 m runs (4D200, 4D210, 4D251, 4D290, 4D291), not the 0.8 m runs.
- Older citations of the same DOI (Boomers et al. ref [14]) give "Forschungszentrum Jülich, Bergische Universität Wuppertal, Ruhr-Universität Bochum: Bottleneck Experiment. Pedestrian Dynamics Data Archive (2022)". The arXiv version's ref [13] (Tiny Box) wrongly reuses the same DOI; the journal version's refs [13], [14] give URLs only, no DOI.

Fetched BibTeX (doi.org, Accept: application/x-bibtex): @misc, doi 10.34735/PED.2021.9, url https://ped.fz-juelich.de/da/2021bottleneck, the 8 authors above, title as above, publisher Forschungszentrum Jülich, year 2026. The repo entry `fzj_ped20219` matches except it lacks `url`.

## 4. Adrian, Seyfried, Sieben 2020 (J. R. Soc. Interface 17:20190871): wrong source for these runs

- Entrance: "an entrance gate with a passage width of 0.5 m" served as the bottleneck. The referee is right.
- Varied parameter: corridor **width** w in front of the gate, 1.2 to 5.6 m (Table 1: 5.6, 4.5, 3.4, 2.3, 1.2 m), plus motivation hi/lo and priming (crowding/queuing).
- Run names 030/040 ... 270/280; 030/040 is w = 5.6 m, 110/120 is w = 1.2 m. The numerical coincidence with 4D030/4D110 is only a naming overlap.
- Data: Pedestrian Dynamics Data Archive DOI 10.34735/ped.2018.1 (2018crowdqueue), a different (2018) experiment. Project CroMa (BMBF 13N14530-13N14532), which is why both are "CroMa".
- So it does not describe any 0.8 m run, a 2.0 m or 0.2 m bottleneck length, or the 2021 Duesseldorf data.

## 5. Publication describing the five runs

Boomers et al., "Pedestrian Crowd Management Experiments: A Data Guidance Paper", Collective Dynamics 8, 1-57 (2023), DOI 10.17815/CD.2023.141 (Crossref: published 2023-05-08, CC BY 4.0); preprint arXiv:2303.02319 (v2, 2023-03-10). Sec. 3.7 "Bottleneck Experiments" and Appendix A.9, Table 19 list runs 4D030, 4D040, 4D110, 4D120, 4D130 with w = 0.8 m and l = 2.0 / 0.2 m. Checked in both the arXiv v2 text and the journal PDF (collective-dynamics.eu download A141/238): journal Sec. 3.7, App. A.9, Table 19 give the same rows (4D030: N 161, w 0.8, l 2.0, h0; 4D110: N 132, w 0.8, l 0.2, h0; 4D130: N 129, w 0.8, l 0.2, h2).

No other paper found (Semantic Scholar, Crossref, OpenAlex searches; Küpper & Adrian 2026; Üsten et al. arXiv:2604.26858 has no match for the dataset or run names) that analyses these five 0.8 m runs.

## 6. Recommendations

- Replace `\cite{adrian2020crowds}` in the 07_experiments sentence by `\cite{boomers2023data}` (key to choose), journal version.
- Keep `fzj_ped20219`; add the fetched `url` field.
- Change 0.21 m to 0.2 m in the text (and check numbers/macros/code comments using 0.21; `RUNS` in `e10_croma.py` uses L = 0.21, a 1 cm geometry difference).
- Use "bottleneck length" rather than "corridor" width, and mention the full-commitment run.

Replacement sentence (draft):

> The CroMa bottleneck experiments~\cite{fzj_ped20219,boomers2023data} include \EtenHumanN\ runs through a 0.8\,m wide bottleneck, two with a bottleneck 2.0\,m long and three with one 0.2\,m long (a door in a wall) (runs 4D030, 4D040, 4D110, 4D120, 4D130). Participants were told to walk normally, to hurry or (in one run) to give full commitment, and in four runs kept a 2\,m semicircle in front of the bottleneck clear.
