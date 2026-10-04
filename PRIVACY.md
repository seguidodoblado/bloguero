<p align="right"><a href="PRIVACY.en.md">🇺🇸 English</a></p>

# Política de privacidad

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
