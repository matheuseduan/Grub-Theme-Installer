# 🎨 GRUB Theme Installer

> Interface gráfica (PySide6 / Qt) para instalar temas personalizados no GRUB2 em sistemas Debian e derivados.

![Dev Matheus Eduan](https://img.shields.io/badge/Dev-Matheus_Eduan-blue?&logo=devbox)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![PySide6](https://img.shields.io/badge/PySide6-6.6%2B-green?logo=qt)
![Debian](https://img.shields.io/badge/Debian%20%2F%20Ubuntu-compatible-red?logo=debian)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ O que o programa faz

1. **Seleciona** a pasta do tema via interface gráfica
2. **Copia** a pasta para `/boot/grub/themes/<nome-da-pasta>/`
   - Cria o diretório `themes/` caso não exista
   - Substitui instalação anterior se já existir
3. **Edita** `/etc/default/grub` automaticamente:
   - Localiza `GRUB_THEME=` (comentado ou não) e substitui o valor
   - Se não existir, adiciona ao final do arquivo
4. **Executa** `update-grub` (opcional, habilitado por padrão)

---

## 🖥️ Interface

```
┌─────────────────────────────────────────────────┐
│  🎨 GRUB Theme Installer            ✔  Root     │
├─────────────────────────────────────────────────┤
│  📁 Selecionar pasta do tema                    │
│  [ /home/user/meu-tema ____________] [Procurar] │
│                                                 │
│  🔍 Caminhos que serão utilizados               │
│  Destino:   /boot/grub/themes/meu-tema/         │
│  theme.txt: /boot/grub/themes/meu-tema/theme.txt│
│  Status:    ✔ theme.txt encontrado              │
│                                                 │
│  📋 Log de instalação                           │
│  ╔══════════════════════════════════════════╗   │
│  ║ ✦  GRUB Theme Installer iniciado.        ║   │
│  ║ ✔  Executando como root — OK.            ║   │
│  ╚══════════════════════════════════════════╝   │
│                                                 │
│  [☑ Executar update-grub]  [🚀 Instalar Tema]  │
└─────────────────────────────────────────────────┘
```

---

## 📋 Requisitos

| Dependência | Versão mínima |
|-------------|---------------|
| Python      | 3.9+          |
| PySide6     | 6.6.0+        |
| Sistema     | Debian / Ubuntu / derivados |

---

## 🚀 Instalação

### Opção 1 — Pacote `.deb` (recomendado)

Baixe o `.deb` na [página de Releases](../../releases/latest) e instale:

```bash
sudo apt install ./grub-theme-installer_1.0.1_all.deb
```

O `apt` resolve todas as dependências automaticamente. Após instalar, o programa aparece no **menu de aplicativos** ou pode ser chamado pelo terminal:

```bash
grub-theme-installer
```

### Opção 2 — Direto do código-fonte

```bash
# Clone o repositório
git clone https://github.com/matheuseduan/Grub-Theme-Installer.git
cd Grub-Theme-Installer/

# Instale a dependência Python
pip3 install -r requirements.txt --break-system-packages

# Execute
python3 main.py
```

> O programa detecta que não está rodando como root e pede a senha automaticamente via `pkexec` (diálogo gráfico) ou `sudo` (terminal).

---

## 🔑 Elevação de privilégios

O programa precisa de acesso root para:
- Copiar arquivos para `/boot/grub/themes/`
- Editar `/etc/default/grub`
- Executar `update-grub`

Ao iniciar sem root, ele se relança automaticamente:
1. Tenta `pkexec` → abre um **diálogo gráfico** nativo do PolicyKit
2. Fallback para `sudo -E` no terminal

Se ainda assim a janela não abrir (erro de `libxcb` / display):
```bash
sudo -E python3 main.py
```

---

## 🔧 O que é editado em `/etc/default/grub`

O programa usa regex para localizar `GRUB_THEME=` com qualquer valor (inclusive linhas comentadas) e substituir pela nova linha.

**Antes:**
```
GRUB_THEME=""
```

**Depois:**
```
GRUB_THEME="/boot/grub/themes/meu-tema/theme.txt"
```

Se não existir nenhuma ocorrência, a linha é adicionada ao final do arquivo.

---

## 📂 Estrutura do repositório

```
grub-theme-installer/
├── main.py                    # Aplicação principal (GUI PySide6 + lógica)
├── requirements.txt           # Dependências Python
├── assets/
│   └── icon.png               # Ícone do aplicativo
├── packaging/                 # Tudo relacionado ao pacote .deb
│   ├── build-deb.sh           # Script para gerar o .deb
│   └── debian-pkg-tree/       # Árvore-fonte do pacote
│       ├── DEBIAN/
│       │   ├── control        # Metadados + dependências
│       │   ├── postinst       # Executado após instalação
│       │   └── postrm         # Executado após remoção
│       ├── opt/grub-theme-installer/
│       │   ├── main.py
│       │   ├── requirements.txt
│       │   └── assets/icon.png
│       └── usr/
│           ├── bin/grub-theme-installer   # Wrapper executável
│           └── share/
│               ├── applications/grub-theme-installer.desktop
│               ├── icons/hicolor/256x256/apps/grub-theme-installer.png
│               └── doc/grub-theme-installer/
│                   ├── README.md
│                   └── copyright
├── README.md
└── SECURITY.md
```

---

## 🏗️ Gerando o pacote `.deb`

```bash
cd packaging
bash build-deb.sh
```

Ou manualmente:

```bash
chmod 755 packaging/debian-pkg-tree/DEBIAN/postinst
chmod 755 packaging/debian-pkg-tree/DEBIAN/postrm
chmod 755 packaging/debian-pkg-tree/usr/bin/grub-theme-installer
chmod 755 packaging/debian-pkg-tree/opt/grub-theme-installer/main.py
dpkg-deb --build --root-owner-group packaging/debian-pkg-tree \
  grub-theme-installer_$(grep '^Version:' packaging/debian-pkg-tree/DEBIAN/control | awk '{print $2}')_all.deb
```

---

## ⚠️ Avisos

- Faça backup de `/etc/default/grub` antes de usar pela primeira vez
- O tema precisa ter um arquivo `theme.txt` para ser reconhecido pelo GRUB
- Após instalar, reinicie o computador para ver o tema aplicado no boot
- Testado no Debian 11/12, Ubuntu 22.04+

---

## 📄 Licença

MIT © 2026
