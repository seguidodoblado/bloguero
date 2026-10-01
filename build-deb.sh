#!/bin/sh
set -eu
base=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
stage="$base/.deb-stage"
version=$(sed -n '1s/^[^ ]* (\([^)]*\)).*/\1/p' "$base/debian/changelog")
test -n "$version" || { echo "No se pudo leer la versión de debian/changelog" >&2; exit 1; }
upstream=${version%-*}
project_version=$(sed -n 's/^version = "\([^"]*\)"/\1/p' "$base/pyproject.toml")
init_version=$(sed -n 's/^__version__ = "\([^"]*\)"/\1/p' "$base/src/bloguero/__init__.py")
test "$upstream" = "$project_version" -a "$upstream" = "$init_version" || {
    echo "Versiones distintas: debian/changelog ($upstream), pyproject.toml ($project_version), __init__.py ($init_version)." >&2
    exit 1
}
package="$base/../bloguero_${version}_all.deb"
command -v dpkg-deb >/dev/null 2>&1 || { echo "Falta dpkg-deb (instala dpkg-dev)." >&2; exit 1; }
sh "$base/i18n-compile.sh"
rm -rf "$stage"
mkdir -p "$stage/DEBIAN" "$stage/opt/bloguero" "$stage/usr/bin" "$stage/usr/share/applications" "$stage/usr/share/icons/hicolor/scalable/apps"
cp -a "$base/src/bloguero" "$stage/opt/bloguero/"
find "$stage/opt/bloguero" -type d -name __pycache__ -prune -exec rm -rf {} +
cp "$base/debian/bloguero-launcher" "$stage/usr/bin/bloguero"
cp "$base/debian/bloguero.desktop" "$stage/usr/share/applications/"
cp "$base/src/bloguero/assets/bloguero.svg" "$stage/usr/share/icons/hicolor/scalable/apps/"
cp "$base/debian/postinst" "$stage/DEBIAN/postinst"
cat > "$stage/DEBIAN/control" <<EOF
Package: bloguero
Version: ${version}
Section: net
Priority: optional
Architecture: all
Depends: python3, python3-gi, gir1.2-gtk-4.0 (>= 4.10), python3-googleapi, python3-google-auth, python3-google-auth-oauthlib, python3-keyring, python3-markdown, python3-html2text
Maintainer: Jose Antonio Seguido Doblado <jose.antonio.seguido@gmail.com>
Homepage: https://github.com/seguidodoblado/bloguero
Description: Cliente de escritorio para Blogger
 Aplicación GTK para gestionar un blog de Blogger: listar, crear, editar,
 publicar y borrar entradas con un editor enriquecido, caché local y
 trabajo sin conexión.
EOF
chmod 755 "$stage/usr/bin/bloguero"
chmod 755 "$stage/DEBIAN/postinst"
dpkg-deb --build --root-owner-group "$stage" "$package"
rm -rf "$stage"
echo "Paquete generado: $package"
