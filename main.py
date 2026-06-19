#!/usr/bin/env python3
"""
GRUB Theme Installer
Instala temas GRUB no Linux Debian com interface gráfica moderna (PySide6).

O programa pede a senha de root automaticamente (via pkexec/sudo) ao iniciar,
então basta executar normalmente:

    python3 main.py
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# ══════════════════════════════════════════════════════════════════════════════
#  Auto-elevação para root (antes de importar/iniciar a GUI)
# ══════════════════════════════════════════════════════════════════════════════
def _ensure_root() -> None:
    """
    Se o processo não estiver rodando como root, relança a si mesmo
    pedindo a senha. Tenta primeiro pkexec (diálogo gráfico nativo do
    PolicyKit); se não estiver disponível, cai para sudo no terminal.

    IMPORTANTE: pkexec por padrão NÃO repassa variáveis de ambiente como
    DISPLAY/XAUTHORITY para o processo elevado, o que faz o Qt falhar com
    "could not connect to display". Por isso elas são passadas explicitamente
    via `env` na linha de comando.
    """
    if os.geteuid() == 0:
        return

    script = os.path.abspath(sys.argv[0])
    args   = sys.argv[1:]

    def _which(cmd: str) -> bool:
        return shutil.which(cmd) is not None

    # Variáveis de ambiente necessárias para o Qt abrir uma janela gráfica
    # (X11 e/ou Wayland), repassadas manualmente para o processo elevado.
    env_vars = {}
    for var in (
        "DISPLAY",
        "XAUTHORITY",
        "WAYLAND_DISPLAY",
        "XDG_RUNTIME_DIR",
        "XDG_SESSION_TYPE",
        "QT_QPA_PLATFORM",
    ):
        value = os.environ.get(var)
        if value:
            env_vars[var] = value

    # Se XAUTHORITY não estiver definida, usa o padrão do usuário
    if "XAUTHORITY" not in env_vars:
        default_xauth = os.path.expanduser("~/.Xauthority")
        if os.path.isfile(default_xauth):
            env_vars["XAUTHORITY"] = default_xauth

    env_assignments = [f"{k}={v}" for k, v in env_vars.items()]

    # 1ª opção: pkexec → abre um diálogo GRÁFICO pedindo a senha
    if _which("pkexec"):
        try:
            os.execvp(
                "pkexec",
                [
                    "pkexec",
                    "env",
                    *env_assignments,
                    sys.executable,
                    script,
                    *args,
                ],
            )
        except OSError:
            pass  # se falhar, tenta a próxima opção

    # 2ª opção: sudo → pede a senha no terminal (se houver um), preservando
    # o ambiente gráfico com -E (mais simples e direto que pkexec aqui).
    if _which("sudo"):
        try:
            os.execvp(
                "sudo",
                ["sudo", "-E", sys.executable, script, *args],
            )
        except OSError:
            pass

    # Nenhuma opção de elevação disponível
    print(
        "ERRO: este programa precisa de privilégios root e não foi possível "
        "encontrar 'pkexec' nem 'sudo' no sistema.\n"
        "Execute manualmente como root, por exemplo:\n"
        "    su -c 'python3 " + script + "'",
        file=sys.stderr,
    )
    sys.exit(1)


_ensure_root()

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# ══════════════════════════════════════════════════════════════════════════════
#  Constantes de Sistema
# ══════════════════════════════════════════════════════════════════════════════
THEMES_DIR  = Path("/boot/grub/themes")
GRUB_CONFIG = Path("/etc/default/grub")

# ── Identidade do aplicativo (nome exibido + ícone) ──────────────────────────
APP_NAME    = "GRUB Theme Installer"
APP_ID      = "grub-theme-installer"   # usado como WM_CLASS / desktopFileName
ICON_PATH   = Path(__file__).resolve().parent / "assets" / "icon.png"

# ══════════════════════════════════════════════════════════════════════════════
#  Folha de Estilo (QSS) — visual escuro moderno
# ══════════════════════════════════════════════════════════════════════════════
QSS = """
QMainWindow, QWidget {
    background-color: #0d1117;
    color: #c9d1d9;
    font-family: "Segoe UI", "Noto Sans", sans-serif;
}

QFrame#card {
    background-color: #1e2530;
    border: 1px solid #30363d;
    border-radius: 10px;
}

QLabel#cardTitle {
    color: #8b949e;
    font-size: 12px;
    font-weight: bold;
    padding: 2px 0px;
}

QLabel#headerTitle {
    color: #c9d1d9;
    font-size: 18px;
    font-weight: bold;
}

QLabel#badgeOk {
    background-color: #3fb950;
    color: white;
    border-radius: 12px;
    padding: 5px 14px;
    font-size: 11px;
    font-weight: bold;
}

QLabel#badgeErr {
    background-color: #f85149;
    color: white;
    border-radius: 12px;
    padding: 5px 14px;
    font-size: 11px;
    font-weight: bold;
}

QLabel.dim {
    color: #8b949e;
    font-size: 12px;
}

QLabel.value {
    color: #58a6ff;
    font-size: 12px;
    font-family: "Monospace";
}

QLabel.statusOk {
    color: #3fb950;
    font-size: 12px;
}

QLabel.statusWarn {
    color: #d29922;
    font-size: 12px;
}

QLineEdit {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 10px;
    color: #c9d1d9;
    font-size: 13px;
}

QPushButton {
    background-color: #388bfd;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 18px;
    font-size: 13px;
    font-weight: bold;
}
QPushButton:hover { background-color: #2d7de0; }
QPushButton:disabled { background-color: #444c56; color: #8b949e; }

QPushButton#installBtn {
    background-color: #3fb950;
    color: white;
}
QPushButton#installBtn:hover {
    background-color: #2d9140;
    color: white;
}
QPushButton#installBtn:disabled {
    color: #c9d1d9;
}

QPlainTextEdit {
    background-color: #0d1117;
    color: #79c0ff;
    border: none;
    border-radius: 6px;
    font-family: "Monospace";
    font-size: 12px;
    padding: 8px;
}

QCheckBox {
    color: #c9d1d9;
    font-size: 13px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #30363d;
    background: #0d1117;
}
QCheckBox::indicator:checked {
    background: #388bfd;
    border: 1px solid #388bfd;
}

QScrollBar:vertical {
    background: #161b22;
    width: 10px;
}
QScrollBar::handle:vertical {
    background: #30363d;
    border-radius: 5px;
}
"""


# ══════════════════════════════════════════════════════════════════════════════
#  Worker (thread) — executa a instalação sem travar a UI
# ══════════════════════════════════════════════════════════════════════════════
class InstallWorker(QThread):
    log_signal     = Signal(str)
    done_signal    = Signal()
    error_signal   = Signal(str)

    def __init__(self, src_folder: Path, run_update_grub: bool):
        super().__init__()
        self.src_folder      = src_folder
        self.run_update_grub = run_update_grub

    def run(self) -> None:
        try:
            name      = self.src_folder.name
            dest      = THEMES_DIR / name
            theme_txt = dest / "theme.txt"

            # 1. Diretório de temas
            self.log_signal.emit("━━━ PASSO 1: Verificar diretório de temas ━━━")
            THEMES_DIR.mkdir(parents=True, exist_ok=True)
            self.log_signal.emit(f"  ✔  {THEMES_DIR} OK")

            # 2. Copiar pasta
            self.log_signal.emit("━━━ PASSO 2: Copiar pasta do tema ━━━")
            if dest.exists():
                self.log_signal.emit("  ⚠  Pasta anterior encontrada, removendo…")
                shutil.rmtree(dest)
            shutil.copytree(self.src_folder, dest)
            self.log_signal.emit(f"  ✔  Copiado → {dest}")

            # 3. Editar /etc/default/grub
            self.log_signal.emit("━━━ PASSO 3: Atualizar /etc/default/grub ━━━")
            self._patch_grub_config(str(theme_txt))
            self.log_signal.emit(f'  ✔  GRUB_THEME="{theme_txt}"')

            # 4. update-grub
            if self.run_update_grub:
                self.log_signal.emit("━━━ PASSO 4: Executar update-grub ━━━")
                result = subprocess.run(
                    ["update-grub"], capture_output=True, text=True
                )
                if result.returncode == 0:
                    self.log_signal.emit("  ✔  update-grub concluído com sucesso.")
                else:
                    self.log_signal.emit("  ⚠  update-grub retornou erro:")
                    for line in result.stderr.strip().splitlines():
                        self.log_signal.emit(f"     {line}")

            self.log_signal.emit("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            self.log_signal.emit("✅  Instalação concluída!")
            self.done_signal.emit()

        except PermissionError:
            self.error_signal.emit(
                "Permissão negada ao acessar arquivos de sistema.\n\n"
                "Execute o programa com:\n\n    sudo python3 main.py"
            )
        except Exception as exc:
            self.error_signal.emit(f"Erro inesperado:\n{exc}")

    def _patch_grub_config(self, theme_path: str) -> None:
        text     = GRUB_CONFIG.read_text(encoding="utf-8")
        new_line = f'GRUB_THEME="{theme_path}"'
        pattern  = re.compile(r'^[#\s]*GRUB_THEME\s*=.*$', re.MULTILINE)

        if pattern.search(text):
            text = pattern.sub(new_line, text)
            self.log_signal.emit("  →  GRUB_THEME encontrado e substituído.")
        else:
            if not text.endswith("\n"):
                text += "\n"
            text += f"\n{new_line}\n"
            self.log_signal.emit("  →  GRUB_THEME não existia; adicionado ao final.")

        GRUB_CONFIG.write_text(text, encoding="utf-8")


# ══════════════════════════════════════════════════════════════════════════════
#  Janela principal
# ══════════════════════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.selected: Path | None = None
        self.worker: InstallWorker | None = None

        self.setWindowTitle(APP_NAME)
        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))
        self.setFixedSize(720, 640)

        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self._build_header())

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(24, 16, 24, 16)
        body_layout.setSpacing(10)
        root_layout.addWidget(body)

        body_layout.addWidget(self._build_selector_card())
        body_layout.addWidget(self._build_preview_card())
        body_layout.addWidget(self._build_log_card(), stretch=1)
        body_layout.addLayout(self._build_footer())

        self._log("✦  GRUB Theme Installer iniciado.")
        self._log("✔  Executando como root — permissões de escrita OK.")
        self._log("─" * 52)

    # ── Header ─────────────────────────────────────────────────────────────────
    def _build_header(self) -> QWidget:
        header = QFrame()
        header.setStyleSheet("background-color: #161b22; border-bottom: 1px solid #30363d;")
        header.setFixedHeight(68)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(22, 0, 22, 0)

        title = QLabel("🎨   GRUB Theme Installer")
        title.setObjectName("headerTitle")
        layout.addWidget(title)
        layout.addStretch()

        badge = QLabel("✔  Root")
        badge.setObjectName("badgeOk")
        layout.addWidget(badge)

        return header

    # ── Card genérico ──────────────────────────────────────────────────────────
    def _card(self, title_text: str) -> tuple[QFrame, QVBoxLayout]:
        frame = QFrame()
        frame.setObjectName("card")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 10, 14, 14)
        layout.setSpacing(8)

        title = QLabel(title_text)
        title.setObjectName("cardTitle")
        layout.addWidget(title)

        return frame, layout

    # ── Seletor de pasta ───────────────────────────────────────────────────────
    def _build_selector_card(self) -> QFrame:
        card, layout = self._card("📁   Selecionar pasta do tema")

        row = QHBoxLayout()
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("Nenhuma pasta selecionada…")
        self.entry.setReadOnly(True)
        row.addWidget(self.entry, stretch=1)

        browse_btn = QPushButton("📂  Procurar")
        browse_btn.clicked.connect(self._browse)
        row.addWidget(browse_btn)

        layout.addLayout(row)
        return card

    # ── Preview de caminhos ────────────────────────────────────────────────────
    def _build_preview_card(self) -> QFrame:
        card, layout = self._card("🔍   Caminhos que serão utilizados")

        self.lbl_dest   = self._preview_row(layout, "Destino:")
        self.lbl_theme  = self._preview_row(layout, "theme.txt:")
        self.lbl_status = self._preview_row(layout, "Status:", is_status=True)

        return card

    def _preview_row(self, layout: QVBoxLayout, label_text: str, is_status: bool = False) -> QLabel:
        row = QHBoxLayout()
        label = QLabel(label_text)
        label.setProperty("class", "dim")
        label.setFixedWidth(80)
        row.addWidget(label)

        value = QLabel("—")
        value.setProperty("class", "dim" if is_status else "value")
        value.setWordWrap(True)
        row.addWidget(value, stretch=1)

        layout.addLayout(row)
        return value

    # ── Log ────────────────────────────────────────────────────────────────────
    def _build_log_card(self) -> QFrame:
        card, layout = self._card("📋   Log de instalação")
        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box, stretch=1)
        return card

    # ── Rodapé ─────────────────────────────────────────────────────────────────
    def _build_footer(self) -> QHBoxLayout:
        row = QHBoxLayout()

        self._chk_label_base = "Executar  update-grub  após instalar"
        self.chk_update_grub = QCheckBox()
        self.chk_update_grub.setChecked(True)
        self.chk_update_grub.toggled.connect(self._update_checkbox_label)
        self._update_checkbox_label(True)
        row.addWidget(self.chk_update_grub)
        row.addStretch()

        self.install_btn = QPushButton("🚀  Instalar Tema")
        self.install_btn.setObjectName("installBtn")
        self.install_btn.setFixedSize(185, 44)
        self.install_btn.setEnabled(False)
        self.install_btn.clicked.connect(self._install)
        row.addWidget(self.install_btn)

        return row

    def _update_checkbox_label(self, checked: bool) -> None:
        prefix = "✅  " if checked else ""
        self.chk_update_grub.setText(prefix + self._chk_label_base)

    # ── Ações ─────────────────────────────────────────────────────────────────
    def _browse(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Selecione a pasta do tema GRUB")
        if not folder:
            return

        self.selected = Path(folder)
        name      = self.selected.name
        dest      = THEMES_DIR / name
        theme_txt = dest / "theme.txt"

        self.entry.setText(str(self.selected))
        self.lbl_dest.setText(str(dest) + "/")
        self.lbl_theme.setText(str(theme_txt))

        src_theme = self.selected / "theme.txt"
        if src_theme.exists():
            self.lbl_status.setText("✔  theme.txt encontrado na pasta selecionada")
            self.lbl_status.setProperty("class", "statusOk")
        else:
            self.lbl_status.setText("⚠  theme.txt não encontrado (GRUB pode não reconhecer o tema)")
            self.lbl_status.setProperty("class", "statusWarn")
        self.lbl_status.setStyleSheet("")  # força reavaliação do QSS por classe
        self._refresh_style(self.lbl_status)

        self.install_btn.setEnabled(True)
        self._log(f"📁  Selecionado: {name}")
        self._log(f"🎯  Destino:     {dest}/")
        self._log(f"📄  theme.txt:   {theme_txt}")
        self._log("─" * 52)

    def _refresh_style(self, widget: QWidget) -> None:
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    def _install(self) -> None:
        if not self.selected or (self.worker and self.worker.isRunning()):
            return

        self.install_btn.setEnabled(False)
        self.install_btn.setText("⏳  Instalando…")

        self.worker = InstallWorker(self.selected, self.chk_update_grub.isChecked())
        self.worker.log_signal.connect(self._log)
        self.worker.done_signal.connect(self._on_done)
        self.worker.error_signal.connect(self._on_error)
        self.worker.start()

    def _on_done(self) -> None:
        self.install_btn.setEnabled(True)
        self.install_btn.setText("🚀  Instalar Tema")
        QMessageBox.information(
            self,
            "Instalação Concluída",
            "✅  Tema GRUB instalado com sucesso!\n\n"
            "Reinicie o computador para visualizar o novo tema no boot.",
        )

    def _on_error(self, msg: str) -> None:
        self.install_btn.setEnabled(True)
        self.install_btn.setText("🚀  Instalar Tema")
        self._log(f"❌  ERRO: {msg}")
        QMessageBox.critical(self, "Erro na Instalação", msg)

    def _log(self, msg: str) -> None:
        self.log_box.appendPlainText(msg)


# ══════════════════════════════════════════════════════════════════════════════
#  Ponto de Entrada
# ══════════════════════════════════════════════════════════════════════════════
def main() -> None:
    app = QApplication(sys.argv)

    # ── Identidade do app (corrige o nome exibido na barra de tarefas) ──────
    # Por padrão, ao rodar via "python3 main.py", a barra de tarefas mostra
    # "python3" porque o WM_CLASS é derivado do executável. Definindo o nome
    # da aplicação e o desktopFileName, a maioria dos ambientes (GNOME, KDE,
    # XFCE, etc.) passa a exibir o nome correto e o ícone do app.
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)
    app.setDesktopFileName(APP_ID)
    if ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(ICON_PATH)))

    app.setStyleSheet(QSS)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
