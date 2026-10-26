# Étude de niches e-commerce — rapport

> État : **Phase 1 terminée** (repérage, 26/10/2026). Phase 2 en attente de ton « OK ».
> Toutes les sources sont dans `sources.csv` ; les extraits bruts dans `sources/` ; les calculs dans `analysis/`.

## 1. Résumé
_À rédiger en fin d'étude._

## 2. Méthode et limites
### Profil vendeur (déclaré le 2026-10-26)
| Champ | Valeur |
|---|---|
| Pays | Belgique et France au départ ; d'autres pays ensuite |
| Canaux | Site propre (Shopify déjà pratiqué) + réseaux sociaux / TikTok Shop |
| Budget test | 400 € |
| Budget stock initial | 200 € (en plus du budget test ; total 600 €) |
| Temps | 16 h/semaine |
| Avantages | Compétences informatiques, expérience d'une boutique Shopify. Aucun fournisseur, réseau ou communauté |
| Catégories exclues | Aucune |
| Statut | Indépendant |

Canal TikTok Shop : inscription vendeur possible en Belgique et en France d'après le Seller Center (S007) ; lancement en Belgique annoncé pour le 15/06/2026 (S008). Je ne sais pas encore si TikTok Shop accepte un indépendant personne physique : à vérifier en Phase 3.

### Accès aux sources testé le 2026-10-26
| Source | Résultat | Conséquence |
|---|---|---|
| WebSearch | Fonctionne (outil indiqué « US-only » : résultats potentiellement biaisés vers des sources US) | Compléter par des sources UE/BE consultées directement |
| WebFetch | Fonctionne, mais **résume** les pages | Tout chiffre précis est revérifié sur la page brute (curl) ou marqué « issu d'un résumé » |
| EUR-Lex (eur-lex.europa.eu) | HTTP 202 vide (WebFetch et curl) | Textes officiels récupérés via l'Office des publications (CELLAR) |
| Commission européenne | OK | S002 |
| Amazon.fr — Meilleures ventes | 88 pages relevées (S012), puis **captcha sur 15 pages** | Relevé automatique arrêté (règle 8) |
| Amazon.com.be | robots.txt OK (S003) mais **non relevé** (arrêt après le captcha d'Amazon.fr) | Classement belge à obtenir autrement (voir § 6) |
| bol.com | HTTP 403 ; robots.txt interdit `/be/fr/p/` et `/*/s/` (S005) | **Non consulté.** Nécessite tes captures |
| Google Trends | Pas d'accès programmatique (HTTP 400) | Nécessite tes exports CSV |
| TikTok Creative Center | Page en JavaScript, aucun classement lisible (S024) | Nécessite tes captures |
| Becom | Rapport original non trouvé ; chiffres via DH (S010) et VRT (S011) | Sources secondaires |
| Eurostat | API OK (S009) | Contexte macro uniquement |

### Méthode de la Phase 1
1. **Signal d'achat** : classement « Meilleures ventes » d'Amazon.fr, que la page définit comme « nos produits les plus populaires en vertu du nombre de ventes » (S012). Rang = preuve d'ACHAT **relative** (pas un volume). Nombre d'évaluations = achats cumulés approximatifs (mélange notes et avis, parfois partagé entre variantes).
2. **Exploration** : 18 catégories → 55 sous-catégories → 15 sous-sous-catégories (30 produits par page, soit 2 100+ lignes dans `analysis/amazon_fr_*.csv`). Script : `analysis/amazon_bs.py`.
3. **Concurrence** (première impression) : `analysis/concentration.py` calcule pour chaque page `part_top3 = évaluations des 3 produits les plus notés ÷ total des évaluations du top 30` et le nombre de produits classés avec moins de 100 évaluations (résultats dans `analysis/concentration_fr.csv`).
4. **Éliminations** selon tes règles, chaque raison réglementaire étant appuyée sur le texte officiel (S013-S023).

### Limites de la Phase 1 (à garder en tête)
- **Un seul jour d'observation** (26/10/2026) : la saisonnalité et la tendance ne sont pas mesurées (prévu en Phase 2, avec tes exports Google Trends).
- **France uniquement** pour les classements : la Belgique n'est pas couverte (Amazon.com.be non relevé, bol.com bloqué).
- **Prix indicatifs** : Amazon a servi les pages avec une adresse de livraison aux États-Unis.
- **Avis négatifs et forums : non collectés** dans cette phase (arrêt d'Amazon avant la lecture des fiches produits). Ce signal qualitatif est reporté à la Phase 2 pour les 10 finalistes.
- Biais de canal : Amazon ≠ site propre ou TikTok Shop. Une demande prouvée sur Amazon ne garantit pas la conversion sur ton site.

### Contexte marché (macro, pas au niveau d'une niche)
- 2024 : 64,21 % des particuliers en Belgique et 69,31 % en France ont commandé des articles physiques en ligne au cours des 3 derniers mois (Eurostat, S009). Les données 2025 ne sont pas encore publiées dans ce jeu de données.
- 2025 : 18,3 milliards d'euros de dépenses en ligne en Belgique, soit +5,4 % (Becom, cité par DH, S010). Le chiffre d'affaires du secteur belge n'a progressé que de 3,43 % ; Becom évoque une croissance de 20 à 30 % pour Shein et Temu (déclaration rapportée par la VRT, S011).

## Phase 1 — Repérage : 40 niches (21 gardées, 19 éliminées)
Détail complet (URL, signaux, concurrence) : `analysis/phase1_candidats.csv`. Toutes les données ont été mesurées le 26/10/2026 sur Amazon.fr (S012).

### Gardées pour la Phase 2
| ID | Niche | Preuve | Concurrence (1re impression) | Alerte |
|---|---|---|---|---|
| C01 | Accessoires de puzzle adulte (tapis, plateaux, trieurs) | ACHAT fort : trieur 6 352 éval. ; tapis Ravensburger 4 839 éval. ; tapis MOZOOSON 1 226 éval. | Concentrée (part top3 0,79) | — |
| C02 | Puzzles adultes à illustrations originales | ACHAT moyen : 1 702 / 543 / 358 éval. | Grandes marques + petites marques | Champ « jouet » à vérifier |
| C03 | Kits maquettes DIY adultes (book nooks, puzzles 3D) | ACHAT moyen : 1 124 / 220 éval. | Marques chinoises établies | LED et piles |
| C04 | Accessoires de peinture de figurines | ACHAT faible (accessoires) | Marques spécialisées | Peintures exclues (CLP) |
| C05 | Minuteurs visuels | ACHAT fort : 5 383 / 4 201 / 4 016 éval. | Designs quasi identiques | EEE probable (DEEE, piles) |
| C06 | Tableaux de routine pour enfants (FR) | ACHAT moyen : 2 784 éval. ; 23/30 produits <100 éval. | Smart Panda dominant | Jouet (<14 ans), aimants |
| C07 | Planificateurs magnétiques familiaux | ACHAT moyen : 2 537 / 1 399 éval. ; 17/30 produits <100 éval. | Fragmentée | — |
| C08 | Accessoires d'impression 3D | ACHAT faible (accessoires) | Marques de filament | Adéquation avec ton profil |
| C09 | Gilets d'hydratation trail | ACHAT faible à moyen : 2 189 éval. | Salomon + génériques | Retours liés aux tailles |
| C10 | Accessoires textiles de musculation | ACHAT fort : 10 127 / 8 286 éval. | Marques DTC européennes | — |
| C11 | Leurres et outils de pêche aux carnassiers | ACHAT fort : TRUSCEND 12 226 / 13 825 éval. | TRUSCEND domine | Plomb : je ne sais pas |
| C12 | Accessoires de voiture pour chiens | ACHAT fort : 17 658 / 10 768 / 10 339 éval. | KYG ≥6 fiches | Volume du colis |
| C13 | Accessoires d'éducation canine (non électroniques) | ACHAT fort : longe 21 758 éval. | Génériques | — |
| C14 | Filets à foin pour chevaux | ACHAT faible : 969 éval. max | Petite catégorie | — |
| C15 | Mangeoires et nichoirs | ACHAT faible : 2 471 éval. max | Page dominée par la nourriture | Saison |
| C16 | Accessoires de fermentation | ACHAT faible : 1 123 éval. max | Petite catégorie | Contact alimentaire, verre |
| C17 | Kits cadeaux graines / bonsaï | ACHAT moyen : 6 518 / 5 593 éval. | Page dominée par le gazon | Semences : je ne sais pas |
| C18 | Accessoires de guitare | ACHAT fort : capodastre 56 836 éval. ; support mural 2 432 éval. | Génériques bon marché | — |
| C19 | Isolation anti-courants d'air | ACHAT fort : Vellure 24 866 éval. | Vellure dominant | Saison |
| C20 | Bouillottes et coussins aux noyaux de cerise | ACHAT fort : 7 900 éval. | Page mixte | Brûlure : norme inconnue |
| C21 | Kits de crochet pour débutants | ACHAT faible et indirect (fils seuls) | Non relevée (captcha) | Étiquetage textile |

### Éliminées (raison)
| ID | Niche | Raison |
|---|---|---|
| E01 | Cadres pour puzzles | Volumineux et fragiles |
| E02 | Éclairage de running LED | Batterie lithium : enregistrement par État membre (DEEE art. 16, S015 ; batteries art. 55, S016) + saison |
| E03 | Colliers de dressage électroniques | Radio (S020) + DEEE + batteries |
| E04 | Élastiques de musculation | Générique à ~7 € |
| E05 | Pièges collants anti-moucherons | Générique ; une marque occupe 3 places du top 30 |
| E06 | Marque-pages adhésifs | Générique à ~9 € |
| E07 | Plaques de boîte aux lettres personnalisées | Prix de marché 4,99 € (MESURÉ) ; HYPOTHÈSE : envoi non rentable ; graveur laser nécessaire |
| E08 | Petits articles ménagers génériques | Génériques ; verre |
| E09 | Housses de pluie pour sac à dos | Générique à 7-15 € |
| E10 | Masques de sommeil | Générique à ~8 € |
| E11 | Bouchons d'oreilles | EPI de catégorie III « bruits nocifs » (S017) |
| E12 | Produits chimiques (huiles essentielles, nettoyants, magnésie) | CLP (S018) ; statut cosmétique incertain |
| E13 | Cosmétiques (colle à cils, vernis) | Règlement cosmétiques (S022) |
| E14 | Puériculture, jouets du premier âge | Jouets (S013, S014) ; contact alimentaire (S021) ; publics vulnérables |
| E15 | Électronique grand public | Génériques massifs + DEEE/batteries |
| E16 | Calendriers de l'Avent, agendas datés | HYPOTHÈSE : stock périmé après la date |
| E17 | Escalade (mousquetons, cordes) | EPI de catégorie III « chutes de hauteur » (S017) |
| E18 | Aliments pour animaux | Règlement 767/2009 (S019) |
| E19 | Articles volumineux | Lourds ou volumineux |

Idée écartée faute de signal : objets imprimés en 3D à la demande (ton profil s'y prête, mais je n'ai relevé aucune preuve de demande).

## 3. Tableau de scoring
_Phase 2._

## 4. Dossiers du top 3
_Phase 3._

## 5. Plan de test
_Phase 4._

## 6. « Je ne sais pas »
- **Belgique** : aucun classement de ventes belge relevé (Amazon.com.be non relevé, bol.com bloqué). → Captures bol.com et Amazon.com.be de ta part (voir la liste des exports).
- **Tendance et saisonnalité** : non mesurées. → Exports Google Trends BE/FR sur 5 ans pour les finalistes.
- **Avis négatifs** des produits leaders : non collectés. → À faire en Phase 2 sur les 10 finalistes.
- Restrictions sur le plomb dans les articles de pêche (C11), règles sur les semences (C17), norme applicable aux bouillottes (C20), statut « jouet » d'un puzzle adulte (C02) : à vérifier.
- Conditions d'éligibilité vendeur TikTok Shop BE/FR pour un indépendant : non vérifiées.
- Frais de traitement douanier d'environ 2 €/colis au 1er novembre 2026 : absents de la source officielle S002 ; à vérifier.
- Référence juridique (n° de règlement) et date de fin du droit de 3 € : absentes de S002 ; à vérifier.

## 7. Sources
Voir `sources.csv`.
