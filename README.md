<p align="right"><a href="README.en.md">🇺🇸 English</a></p>

<p align="center">
  <img src="src/bloguero/assets/bloguero.svg" alt="Logotipo de Bloguero" width="128">
</p>

<h1 align="center">Bloguero</h1>

<p align="center">
  <img src="https://img.shields.io/github/v/release/seguidodoblado/bloguero" alt="release">
  <img src="https://github.com/seguidodoblado/bloguero/actions/workflows/ci.yml/badge.svg" alt="CI">
  <img src="https://github.com/seguidodoblado/bloguero/actions/workflows/cd.yml/badge.svg" alt="CD">
  <a href="https://github.com/seguidodoblado/bloguero/blob/main/LICENSE"><img src="https://img.shields.io/github/license/seguidodoblado/bloguero" alt="license"></a>
  <a href="https://github.com/seguidodoblado/bloguero/commits/main/"><img src="https://img.shields.io/github/last-commit/seguidodoblado/bloguero" alt="last commit"></a>
  <a href="https://github.com/seguidodoblado/bloguero/commits/main/"><img src="https://img.shields.io/github/commit-activity/t/seguidodoblado/bloguero" alt="total commits"></a>
  <img src="https://img.shields.io/github/downloads/seguidodoblado/bloguero/total" alt="downloads">
  <img src="https://img.shields.io/github/stars/seguidodoblado/bloguero?style=flat" alt="stars">
  <a href="https://github.com/seguidodoblado/bloguero/issues"><img src="https://img.shields.io/github/issues/seguidodoblado/bloguero" alt="issues"></a>
  <img src="https://img.shields.io/github/languages/top/seguidodoblado/bloguero" alt="language">
  <a href="https://codetime.dev"><img alt="CodeTime Badge" src="https://shields.jannchie.com/endpoint?style=flat&color=0284c7&url=https%3A%2F%2Fcodetime.dev%2Fv3%2Fusers%2Fshield%3Fuid%3D36830"></a>
  <a href="https://wakatime.com/badge/github/seguidodoblado/bloguero"><img src="https://wakatime.com/badge/github/seguidodoblado/bloguero.svg" alt="wakatime"></a>
</p>

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
  Preferencias, siguiendo el tema del sistema por defecto. El menú de la cabecera da acceso a
  Preferencias y a la ventana «Acerca de» estándar de GNOME.

## Documentación

Toda la documentación —instalación, guía de uso, especificaciones técnicas, solución de problemas y más— está en
la **[wiki del proyecto](https://github.com/seguidodoblado/bloguero/wiki)** (español e inglés).

## Licencia

Este proyecto se distribuye bajo la GNU General Public License, versión 3 (ver `LICENSE`).
