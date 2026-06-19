#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
#  build-deb.sh — Gera o pacote .deb a partir da árvore-fonte
#
#  Uso:
#    cd packaging
#    bash build-deb.sh
#
#  O .deb gerado aparece na raiz do repositório.
# ═══════════════════════════════════════════════════════════════════════════
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
PKG_TREE="$SCRIPT_DIR/debian-pkg-tree"
CONTROL="$PKG_TREE/DEBIAN/control"

# Lê a versão diretamente do control
VERSION=$(grep '^Version:' "$CONTROL" | awk '{print $2}')
OUTPUT="$REPO_ROOT/grub-theme-installer_${VERSION}_all.deb"

echo "━━━ GRUB Theme Installer — Build .deb ━━━"
echo "  Versão : $VERSION"
echo "  Saída  : $OUTPUT"
echo ""

# Sincroniza main.py e assets da raiz do repo para dentro da árvore .deb
echo "→ Sincronizando arquivos fonte..."
cp "$REPO_ROOT/main.py"              "$PKG_TREE/opt/grub-theme-installer/main.py"
cp "$REPO_ROOT/requirements.txt"     "$PKG_TREE/opt/grub-theme-installer/requirements.txt"
cp "$REPO_ROOT/assets/icon.png"      "$PKG_TREE/opt/grub-theme-installer/assets/icon.png"
cp "$REPO_ROOT/assets/icon.png"      "$PKG_TREE/usr/share/icons/hicolor/256x256/apps/grub-theme-installer.png"
cp "$REPO_ROOT/README.md"            "$PKG_TREE/usr/share/doc/grub-theme-installer/README.md"

# Permissões obrigatórias para o dpkg-deb
echo "→ Ajustando permissões..."
chmod 755 "$PKG_TREE/DEBIAN/postinst"
chmod 755 "$PKG_TREE/DEBIAN/postrm"
chmod 755 "$PKG_TREE/usr/bin/grub-theme-installer"
chmod 755 "$PKG_TREE/opt/grub-theme-installer/main.py"

# Gera o .deb
echo "→ Construindo pacote..."
dpkg-deb --build --root-owner-group "$PKG_TREE" "$OUTPUT"

echo ""
echo "✅  Pacote gerado: $(basename "$OUTPUT")"
echo ""
echo "Para instalar:"
echo "    sudo apt install $OUTPUT"
