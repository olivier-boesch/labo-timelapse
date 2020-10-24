# labo-timelapse
Comment faire des films pour des expériences qui durent...

## Le Système

### Photos

![pylapse all](https://raw.githubusercontent.com/olivier-boesch/labo-timelapse/main/media/v1_complete.jpg)

![pylapse all](https://raw.githubusercontent.com/olivier-boesch/labo-timelapse/main/media/v1_screen.jpg)


### Composants

#### Matériel

Pour le système (tel que sur la photo), Vous avez besoin :

* Un raspberry pi 3B (or 3B+) avec Raspberry Pi OS (debian buster) installé
* Un écran officiel raspberry 7" (possible de l'acheter ici : https://www.kubii.fr/ecrans-afficheurs/1131-ecran-tactile-officiel-7-800x480-kubii-640522710829.html )
* un boitier de marque oneNineDesign (comme celui ci : https://www.welectron.com/OneNineDesign-Raspberry-Pi-3-Touch-Screen-Case-White )
* Une Camera 5Mpx (comme celle ci : https://www.kubii.fr/cameras-accessoires/2195-module-camera-5mp-avec-focus-ajustable-kubii-3272496011090.html )

* Une pièce imprimée en 3D (en PLA) (disponible dans ce dépôt)
![pylapse mount](https://raw.githubusercontent.com/olivier-boesch/labo-timelapse/main/media/pylapse_mount.png)

* Un profilé aluminium creux de 10mm de côté (vendu en 1m ici : https://www.leroymerlin.fr/v3/p/produits/tube-carre-aluminium-brut-argent-l-1-m-x-l-1-cm-x-h-1-cm-e1501604704 )

* visserie : 2x M5x40mm (vis à tête plate et écrou à oreille), 3x M4x15mm (vis à tête plate et écrou standard)

* un collier de srrage plastique (max 2.5mm de large)

* un peu de scotch double-face (type miroirs)

#### Logiel

* les dépendances (on peut les installer automatiquement avec le script **install_dependencies.sh**)
    * la branche **master** de kivy
    * picamera
* le logiciel qui est dans le répertoire src

### Assemblage / Installation

#### Montage

Coming soon...

#### Installation

* cloner le dépôt github : `git clone https://github.com/olivier-boesch/labo-timelapse.git`
* aller dans le répertoire du dépôt : `cd labo-timelapse`
* installer les dépendances : `bash install_dependencies.sh`
* aller dans le répertoire des sources : `cd src`
* lancer le programme : `python3 main.py`

## Exemples

Coming soon...

## Crédits

* icone USB : USB by Mister Pixel from the Noun Project



