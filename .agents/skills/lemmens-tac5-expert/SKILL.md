---
name: lemmens-tac5-expert
description: Fournit l'expertise technique, l'adressage Modbus et les modes de fonctionnement de la VMC Lemmens TAC5. À utiliser chaque fois qu'une modification ou un diagnostic du composant lemmens_tac5 est demandé.
---

# Expertise VMC Lemmens TAC5

Ce document rassemble la connaissance métier pour interagir avec la régulation TAC5 de Lemmens via le protocole Modbus TCP. Utilisez ces informations pour diagnostiquer ou développer l'intégration Home Assistant `lemmens_tac5`.

## Architecture de l'intégration
L'intégration est locale et se trouve dans le dossier `custom_components/lemmens_tac5`.
- **`const.py`** : Définit toutes les adresses de registres Modbus.
- **`coordinator.py`** : Gère la boucle de *polling* via `AsyncModbusTcpClient` (PyModbus). Lit et écrit les registres.
- **`sensor.py`** / **`number.py`** / **`switch.py`** / **`button.py`** : Entités exposées dans Home Assistant.

## Principes du Modbus sur TAC5
- **Port par défaut :** 502
- **Décalage (Offset) :** La documentation officielle parle en adresses base 1 (ex: 40052). Dans le code (PyModbus), il faut utiliser l'adresse base 0 (ex: 51). Le préfixe "4" désigne simplement des registres de maintien (Holding Registers).
- **Format :** Toutes les valeurs sont des entiers (Integer). Les températures sont envoyées en dixièmes de degrés (ex: 215 = 21.5°C).

## Modes de Fonctionnement (Registre 51, doc: 40052)
Le mode de fonctionnement actuel de la VMC est crucial :
- `0` : OFF (Arrêt)
- `1` : CA (Constant Airflow - Débit Constant en m³/h)
- `2` : LS (Link Speed - Tension 0-10V)
- `3` : CPf (Constant Pressure avec calcul de débit)
- `4` : CPs (Constant Pressure avec sonde physique)
- `6` : TQ (Constant Torque - Couple Constant)
- `9` : INIT (Mode temporaire pendant le calibrage des filtres)

## Contrôle Maître (Registre 199, doc: 40200)
Pour que Home Assistant puisse imposer ses consignes, il doit prendre le contrôle sur la télécommande physique.
- `0` : Télécommande (RC) maître.
- `1` : Modbus maître (permet de changer la vitesse ou de l'éteindre via le registre 200).
- **Remarque :** L'arrêt de la machine peut aussi se faire plus radicalement en écrivant `0` dans le registre de Setup Mode (425).

## Alarme d'encrassement des filtres (Pressure Alarm)
Disponible uniquement en modes CA et LS. La VMC mémorise une "pression de référence" (calibrage) et surveille que la pression actuelle ne dépasse pas `Pression de référence + Delta`.
- Activer l'alarme : Écrire `1` au registre 430.
- Delta Air Neuf (Pa) : Registre 431.
- Delta Extraction (Pa) : Registre 432.
- Pressions actuelles : Registres 65 (Air Neuf) et 73 (Extraction).
- Pressions de référence stockées : Registres 61 (Air Neuf) et 63 (Extraction).
- **Procédure de Calibrage :** Écrire le débit de référence au registre 253, puis déclencher l'initialisation en écrivant `1` au registre 252.

## Résolution des problèmes courants
1. **Échec d'écriture Modbus** : Si la commande `client.write_register` échoue, assurez-vous que la VMC accepte l'ordre dans son mode de fonctionnement actuel (ex: changer la vitesse "II" est refusé en mode Pression Constante).
2. **Pourcentages d'encrassement** : Si le calcul affiche 0%, c'est que la pression actuelle est inférieure ou très proche de la pression de référence (filtres propres ou VMC venant d'être calibrée).
3. **Mise à jour (Polling)** : Ne surchargez pas le bus Modbus de requêtes individuelles. Lisez les registres par blocs (`count=X`) dans le `coordinator.py` quand c'est possible.

## Outils et Environnement (CLI Home Assistant)
L'environnement dans lequel vous évoluez permet d'utiliser directement la commande `ha` (Home Assistant CLI) dans le terminal (système Home Assistant OS).
- Pour appliquer les changements de code du composant, n'hésitez pas à utiliser `ha core restart` ou la commande Docker `docker restart homeassistant`.
- Pour vérifier les erreurs, vous pouvez consulter les logs avec `ha core logs` ou utiliser directement l'accès au conteneur.