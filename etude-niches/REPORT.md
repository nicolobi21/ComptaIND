# Étude de niches e-commerce — rapport

> État : **Phase 2 B2B terminée** (26/10/2026) ; Phase 3 en attente de ton « OK » et de ton choix du top 3. **Réorientation : B2B seul**, vente par démonstration chez des professionnels, Belgique francophone. La Phase 1 B2C ci-dessous est conservée pour mémoire. Phase 2 en attente de ton « OK ».
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

**Mise à jour du profil (26/10/2026)** : B2B seul ; démonstrations chez des clients professionnels ; zone francophone (Wallonie, Bruxelles) ; régime de franchise TVA ; budget « plus si besoin » (plafond non chiffré → à préciser).

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

## Phase 1-bis — B2B Belgique francophone : 27 pistes (21 gardées, 6 éliminées)
Détail complet : `analysis/phase1bis_b2b.csv`.

### Méthode : la preuve change de nature en B2B
Il n'existe pas de classement public des ventes entre entreprises. J'ai donc utilisé trois types de signaux, du plus fort au plus faible :
1. **OBLIGATION** : un texte officiel impose (ou va imposer) l'achat. La demande est contrainte, mais ce n'est pas une preuve de ventes.
2. **ACHAT PUBLIC** : avis d'attribution TED (S032). Ce sont 4 810 marchés belges de fournitures sur 24 mois, dont 2 523 en Wallonie et à Bruxelles (1 142 + 1 381, région déduite du code postal de l'acheteur). C'est une preuve d'achat réelle, mais sur de **gros marchés** (valeurs médianes par groupe CPV ≈ 250 k€ à plusieurs M€). Elle montre que la catégorie s'achète et que des PME en remportent, pas que tu peux y vendre en direct.
3. **ACHAT B2C + HYPOTHÈSE B2B** : niches de la Phase 1 dont les acheteurs pourraient être des professionnels (aucune preuve).

### Pistes avec le signal le plus fort
| ID | Piste | Signal | Pourquoi c'est intéressant pour toi | Alerte principale |
|---|---|---|---|---|
| B01 | CO2-mètres pour lieux accessibles au public | OBLIGATION progressive dès le 01/01/2027 (S028) | Démonstration simple, capteurs connectés (IT) | Liste des premiers lieux concernés inconnue |
| B02 | Purificateurs d'air pour lieux publics | Même loi (S028) | Ticket élevé, démonstration | Exigences belges imposées aux fabricants et importateurs |
| B03 | Offre clé en main « qualité de l'air » | Même loi : mesure, analyse de risques, plan d'action (S028) | Produit + service + tableau de bord IT | Qualification requise pour l'analyse de risques : je ne sais pas |
| B05 | Caisses pour l'horeca | 32 417 établissements équipés en 2023 (S031) | Gros ticket, IT | Nouvelles échéances : source secondaire seulement |
| B06 | Écrans interactifs, affichage dynamique | TED : 12 avis audiovisuel dont 8 PME (S032) | Gros ticket, IT, démonstration | Concurrence d'intégrateurs établis |
| B07 | Wi-Fi / réseaux pour PME | TED : 9 avis dont 8 PME (S032) | IT | Surtout du service |

Les autres pistes gardées (vêtements professionnels, fontaines à eau, cuisine professionnelle, mobilier ergonomique, boîtes de secours…) et les 6 éliminées sont dans le CSV.

### Contraintes transversales (à lire avant de choisir)
1. **Franchise TVA vs gros ticket.** Plafond de 25 000 €/an selon une source secondaire (S027, ESTIMÉ, non confirmé sur le site du SPF Finances). Calcul : 10 ventes × 2 500 € = 25 000 € → plafond atteint. En sortant de la franchise, tu devrais facturer la TVA et émettre des **factures électroniques structurées** (obligatoires entre assujettis depuis le 01/01/2026, S025).
2. **Statut DEEE pour l'électronique** (B01, B02, B05, B06, B07). Si tu achètes à un distributeur belge, tu es « distributeur ». Si tu achètes dans un autre État membre ou hors UE et que tu revends en Belgique, tu deviens « producteur », avec des obligations d'enregistrement (directive 2012/19/UE, art. 3, 1, f) iii et g ; S015).
3. **Sites bloqués** : Statbel (captcha) et Justel (requêtes rejetées). Je ne connais donc pas le **nombre d'entreprises cibles** par secteur en Wallonie et à Bruxelles, et je n'ai pas lu le texte consolidé des lois belges.

## 3. Tableau de scoring (Phase 2 — B2B, 26/10/2026)
Profil retenu : B2B, démonstrations chez des professionnels, base Charleroi avec voiture, budget 10 000 €, service accepté, passage à l'assujettissement TVA possible.

### Présélection des 10 pistes (sur 21)
Écartées avant notation : B11 présentoirs (volumineux), B13 jetables restauration et B18 supports visuels (petit ticket), B14 matériel informatique (concurrence massive, aucun signal spécifique), B15 stores (sur mesure + pose), B16 imprimés (sous-traitance), B19-B21 (aucune preuve d'achat professionnel). B01, B02 et B03 sont fusionnées en une seule piste « QAI », pour que le top 3 contienne trois pistes distinctes.

### Méthode
- Script `analysis/scoring_b2b.py` : notes, justifications et échelles définies **avant** la notation (en-tête du script). Sortie : `scoring.csv`.
- Score = Σ (note × poids). Exemple pour QAI : 3×0,25 + 4×0,15 + 3×0,15 + 4×0,20 + 3×0,10 + 5×0,15 = **3,65**.
- Demande et tendance : recherche plein texte TED FR+NL sur 36 mois (S035). J'ai contrôlé un échantillon de 6 avis par piste pour mesurer la part d'avis réellement pertinents (« précision »). Attributions estimées = attributions Wallonie+Bruxelles × précision.
- **Marge : HYPOTHÈSE.** Aucun prix de gros public n'est accessible (Alibaba ne renvoie rien) ; il faut des devis (Phase 3).
- **Adéquation : HYPOTHÈSE motivée** (IT, démonstration, voiture, budget).

### Résultats
| Rang | Piste | Demande | Tendance | Concurrence | Marge (H) | Régl./logist. | Adéquation (H) | **Score** | Statut |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Qualité de l'air intérieur (CO2-mètres + purificateurs + mise en place) | 3 | 4 | 3 | 4 | 3 | 5 | **3,65** | À TESTER (aucune preuve d'achat) |
| 2 | Systèmes de caisse pour l'horeca | 4 | 3 | 3 | 3 | 2 | 4 | **3,30** | Gardée |
| 3 ex æquo | Réseaux Wi-Fi pour PME | 2 | 3 | 3 | 4 | 3 | 4 | **3,10** | Gardée |
| 3 ex æquo | Vêtements professionnels personnalisés | 4 | 3 | 3 | 3 | 3 | 2 | **3,10** | Gardée |
| 5 | Boîtes de secours | 3 | 3 | 2 | 2 | 4 | 2 | 2,60 | |
| 6 | Écrans interactifs | 2 | 2 | 2 | 3 | 2 | 4 | 2,50 | |
| 6 | Fontaines à eau | 2 | 3 | 3 | 3 | 2 | 2 | 2,50 | |
| 8 | Cuisine professionnelle | 3 | 4 | 3 | 2 | 1 | 1 | 2,45 | |
| 9 | Éclairage LED | 2 | 2 | 3 | 3 | 2 | 2 | 2,35 | |
| 10 | Mobilier ergonomique | 2 | 3 | 2 | 2 | 2 | 2 | 2,15 | |
(H) = HYPOTHÈSE. Justification et source de chaque note : `scoring.csv`.

### Sensibilité
- **±20 % sur chaque poids** (12 scénarios, poids renormalisés) : QAI reste n° 1 et les caisses n° 2 dans **12 scénarios sur 12**. La 3e place alterne entre Wi-Fi et vêtements professionnels (changement dans 3 scénarios sur 12 : demande ×1,2, marge ×0,8, adéquation ×0,8).
- **Robustesse aux hypothèses** :
  - (a) marge neutralisée à 3 pour toutes les pistes → QAI 3,45, caisses 3,30, vêtements 3,10, Wi-Fi 2,90 ;
  - (b) **critères mesurés seulement** (demande, tendance, concurrence, réglementaire) → **vêtements professionnels 3,38**, QAI 3,23, caisses 3,23, cuisine 2,92.
- **Lecture** : la 1re place de la qualité de l'air dépend de mes hypothèses (marge et adéquation). Sur les seules données mesurées, les vêtements professionnels passent devant. Confiance : **faible à moyenne**.

## Exploration — Marchés publics belges et création d'entreprise (26/10/2026)
Profil complémentaire : ingénieur de gestion, intérêt pour le bâtiment.

### Accès aux données
| Source | Accès | Couverture |
|---|---|---|
| TED (API officielle de l'UE, sans compte) | Utilisé (S036) | Avis belges publiés au niveau européen, surtout au-dessus des seuils européens |
| publicprocurement.be (plateforme belge, SPF BOSA) | Application JavaScript ; API **interne non documentée** (S038). **Non interrogée** | Tous les marchés belges, y compris les petits |
| SPF Économie (agréation des entrepreneurs) | Contrôle anti-robot | — |

### Matériel : besoins les plus fréquents (avis de marché de fournitures, Bruxelles + Wallonie, 36 mois)
Logiciels 365 · produits pharmaceutiques 266 · matériel médical 233 · équipements médicaux 233 · laboratoire 171 · énergie 153 · alimentation 132 · véhicules 124 · informatique 118 · **mobilier 116** · utilitaires 111 · **vêtements professionnels 98** · … · extincteurs 43. Hainaut : logiciels 49, médical 37, alimentation 36, informatique 32. Détail : `analysis/mp_supplies_cpv5_*.csv`. La valeur estimée médiane, quand elle est renseignée, se compte en centaines de milliers d'euros, voire en millions.

### Travaux : corps de métier (avis de marché, Bruxelles + Wallonie, 36 mois)
| CPV | Travaux | Avis de marché A1 → A2 → A3 | Valeur attribuée médiane | Offres reçues (médiane) |
|---|---|---|---|---|
| 45000 | Construction (général) | 559 → 417 → 438 | 7,1 M€ | 3 |
| 45310 | **Équipement électrique** | **12 → 19 → 32** | 5,8 M€ | **2** |
| 45331 | Chauffage, ventilation, climatisation | 17 → 7 → 9 | 10,7 M€ | 4 |
| 45400 | Parachèvement | 22 → 24 → 10 | 2,3 M€ | 3 |
| 45261 | Couverture panneaux solaires | 9 → 8 → 3 | 6,6 M€ | 4,5 |
| 45111 | Démolition | 2 → 4 → 23 | 5,6 M€ | 12 |
Détail : `analysis/mp_works_cpv5_*.csv`.

**Lecture** : sur TED, les travaux sont de **gros chantiers**, réservés à des entreprises agréées de classes élevées. Les plafonds de classe (classe 1 jusqu'à 135 000 €, classe 7 jusqu'à 5 330 000 €) ne viennent que d'une source secondaire (S039, ESTIMÉ ; montants peut-être modifiés au 01/06/2024). Les petits marchés accessibles à une jeune entreprise ne sont **pas** sur TED : il faut les données de publicprocurement.be.

### Main-d'œuvre qualifiée (Forem, liste 2026, S037)
Sont en pénurie en Wallonie, entre autres : installateur électricien, monteur-électricien, monteur en chauffage-sanitaire-ventilation, techniciens HVAC, frigoriste et brûleurs, couvreur, maçon, plafonneur, carreleur, peintre-décorateur, menuisier, isolateur. Proches d'un profil ingénieur de gestion : **métreur, conducteur de chantier, chef de chantier, évaluateur énergétique (PEB, audit), responsable PEB**.

### Données nationales publicprocurement.be (S040, usage de l'API autorisé le 26/10/2026)
Périmètre : Wallonie + Bruxelles, publications du 26/10/2023 au 25/10/2026, références uniques. Cela fait **23 817 publications de travaux** (12 464 mises en concurrence, 11 319 attributions) et **22 023 de fournitures** (8 917 mises en concurrence). Pour comparaison, TED ne contenait que 7 906 avis de travaux pour toute la Belgique : la plateforme belge contient bien les petits marchés.

**Tendance générale** : les mises en concurrence de travaux passent de 4 876 (A1) à 3 834 (A2) puis 3 754 (A3), soit **−23 %**. La cause n'est pas étudiée.

**Travaux : sous-catégories d'agréation exigées** (mises en concurrence, Wallonie + Bruxelles, 36 mois ; `analysis/bosa/travaux_agreations_*.csv`, libellés S041)
| Code | Métier | Avis | A1 → A3 | Classe médiane | Avis en classes 1-2 | Zone Charleroi (BE32B) |
|---|---|---|---|---|---|---|
| P1 | Électricité des bâtiments | 479 | 178 → 151 (−15 %) | 2 | 75 % | 28 |
| D17 | Chauffage central, installations thermiques | 307 | **86 → 116 (+35 %)** | 2 | 66 % | 21 |
| D1 | Gros œuvre | 286 | 103 → 89 | 2 | 51 % | 17 |
| D5 | Menuiserie bois | 240 | 91 → 63 (−31 %) | 2 | 63 % | 20 |
| D18 | Ventilation, climatisation | 229 | 75 → 78 (+4 %) | 2 | 64 % | 17 |
| D16 | Sanitaire, chauffage gaz individuel | 192 | 65 → 62 | 2 | 66 % | 19 |
| D8 / D12 | Toitures | 151 / 115 | stable / en baisse | 2 | 67-70 % | 16 / 8 |
| D (général) | Entreprise générale de bâtiments | 1 691 | 646 → 458 | 4 | 32 % | 136 |

- **56 %** des mises en concurrence de travaux (58 % autour de Charleroi) n'exigent **aucune agréation** dans les données de recherche. Ce sont probablement de petits marchés, mais ce n'est pas vérifié.
- **Plus gros acheteurs de travaux, arrondissement de Charleroi** (36 mois) : Igretec 99, Infrabel 59, Ville de Charleroi 53, SPW Routes de Charleroi 51, Fonds du Logement de Wallonie 46, OTW 41, Sambre & Biesme 33, Logis Châtelettain 25, … Plusieurs sont des **sociétés de logement social**.
- **Fournitures** (mises en concurrence, Wallonie + Bruxelles) : logiciels 340, laboratoire 225, pharmacie 211, utilitaires 168, matériel médical 154, véhicules 153, … vêtements professionnels 72, matériel de plomberie et chauffage 60.
- **Limites** : les résultats de recherche ne donnent ni montants, ni gagnants, ni nombre d'offres. Ces informations sont dans le détail des avis, non téléchargés à ce stade. L'interprétation des codes de procédure en montants n'est pas vérifiée (Justel bloqué).

### Focus électricité : détail des attributions (S042, 26/10/2026)
Périmètre : 905 avis d'attribution de travaux « électricité » (CPV 4531* hors ascenseurs, ou agréation P1/P2), en Wallonie et à Bruxelles, du 26/10/2023 au 25/10/2026, soit **1 415 lots**. Contrôle qualité : sur 1 162 lots attribués, 1 013 montants sont cohérents, 40 incohérents et 109 absents (ces 149 sont exclus des statistiques de montant). Le gagnant est identifié pour 1 159 lots sur 1 162.

**ORES** (gestionnaire du réseau de distribution) représente 142 lots : compteurs, raccordements, éclairage public. Ce sont des travaux de **réseau**, pas d'électricité du bâtiment, donc ils sont exclus des chiffres ci-dessous.

| Indicateur (hors ORES) | Wallonie + Bruxelles (tous lots) | Hainaut | Arr. Charleroi |
|---|---|---|---|
| Lots | 1 415 (dont ORES) | 286 | 98 |
| Montant médian attribué | 100 681 € | 91 499 € | 97 936 € |
| Lots < 143 k€ | 61 % | 63 % | 58 % |
| Offres reçues (médiane) | 2 | 2 | 2 |
| Lots à **offre unique** | 26 % | 30 % | 39 % |
| Lots 30-143 k€ à offre unique | 33 % | 43 % | 56 % |
| Lots infructueux (aucun attributaire) | 14 % | 9 % | 13 % |
| Gagnants distincts | 647 | 168 | 65 |
| Part des 10 premiers gagnants | 10 % | 20 % | 33 % |
| Gagnants avec code postal en Hainaut | 23 % | 58 % | 49 % |
| Écart offre haute / basse (≥ 2 offres) | 20 % | 18 % | 16 % |

Sources des chiffres : `analysis/elec/synthese.txt` (colonne Wallonie + Bruxelles, ORES compris) et `analysis/elec/hors_ORES/synthese.txt` (Hainaut et Charleroi).
- Hors ORES en Hainaut, **11 lots** ont été déclarés infructueux **sans aucune offre**, par exemple des travaux « stock » d'Igretec, la mise en conformité du bâtiment « Quai 10 » à Charleroi, ou le relighting du centre sportif de Lobbes.
- **Les plus gros gagnants en Hainaut (hors ORES)** : TSAV (12 lots), Installations, Maintenance et Constructions Électrotechniques (6), Florisol (6), Aegentis (5), Mignone, Equans, Collignon Eng., Wanty, Lexar Technics, AES… Le marché est **fragmenté** : 168 gagnants différents.
- **Taille déclarée** des gagnants (déclaration partielle, 120 lots en Hainaut) : grandes entreprises 67, PME (sme, small, medium, micro) 52.
- **Lecture** : la concurrence est faible sur les petits marchés. Autour de Charleroi, 56 % des lots de 30 à 143 k€ n'ont reçu qu'une seule offre. Les acheteurs paient en moyenne leur estimation (montant attribué ÷ estimation ≈ 0,95-1,00, mais sur peu de lots). C'est un **indice d'opportunité pour une entreprise d'électricité agréée P1 classes 1-2**, pas une preuve de rentabilité : la marge, le coût de la main-d'œuvre en pénurie (Forem, S037) et les conditions d'agréation ne sont pas mesurés.

### Électricité : types de travaux (hors ORES)
Classement automatique sur l'intitulé et le CPV (règles dans `analysis/elec_types.py`, contrôle manuel par échantillon). Tableaux complets : `analysis/elec/types/types_*.csv`.

| Type (Hainaut, 286 lots) | Part | Montant médian | Offre unique | Infructueux |
|---|---|---|---|---|
| Lot électricité d'un chantier de bâtiment | 29 % | 214 621 € | 29 % | 13 % |
| Détection incendie, alarme, accès, vidéo | 19 % | 30 210 € | 34 % | 7 % |
| Mise en conformité / rénovation d'installation | 16 % | 143 331 € | 20 % | 11 % |
| Éclairage, relighting | 10 % | 56 066 € | 35 % | 4 % |
| Photovoltaïque | 10 % | 95 120 € | 23 % | 7 % |
| Haute / moyenne tension, cabines | 8 % | 156 968 € | 38 % | 4 % |
| Chauffage/PAC/HVAC, câblage data, bornes, signalisation | 8 % | — | — | — |

Les montants de moins de 1 000 € sont exclus : ce sont des taux horaires ou des coefficients d'accords-cadres (18 lots). On note par exemple **110 et 125 €/h** pour des « interventions aux installations électriques » à Farciennes, et des coefficients de 0,82-0,84 sur bordereau (Direction régionale du Hainaut).

### Électricité : pourquoi si peu d'offres ? Lecture de 17 cahiers des charges (S043)
Échantillon : 17 dossiers à offre unique ou sans offre (14 en Hainaut, 3 ailleurs en Wallonie pour les types manquants) dont les documents étaient encore en ligne. Indicateurs : `analysis/elec/csc_indicateurs.csv` ; extraits : `analysis/elec/csc_extraits.md`.
- **Délai pour remettre une offre** : médiane **25 jours** (de 20 à 63 ; 14 dossiers mesurés), dont 7 à 25 jours ou moins.
- **Visite des lieux obligatoire** : 12 dossiers sur 17.
- **Site occupé ou travaux pendant les congés / hors horaires** : 7 sur 17 (site occupé) ; 11 sur 17 mentionnent congés, week-ends ou nuit (détection par mots-clés, à confirmer).
- **Agréation exigée** : de la classe 1 à la classe 5. Les 2 dossiers **sans aucune offre** sont des marchés **multi-métiers** :
  - école Beaulieu : lot 1 = gros œuvre + parachèvements + techniques spéciales, agréations de classe 5 ;
  - Igretec : marché « stock » D, D4, D5, P1, D13…

  Un électricien seul ne pouvait pas y répondre.
- Autres freins relevés : délais d'exécution très courts liés à des fonds européens (A6K : réception au plus tard le 21/08/2026) ; cautionnement de 5 % ; pénalités spéciales (400 €/jour DNSH).
- **Absents** : aucune exigence de chiffre d'affaires minimum détectée ; références exigées dans 4 dossiers sur 17 seulement.
- **Lecture** : le manque d'offres semble venir surtout de **contraintes pratiques** (visite obligatoire, délai court, site occupé, calendrier serré) et de l'**allotissement multi-métiers**, plutôt que de barrières financières. C'est une interprétation sur 17 dossiers non tirés au hasard.

### Électricité : gagnants récurrents en Hainaut et leurs comptes (S044, BNB)
Onze sociétés domiciliées en Hainaut, 3 derniers exercices. Détail : `analysis/elec/bilans_gagnants_hainaut.csv` et `analysis/elec/gagnants_poids_marches_publics.csv`.

| Société (code postal) | ETP | CA ou marge brute (dernier exercice) | Résultat | Rentabilité | Marchés électricité gagnés (36 mois, Wallonie + Bruxelles) |
|---|---|---|---|---|---|
| TSAV (7712) | 3 | MB 209 428 € | 5 030 € | 2,4 % de la MB | 14 lots, 164 945 € (alarme, accès, vidéo) |
| Installations, Maintenance et Constructions Électrotechniques (6180) | 23,9 | MB 2 435 338 € | 356 922 € | 14,7 % de la MB | 10 lots, 2,61 M€ |
| Aegentis (7022) | 10 | MB 736 933 € | 37 604 € | 5,1 % de la MB | 8 lots, 654 701 € |
| AES (7971) | 22,5 | MB 1 220 325 € | 48 578 € | 4,0 % de la MB | 5 lots, 766 022 € |
| D.E.I. (7700) | 20,3 | MB 1 606 016 € | 227 806 € | 14,2 % de la MB | 6 lots, 1,33 M€ |
| Lexar Technics (7140) | 48,9 | CA 14 922 600 € | 2 053 394 € | 13,8 % du CA | 12 lots, 1,20 M€ (éclairage) |
| Sotrelco (7100) | 115,5 | CA 39 581 560 € | 1 301 771 € | 3,3 % du CA | 7 lots, 17,9 M€ |
| Jacops Sud (6000) | 268,9 | CA 58 743 336 € | 2 582 628 € | 4,4 % du CA | 13 lots, 1,87 M€ |
| Mignone (7170) | 93,9 | CA 30 674 005 € | 105 087 € | 0,3 % du CA | 5 lots, 3,40 M€ |
| Technord (7500) | 304,4 | CA 97 247 138 € | 5 508 622 € | 5,7 % du CA | 5 lots, 1,27 M€ (HT/MT) |
| Wanty (7134) | 773 | CA 197 013 073 € | −1 521 147 € | −0,8 % du CA | 9 lots, 2,79 M€ (éclairage) |

- Les petites sociétés (schéma abrégé ou micro) ne publient pas leur chiffre d'affaires, seulement la **marge brute** (rubrique 9900).
- **Marge brute par ETP des PME d'électricité** : de 54 237 € (AES) à 101 897 € (IMCE).
- **Taille des acteurs** : les marchés électricité sont gagnés à la fois par des **PME locales de 3 à 25 ETP** et par des **groupes de 100 à 800 ETP**, pour qui ces marchés pèsent peu (0,4 à 3,7 % du CA, sauf Sotrelco 15 %).

## 4. Dossiers du top 3
_Phase 3._

## 5. Plan de test
_Phase 4._

## 6. « Je ne sais pas »
- **B2B** : plafond exact de la franchise TVA (à confirmer par ton comptable ou le SPF Finances) ; arrêté royal qui fixe les premiers lieux soumis à la loi sur l'air intérieur en 2027 ; qualification requise pour l'analyse de risques ; nombre d'entreprises cibles par secteur (Statbel bloqué) ; délais de paiement B2B ; règles d'accès à la profession pour l'installation (électricité, réseau) ; ton plafond de budget ; ta zone de déplacement.
- **Belgique** : aucun classement de ventes belge relevé (Amazon.com.be non relevé, bol.com bloqué). → Captures bol.com et Amazon.com.be de ta part (voir la liste des exports).
- **Tendance et saisonnalité** : non mesurées. → Exports Google Trends BE/FR sur 5 ans pour les finalistes.
- **Avis négatifs** des produits leaders : non collectés. → À faire en Phase 2 sur les 10 finalistes.
- Restrictions sur le plomb dans les articles de pêche (C11), règles sur les semences (C17), norme applicable aux bouillottes (C20), statut « jouet » d'un puzzle adulte (C02) : à vérifier.
- Conditions d'éligibilité vendeur TikTok Shop BE/FR pour un indépendant : non vérifiées.
- Frais de traitement douanier d'environ 2 €/colis au 1er novembre 2026 : absents de la source officielle S002 ; à vérifier.
- Référence juridique (n° de règlement) et date de fin du droit de 3 € : absentes de S002 ; à vérifier.

## 7. Sources
Voir `sources.csv`.
