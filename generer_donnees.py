"""
Projet Power BI : Bank Data Quality & Credit Portfolio Monitoring
Génère un jeu de données bancaires 100 % FICTIF avec des erreurs injectées volontairement.

Usage :  python generer_donnees.py
Sortie : dossier ./data_banque/ avec 4 CSV (encodage UTF-8 avec BOM, lisible par Power BI et Excel)
Dépendances : pandas, numpy
"""
import os
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)  # graine fixe = résultats reproductibles
OUT = "data_banque"
os.makedirs(OUT, exist_ok=True)

N_CLIENTS = 5000
N_CREDITS = 12000
DATE_MIN, DATE_MAX = pd.Timestamp("2022-01-01"), pd.Timestamp("2025-12-31")

# ------------------------------------------------------------------ AGENCES
agences_def = [
    ("Casablanca", "Casablanca-Settat", 33.5731, -7.5898),
    ("Mohammedia", "Casablanca-Settat", 33.6866, -7.3830),
    ("Settat", "Casablanca-Settat", 33.0010, -7.6166),
    ("El Jadida", "Casablanca-Settat", 33.2316, -8.5007),
    ("Rabat", "Rabat-Salé-Kénitra", 34.0209, -6.8416),
    ("Salé", "Rabat-Salé-Kénitra", 34.0531, -6.7985),
    ("Kénitra", "Rabat-Salé-Kénitra", 34.2610, -6.5802),
    ("Marrakech", "Marrakech-Safi", 31.6295, -7.9811),
    ("Safi", "Marrakech-Safi", 32.2994, -9.2372),
    ("Fès", "Fès-Meknès", 34.0331, -5.0003),
    ("Meknès", "Fès-Meknès", 33.8935, -5.5473),
    ("Tanger", "Tanger-Tétouan-Al Hoceïma", 35.7595, -5.8340),
    ("Tétouan", "Tanger-Tétouan-Al Hoceïma", 35.5785, -5.3684),
    ("Agadir", "Souss-Massa", 30.4278, -9.5981),
    ("Taroudant", "Souss-Massa", 30.4703, -8.8769),
    ("Oujda", "Oriental", 34.6814, -1.9086),
    ("Nador", "Oriental", 35.1681, -2.9335),
    ("Béni Mellal", "Béni Mellal-Khénifra", 32.3373, -6.3498),
    ("Khouribga", "Béni Mellal-Khénifra", 32.8811, -6.9063),
    ("Laâyoune", "Laâyoune-Sakia El Hamra", 27.1253, -13.1625),
    ("Dakhla", "Dakhla-Oued Ed-Dahab", 23.6848, -15.9580),
    ("Errachidia", "Drâa-Tafilalet", 31.9314, -4.4244),
    ("Ouarzazate", "Drâa-Tafilalet", 30.9335, -6.9370),
    ("Al Hoceïma", "Tanger-Tétouan-Al Hoceïma", 35.2517, -3.9372),
    ("Taza", "Fès-Meknès", 34.2100, -4.0100),
]
directeurs = ["Y. Alaoui", "S. Benjelloun", "K. Idrissi", "M. Tazi", "A. Berrada",
              "H. Lahlou", "N. Chraibi", "R. Fassi", "L. Bennani", "O. Kettani"]
agences = pd.DataFrame({
    "agence_id": [f"AG{str(i+1).zfill(3)}" for i in range(len(agences_def))],
    "ville_agence": [a[0] for a in agences_def],
    "region": [a[1] for a in agences_def],
    "latitude": [a[2] for a in agences_def],
    "longitude": [a[3] for a in agences_def],
    "directeur": [directeurs[i % len(directeurs)] for i in range(len(agences_def))],
})
# Chaque agence a un niveau de risque propre (quelques agences très risquées = insights)
risque_agence = rng.uniform(0.6, 1.4, len(agences))
for idx in rng.choice(len(agences), 3, replace=False):
    risque_agence[idx] = rng.uniform(2.2, 3.0)
agences["_risque"] = risque_agence

# ------------------------------------------------------------------ CLIENTS
prenoms = ["Youssef", "Fatima", "Mohamed", "Khadija", "Ahmed", "Salma", "Omar", "Imane",
           "Hamza", "Aya", "Anas", "Hajar", "Karim", "Sara", "Mehdi", "Nadia", "Reda",
           "Zineb", "Amine", "Meryem", "Ayoub", "Houda", "Soufiane", "Rania"]
noms = ["Alaoui", "Benani", "El Idrissi", "Tazi", "Berrada", "Lahlou", "Chraibi", "Fassi",
        "Bennis", "Kettani", "Amrani", "Naciri", "Sbai", "Ziani", "Mansouri", "Haddad",
        "Rifi", "Ouazzani", "Skalli", "Cherkaoui"]
segments = ["Particulier", "Premium", "Professionnel", "Entreprise"]

villes_clients = rng.choice(agences["ville_agence"], N_CLIENTS)
segment = rng.choice(segments, N_CLIENTS, p=[0.62, 0.15, 0.17, 0.06])
revenu_base = {"Particulier": 5500, "Premium": 18000, "Professionnel": 12000, "Entreprise": 45000}
revenu = np.array([max(2500, rng.normal(revenu_base[s], revenu_base[s] * 0.25)) for s in segment]).round(0)

clients = pd.DataFrame({
    "client_id": [f"CL{str(i+1).zfill(5)}" for i in range(N_CLIENTS)],
    "nom_complet": [f"{rng.choice(prenoms)} {rng.choice(noms)}" for _ in range(N_CLIENTS)],
    "age": rng.integers(20, 71, N_CLIENTS),
    "ville": villes_clients,
    "segment": segment,
    "revenu_mensuel": revenu,
    "date_entree": (DATE_MIN - pd.to_timedelta(rng.integers(0, 3650, N_CLIENTS), unit="D")).strftime("%Y-%m-%d"),
})

# ------------------------------------------------------------------ CRÉDITS
types = ["Immobilier", "Consommation", "Automobile", "Professionnel"]
p_types = [0.25, 0.40, 0.20, 0.15]
montant_base = {"Immobilier": 700000, "Consommation": 60000, "Automobile": 150000, "Professionnel": 300000}
duree_base = {"Immobilier": [180, 240, 300], "Consommation": [24, 36, 48, 60],
              "Automobile": [48, 60, 84], "Professionnel": [36, 60, 84]}
taux_base = {"Immobilier": 4.5, "Consommation": 8.0, "Automobile": 6.5, "Professionnel": 6.0}

client_ids = rng.choice(clients["client_id"], N_CREDITS)
client_ville = clients.set_index("client_id")["ville"]
agences_idx = agences.set_index("ville_agence")
type_credit = rng.choice(types, N_CREDITS, p=p_types)
montant = np.array([max(5000, rng.normal(montant_base[t], montant_base[t] * 0.35)) for t in type_credit]).round(-2)
duree = np.array([rng.choice(duree_base[t]) for t in type_credit])
taux = np.array([rng.normal(taux_base[t], 0.6) for t in type_credit]).round(2)
date_octroi = DATE_MIN + pd.to_timedelta(rng.integers(0, (DATE_MAX - DATE_MIN).days - 30, N_CREDITS), unit="D")

# 80 % des crédits dans l'agence de la ville du client, 20 % ailleurs
agence_credit = []
for cid in client_ids:
    if rng.random() < 0.8:
        agence_credit.append(agences_idx.loc[client_ville[cid], "agence_id"])
    else:
        agence_credit.append(rng.choice(agences["agence_id"]))
agence_credit = np.array(agence_credit)
risque = agences.set_index("agence_id")["_risque"]
r = np.array([risque[a] for a in agence_credit])

# Jours de retard : plus le risque de l'agence est élevé, plus les retards sont fréquents
u = rng.random(N_CREDITS)
jours_retard = np.zeros(N_CREDITS, dtype=int)
p_retard = 0.18 * r
p_grave = 0.03 * r
for i in range(N_CREDITS):
    if u[i] < p_grave[i]:
        jours_retard[i] = rng.integers(91, 400)
    elif u[i] < p_grave[i] + 0.05 * r[i]:
        jours_retard[i] = rng.integers(31, 91)
    elif u[i] < p_retard[i] + p_grave[i]:
        jours_retard[i] = rng.integers(1, 31)

fin_credit = date_octroi + pd.to_timedelta(duree * 30, unit="D")
statut = np.where(jours_retard > 90, "Impayé",
          np.where(fin_credit < DATE_MAX, "Soldé", "En cours"))
# un crédit soldé n'a pas de retard actuel
jours_retard = np.where(statut == "Soldé", 0, jours_retard)

credits = pd.DataFrame({
    "credit_id": [f"CR{str(i+1).zfill(6)}" for i in range(N_CREDITS)],
    "client_id": client_ids,
    "agence_id": agence_credit,
    "type_credit": type_credit,
    "montant": montant,
    "taux_interet": taux,
    "duree_mois": duree,
    "date_octroi": date_octroi.strftime("%Y-%m-%d"),
    "statut": statut,
    "jours_retard": jours_retard,
})

# ------------------------------------------------------------------ REMBOURSEMENTS
rows = []
for cr in credits.itertuples():
    taux_m = cr.taux_interet / 100 / 12
    mensualite = cr.montant * taux_m / (1 - (1 + taux_m) ** -cr.duree_mois)
    debut = pd.Timestamp(cr.date_octroi)
    mois_ecoules = max(1, int((DATE_MAX - debut).days / 30))
    n = min(cr.duree_mois, mois_ecoules, int(rng.integers(2, 11)))
    for k in range(1, n + 1):
        rows.append((cr.credit_id, (debut + pd.Timedelta(days=30 * k)).strftime("%Y-%m-%d"),
                     round(mensualite * rng.uniform(0.97, 1.03), 2)))
remb = pd.DataFrame(rows, columns=["credit_id", "date_paiement", "montant_paye"])
remb.insert(0, "paiement_id", [f"PM{str(i+1).zfill(7)}" for i in range(len(remb))])

# ================================================================== INJECTION D'ERREURS
log = {}

# 1) Clients : doublons (3 %) — même client avec un id différent
n_dup = int(N_CLIENTS * 0.03)
dups = clients.sample(n_dup, random_state=1).copy()
dups["client_id"] = [f"CL{str(N_CLIENTS + i + 1).zfill(5)}" for i in range(n_dup)]
clients = pd.concat([clients, dups], ignore_index=True)
log["clients_doublons"] = n_dup

# 2) Clients : revenu manquant (4 %)
idx = clients.sample(frac=0.04, random_state=2).index
clients.loc[idx, "revenu_mensuel"] = np.nan
log["clients_revenu_vide"] = len(idx)

# 3) Clients : âges impossibles (1,5 %)
idx = clients.sample(frac=0.015, random_state=3).index
clients.loc[idx, "age"] = rng.choice([-3, 0, 5, 140, 999, 215], len(idx))
log["clients_age_impossible"] = len(idx)

# 4) Clients : villes mal écrites (8 %)
variantes = {"Casablanca": ["Casa", "casablanca", "CASABLANCA", "Casablanca "],
             "Rabat": ["rabat", "RABAT", "Rabat "], "Marrakech": ["Marrakesh", "marrakech", "Marrakech "],
             "Fès": ["Fes", "fes", "FES"], "Tanger": ["Tangier", "tanger", "Tanger "],
             "Agadir": ["agadir", "AGADIR"], "Oujda": ["oujda", "Oujda "]}
idx = clients.sample(frac=0.08, random_state=4).index
n_ville = 0
for i in idx:
    v = clients.at[i, "ville"]
    if v in variantes:
        clients.at[i, "ville"] = rng.choice(variantes[v])
        n_ville += 1
log["clients_ville_non_standard"] = n_ville

# 5) Clients : noms en minuscules / espaces parasites (2 %)
idx = clients.sample(frac=0.02, random_state=5).index
clients.loc[idx, "nom_complet"] = clients.loc[idx, "nom_complet"].str.lower() + " "
log["clients_nom_mal_formate"] = len(idx)

# 6) Crédits : montants négatifs (1 %) et taux aberrants (0,7 %)
idx = credits.sample(frac=0.01, random_state=6).index
credits.loc[idx, "montant"] = -credits.loc[idx, "montant"]
log["credits_montant_negatif"] = len(idx)
idx = credits.sample(frac=0.007, random_state=7).index
credits.loc[idx, "taux_interet"] = rng.choice([0, 45.0, 99.9, -2.5], len(idx))
log["credits_taux_aberrant"] = len(idx)

# 7) Crédits : client_id orphelin (0,5 %) — client inexistant
idx = credits.sample(frac=0.005, random_state=8).index
credits.loc[idx, "client_id"] = [f"CL9{str(i).zfill(4)}" for i in range(len(idx))]
log["credits_client_orphelin"] = len(idx)

# 8) Remboursements : date de paiement AVANT l'octroi du crédit (2 %)
idx = remb.sample(frac=0.02, random_state=9).index
octroi = credits.set_index("credit_id")["date_octroi"]
remb.loc[idx, "date_paiement"] = [
    (pd.Timestamp(octroi[c]) - pd.Timedelta(days=int(rng.integers(5, 400)))).strftime("%Y-%m-%d")
    for c in remb.loc[idx, "credit_id"]]
log["remboursements_date_incoherente"] = len(idx)

# 9) Remboursements : lignes dupliquées (1 %) et montants nuls (0,5 %)
dup_r = remb.sample(frac=0.01, random_state=10)
remb = pd.concat([remb, dup_r], ignore_index=True)
log["remboursements_doublons"] = len(dup_r)
idx = remb.sample(frac=0.005, random_state=11).index
remb.loc[idx, "montant_paye"] = 0
log["remboursements_montant_nul"] = len(idx)

# Mélange pour que les doublons ne soient pas côte à côte
clients = clients.sample(frac=1, random_state=12).reset_index(drop=True)
remb = remb.sample(frac=1, random_state=13).reset_index(drop=True)

# ------------------------------------------------------------------ EXPORT
agences.drop(columns="_risque").to_csv(f"{OUT}/agences.csv", index=False, encoding="utf-8-sig")
clients.to_csv(f"{OUT}/clients.csv", index=False, encoding="utf-8-sig")
credits.to_csv(f"{OUT}/credits.csv", index=False, encoding="utf-8-sig")
remb.to_csv(f"{OUT}/remboursements.csv", index=False, encoding="utf-8-sig")

print("Fichiers générés dans :", OUT)
for name, df in [("agences", agences), ("clients", clients), ("credits", credits), ("remboursements", remb)]:
    print(f"  {name}.csv : {len(df):,} lignes")
print("\nErreurs injectées (corrige-les dans Power Query !) :")
for k, v in log.items():
    print(f"  {k:36s} {v:>6,}")
