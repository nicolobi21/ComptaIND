# Étude de niches e-commerce — rapport

> État : **Phase 0 terminée** (mise en place). Phases 1 à 4 non commencées : en attente du profil et de votre « OK ».
> Toutes les sources sont dans `sources.csv` ; les extraits bruts dans `sources/`.

## 1. Résumé
_À rédiger en fin d'étude._

## 2. Méthode et limites
### Accès aux sources testé le 2026-10-26
| Source | Résultat | Conséquence |
|---|---|---|
| WebSearch | Fonctionne (outil indiqué « US-only » : résultats potentiellement biaisés vers des sources US) | Compléter par des sources UE/BE consultées directement |
| WebFetch | Fonctionne, mais **résume** les pages | Tout chiffre précis est revérifié sur la page brute (curl) ou marqué « issu d'un résumé » |
| EUR-Lex (eur-lex.europa.eu) | HTTP 202 vide (WebFetch et curl) | Textes officiels récupérés via l'Office des publications (CELLAR) — S001 |
| Commission européenne | OK | S002 |
| Amazon.com.be / Amazon.fr — Meilleures ventes | Page accessible ; robots.txt n'interdit pas ces pages (S003, S004) | Consultation manuelle, faible volume |
| bol.com | HTTP 403 ; robots.txt interdit `/be/fr/p/` et `/*/s/` (S005) | **Non consulté.** Nécessite vos captures/exports |
| Google Trends | Pas d'accès programmatique (HTTP 400) | Nécessite vos exports CSV |
| Becom (becom.digital) | Accessible (S006) | Contenus réservés aux membres : je ne sais pas encore |
| Statbel, SPF Finances (douanes) | Accessibles (HTTP 200) | Utilisables en Phase 1/3 |

## 3. Tableau de scoring
_Phase 2._

## 4. Dossiers du top 3
_Phase 3._

## 5. Plan de test
_Phase 4._

## 6. « Je ne sais pas »
- Profil vendeur : non renseigné (bloquant pour la Phase 1).
- Frais de traitement douanier d'environ 2 €/colis au 1er novembre 2026 : non trouvé dans la source officielle S002 ; à vérifier.
- Référence juridique (n° de règlement) du droit de 3 € et date de fin : absentes de S002 ; à vérifier.

## 7. Sources
Voir `sources.csv`.
