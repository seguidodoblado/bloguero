<p align="right"><a href="PRIVACY.md">🇪🇸 Español</a></p>

# Privacy Policy

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
