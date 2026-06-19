# Como Contribuir

Obrigado por querer contribuir! Aqui estão as diretrizes para facilitar o processo.

---

## Fluxo de trabalho

1. **Fork** o repositório
2. Crie uma branch descritiva:
   ```bash
   git checkout -b fix/erro-pkexec-wayland
   # ou
   git checkout -b feat/suporte-temas-grub-btrfs
   ```
3. Faça suas alterações e commit:
   ```bash
   git commit -m "fix: repassa WAYLAND_DISPLAY ao pkexec"
   ```
4. Abra um **Pull Request** descrevendo o que mudou e por quê

---

## Ambiente de desenvolvimento

```bash
git clone https://github.com/seu-usuario/grub-theme-installer.git
cd grub-theme-installer
pip3 install -r requirements.txt --break-system-packages
python3 main.py
```

Para lint:
```bash
pip install flake8 pyflakes
pyflakes main.py
flake8 main.py --max-line-length=100
```

---

## Gerando o pacote `.deb`

```bash
cd packaging
bash build-deb.sh
```

---

## Convenções de commit

Use prefixos semânticos:

| Prefixo   | Quando usar                          |
|-----------|--------------------------------------|
| `feat:`   | Nova funcionalidade                  |
| `fix:`    | Correção de bug                      |
| `docs:`   | Apenas documentação                  |
| `refactor:` | Refatoração sem mudança de comportamento |
| `chore:`  | Tarefas de manutenção (CI, deps...)  |

---

## Reportando bugs

Use o [template de bug report](.github/ISSUE_TEMPLATE/bug_report.md) e inclua:
- Distro e versão do SO
- Mensagens de erro completas
- Ambiente gráfico (GNOME, KDE, X11, Wayland…)
