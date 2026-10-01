<p align="center">
  <img src="src/bloguero/assets/bloguero.svg" alt="Logotipo de Bloguero" width="128">
</p>

<h1 align="center">Bloguero</h1>

![release](https://img.shields.io/github/v/release/seguidodoblado/bloguero) ![license](https://img.shields.io/github/license/seguidodoblado/bloguero) ![last commit](https://img.shields.io/github/last-commit/seguidodoblado/bloguero) ![downloads](https://img.shields.io/github/downloads/seguidodoblado/bloguero/total) ![stars](https://img.shields.io/github/stars/seguidodoblado/bloguero?style=flat) ![issues](https://img.shields.io/github/issues/seguidodoblado/bloguero) ![language](https://img.shields.io/github/languages/top/seguidodoblado/bloguero)

<p align="center">
  Cliente de escritorio para Blogger: gestiona tus entradas sin pasar por el navegador.
</p>

Aplicación de escritorio (GTK 4 + PyGObject), de uso personal: todo ocurre en tu equipo, con tu propia
cuenta de Google y tu propio proyecto en Google Cloud.

- **Inicia sesión con Google** (OAuth de escritorio) y elige entre los blogs de tu cuenta.
- **Lista y filtra** las entradas por estado: publicadas, borradores, programadas.
- **Crea, edita, publica y borra** entradas, y vuelve a pasar una publicada a borrador.
- **Editor enriquecido (WYSIWYG)** nativo en GTK: negrita, cursiva, subrayado, tachado, títulos,
  listas, cita, código, enlaces y color de texto — sin depender de WebKit.
- **Etiquetas** y **programación de publicación** (fecha y hora).
- **Caché local y trabajo sin conexión**: la lista carga al instante desde SQLite, los cambios sin
  guardar se conservan aunque cierres la app, y si una entrada cambió en Blogger mientras la editabas
  se te avisa antes de sobrescribirla.
- **Interfaz en español e inglés** (gettext), e **idioma y tema (claro/oscuro) configurables** desde
  Preferencias, siguiendo el tema del sistema por defecto.

## Instalación

### 1. Proyecto en Google Cloud

Blogger no tiene una app pública: cada persona necesita su propio cliente OAuth.

1. Crea un proyecto en [Google Cloud Console](https://console.cloud.google.com/projectcreate) y activa
   la **Blogger API**.
2. Configura la pantalla de consentimiento OAuth (tipo *Externos*, con tu cuenta como usuario de
   prueba) y añade el scope `https://www.googleapis.com/auth/blogger`.
3. Crea un cliente OAuth de tipo **App de escritorio** y descarga el JSON de credenciales.
4. Guárdalo como `~/.config/bloguero/client_secret.json`.

### 2. El paquete `.deb`

```sh
git clone https://github.com/seguidodoblado/bloguero.git
cd bloguero
./build-deb.sh
sudo apt install ./bloguero_*.deb
```

El `.deb` resuelve sus dependencias vía `apt` (GTK 4, PyGObject, clientes de Google, etc.); no hace
falta `pip` ni un entorno virtual para usar la aplicación ya instalada.

## Uso

Al abrir Bloguero por primera vez, pulsa **Conectar con Google** y acepta el consentimiento OAuth (verás
un aviso de "app no verificada" mientras el proyecto esté en modo de prueba; es normal, acéptalo).
A partir de ahí, la lista de blogs y entradas se recuerda y la app vuelve a conectarse sola en los
siguientes arranques.

## Desarrollo

```sh
git clone https://github.com/seguidodoblado/bloguero.git
cd bloguero
python3 -m venv --system-site-packages .venv   # --system-site-packages: necesita el PyGObject del sistema
source .venv/bin/activate
pip install -e ".[dev]"

pytest                 # tests
python -m bloguero.app # ejecutar desde el código fuente
```

### Traducciones

El código fuente está en español (`_("texto")` con `gettext`). Para añadir o actualizar traducciones:

```sh
./i18n-extract.sh   # regenera po/bloguero.pot y actualiza po/*.po
# traduce las cadenas nuevas/fuzzy a mano en po/<idioma>.po
./i18n-compile.sh   # compila a .mo para probarlo
LANGUAGE=en python -m bloguero.app
```

Más detalle en [`po/README.md`](po/README.md).

## Licencia

Este proyecto se distribuye bajo la GNU General Public License, versión 3 (ver `LICENSE`).
