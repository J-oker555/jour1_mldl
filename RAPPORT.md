# Rapport

## Phase 1 - Ouvrir la caisse

- Lignes logiques lues: 88875
- Lignes chargees: 88679
- Lignes traitees a part: 196

Les lignes mises a part sont celles dont le nombre de champs ne correspond pas aux onze champs du manifeste.

Repartition des problemes:

- 12 champs au lieu de 11: 196

Exemples:

- Ligne 877: 12 champs au lieu de 11. Extrait: `10/1/2006 12:00 |  |  |  |  | 0 |  |  | ((EDITORIAL COMMENT ABOUT THE UFO PHENOMEN))  ufo+alien+reptiles | 10/30/2006 | 0 | 0`
- Ligne 1712: 12 champs au lieu de 11. Extrait: `10/14/2004 13:00 |  |  |  |  | 0 |  |  | With all the guns in this country...why hasn&#39t anyone taken a shot at one? | 10/27/2004 | 0 | 0`
- Ligne 1814: 12 champs au lieu de 11. Extrait: `10/14/2011 22:30 |  | nv |  |  | 0 | light | 22 | 3 Green lights | 10/19/2011 | 0 | 0`

## Phase 2 - Types et anomalies

Les conversions sont appliquees sans supprimer de ligne. Les valeurs impossibles deviennent `NaN` ou `NaT`, puis sont comptees et conservees pour l'analyse.

- `datetime` -> date et heure: 1220 valeurs invalides, 0 valeurs vides. Origine probable: temoin. Exemples fautifs: ['10/10/2005 24:00', '10/11/1994 24:00', '10/11/2006 24:00', '10/11/2012 24:00', '10/1/1972 24:00', '10/1/1981 24:00', '10/1/2001 24:00', '10/1/2003 24:00', '10/1/2009 24:00', '10/1/2012 24:00']
  - Nature: heure 24:00 non parseable: 1220
- `date_posted` -> date: 0 valeurs invalides, 0 valeurs vides. Origine probable: service de transmission. Exemples fautifs: []
- `duration_seconds` -> nombre: 3 valeurs invalides, 2 valeurs vides. Origine probable: capteur. Exemples fautifs: ['2`', '8`', '0.5`']
  - Nature: caractere parasite dans un nombre: 3
  - Nature: valeur vide: 2
- `latitude` -> nombre: 1 valeurs invalides, 0 valeurs vides. Origine probable: capteur. Exemples fautifs: ['33q.200088']
  - Nature: lettre dans un nombre: 1
- `longitude` -> nombre: 0 valeurs invalides, 0 valeurs vides. Origine probable: capteur. Exemples fautifs: []

## Phase 3 - Etiquette canular

Regle: un releve est marque comme canular si le temoignage contient un mot explicite comme hoax, fake, prank, joke, joking ou balloon prank.

- Releves marques canulars: 827
- Proportion: 0.93 %

Mots declencheurs trouves:

- `hoax`: 798
- `fake`: 9
- `prank`: 2
- `joke`: 15
- `joking`: 3

Exemples de releves marques:

- `a flying colorful disc above my car&#44 near Erie. ((NUFORC Note: Possible hoax?? PD))`
- `((HOAX??)) Short encounter with space craft on my way into my parking lot area.`
- `Silver egg shape over six houses. ((NUFORC Note: Possible hoax?? PD))`
- `Lights in Irvine October 2007: Hoax`
- `((HOAX??)) abduction. 500 Lights On Object0: Yes`

Limite: Cette regle rate les canulars qui ne sont pas avoues dans le texte et peut attraper a tort un temoignage qui nie explicitement le canular.

## Phase 4 - Premier verdict

Split stratifie avec 25% des donnees en test, graine aleatoire 42. Apprentissage: 66509 releves (620 canulars, 65889 non-canulars). Test: 22170 releves (207 canulars, 21963 non-canulars).

- Sur 100 canulars reels, le systeme en attrape: 100.00
- Sur 100 releves signales, vraiment canulars: 100.00

Matrice de confusion sur le jeu de test:

| Reel \ Predit | Pas canular | Canular |
| --- | ---: | ---: |
| Pas canular | 21963 | 0 |
| Canular | 0 | 207 |

## Phase 5 - Fuite de donnees

Le premier modele utilise une information derivee du temoignage alors que l'etiquette de canular vient aussi du temoignage. Ce score n'a donc pas le droit d'etre presente comme une prediction disponible avant lecture/traitement du dossier.

| Colonne modele | Source | Qui ecrit | Quand | Savait deja si canular |
| --- | --- | --- | --- | --- |
| `duration_seconds` | `duration_seconds` | capteur ou transmission | au moment du releve | non |
| `latitude` | `latitude` | capteur ou transmission | au moment du releve | non |
| `longitude` | `longitude` | capteur ou transmission | au moment du releve | non |
| `has_state` | `has_state` | capteur ou transmission | au moment du releve | non |
| `has_country` | `has_country` | capteur ou transmission | au moment du releve | non |
| `comment_length` | `comments` | temoin | apres observation | oui |
| `shape` | `shape` | capteur ou transmission | au moment du releve | non |
| `country` | `country` | capteur ou transmission | au moment du releve | non |
| `hour` | `hour` | capteur ou transmission | au moment du releve | non |
| `month` | `month` | capteur ou transmission | au moment du releve | non |
| `comment_hoax_keyword` | `comments` | temoin | apres observation | oui |

| Mesure | Avant retrait | Apres retrait |
| --- | ---: | ---: |
| Rappel canular | 100.00 % | 61.35 % |
| Precision canular | 100.00 % | 1.40 % |
| Accuracy | 100.00 % | 59.43 % |

## Phase 6 - Modele naif

- Accuracy du stagiaire qui repond toujours `pas canular`: 99.07 %
- Accuracy du modele propre: 59.43 %

L'accuracy seule est trompeuse ici parce que les canulars sont rares. Un systeme peut obtenir un score eleve en ignorant tous les canulars. Pour defendre le modele, il faut presenter le rappel et la precision de la classe canular.
