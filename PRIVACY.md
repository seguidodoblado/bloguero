# Política de privacidad / Privacy Policy

## 🇪🇸 Español

Última actualización: 5 de octubre de 2026.

Bloguero es una aplicación de escritorio de uso personal. No tiene servidor ni cuenta propios, y su autor
no recibe ningún dato de quien la usa.

## Qué datos trata

- **Tu cuenta de Google y tu blog.** Para listar, crear, editar, publicar y borrar entradas, la aplicación pide
  permiso para administrar tu cuenta de Blogger (el ámbito `https://www.googleapis.com/auth/blogger`). Solo se
  usa para eso.
- **Las entradas de tu blog**, que se guardan en una caché local para poder trabajar sin conexión.
- **Tus ajustes** (idioma y tema).

## Dónde se guardan

Todo queda en tu equipo:

- El **token de renovación** de Google, en el llavero del sistema (libsecret), nunca en disco en claro.
- Las **credenciales del cliente OAuth** que tú descargas de Google Cloud, en `~/.config/bloguero/client_secret.json`.
- La **caché** de blogs y entradas, en `~/.cache/bloguero/bloguero.db`.
- Un **registro de errores**, en `~/.cache/bloguero/bloguero.log` (solo el tipo de error y su traza, sin el contenido de las entradas ni credenciales).
- Los **ajustes**, en `~/.config/bloguero/settings.json`.

## Con quién se comparten

Con nadie. La aplicación solo se comunica con los servicios de Google (inicio de sesión y Blogger API), con
tu propia cuenta y tu propio proyecto de Google Cloud. No incluye analítica, telemetría, publicidad ni
servicios de terceros, y no vende ni cede datos.

## Cómo borrar tus datos o retirar el acceso

- **Retirar el acceso:** en tu cuenta de Google, en *Seguridad* → *Tus conexiones a aplicaciones y servicios de
  terceros*, elimina Bloguero.
- **Borrar los datos locales:** elimina `~/.config/bloguero/` y `~/.cache/bloguero/`, y la entrada `bloguero`
  del llavero del sistema.
- Desinstalar la aplicación no borra esos datos por sí solo.

## Cambios en esta política

Si cambia, se actualizará este documento y la fecha de arriba; el historial está en el repositorio.

## Contacto

Jose Antonio Seguido Doblado · jose.antonio.seguido@gmail.com

---

## 🇺🇸 English

Last updated: October 5, 2026.

Bloguero is a desktop application for personal use. It has no server or account of its own, and its author
does not receive any data from the people who use it.

## What data it handles

- **Your Google account and your blog.** To list, create, edit, publish and delete posts, the application asks
  for permission to manage your Blogger account (the `https://www.googleapis.com/auth/blogger` scope). It is
  used for that only.
- **Your blog's posts**, which are stored in a local cache so you can work offline.
- **Your settings** (language and theme).

## Where it is stored

Everything stays on your computer:

- The Google **refresh token**, in the system keyring (libsecret), never in clear text on disk.
- The **OAuth client credentials** that you download from Google Cloud, in `~/.config/bloguero/client_secret.json`.
- The **cache** of blogs and posts, in `~/.cache/bloguero/bloguero.db`.
- An **error log**, in `~/.cache/bloguero/bloguero.log` (only the error type and its traceback, without the content of your posts or credentials).
- The **settings**, in `~/.config/bloguero/settings.json`.

## Who it is shared with

No one. The application only communicates with Google services (sign-in and the Blogger API), with your own
account and your own Google Cloud project. It includes no analytics, telemetry, advertising or third-party
services, and it does not sell or give away data.

## How to delete your data or revoke access

- **Revoke access:** in your Google account, under *Security* → *Your connections to third-party apps and
  services*, remove Bloguero.
- **Delete the local data:** remove `~/.config/bloguero/` and `~/.cache/bloguero/`, and the `bloguero` entry
  from the system keyring.
- Uninstalling the application does not delete that data by itself.

## Changes to this policy

If it changes, this document and the date above will be updated; the history is in the repository.

## Contact

Jose Antonio Seguido Doblado · jose.antonio.seguido@gmail.com
