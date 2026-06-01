# Analiza slovenskega trga avtomobilov

Projektna naloga pri predmetu Podatkovno rudarjenje.

## O projektu

Projekt analizira avtomobile registrirane v Sloveniji ter gradi napovedni model za oceno tržne vrednosti rabljenih vozil.

Podatki prihajajo iz dveh virov:
- **Evidenca registriranih vozil** (podatki.gov.si) — 1.311.778 osebnih avtomobilov
- **Oglasi rabljenih vozil** (mobile.de) — 500 oglasov za 6 najbolj priljubljenih modelov v Sloveniji

## Deployed aplikacija

Aplikacija je dostopna na Streamlit Cloud in omogoča **interaktivno napoved cene** rabljenega vozila glede na njegove karakteristike (znamka, model, gorivo, motor, moč, leto, kilometri, stanje).

> **Opomba:** Zaradi tehničnih omejitev pri deploymentu (velikost podatkov, kompatibilnost knjižnic) analitičnega dela z grafi slovenskega registra vozil žal nismo uspeli vključiti v objavljeno aplikacijo. Celotna analiza je dostopna lokalno z zagonom `app_local.py`.

## Napovedni model

Model uporablja **StackingRegressor** (kombinacija ExtraTreesRegressor + HistGradientBoostingRegressor + RidgeCV) s preprocessing pipeline (RobustScaler + SimpleImputer). Ocenjen z 5-kratno prečno validacijo na 1.124 vozilih.

## Lokalni zagon

```bash
pip install -r requirements.txt
python train_model.py   # generira model2.pkl
streamlit run app.py
```

## Struktura projekta

```
├── app.py              # Streamlit aplikacija (napoved cene)
├── main.py             # Analiza slovenskega registra vozil
├── model2.py           # Trening modela po posameznih avtomobilih
├── train_model.py      # Generiranje skupnega modela za aplikacijo
├── korelacija.py       # Korelacijska analiza in feature importance
├── requirements.txt
└── data/
    ├── top5/           # JSON oglasi z mobile.de
    ├── Vozila1-3.csv   # Register vozil (Git LFS)
    └── model2.pkl      # Naučen model (Git LFS)
```
