# Changelog

Todas as mudanças notáveis neste projeto são documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [1.0.1] — 2026-06-19

### Corrigido
- Dependência `policykit-1` substituída por `policykit-1 | polkitd` no `DEBIAN/control`,
  resolvendo o erro `Depende policykit-1 ... [no choices]` em Debian Trixie (13) e
  repositórios mais recentes onde o pacote de transição deixou de existir.

---

## [1.0.0] — 2026-06-18

### Adicionado
- Interface gráfica moderna com PySide6 / Qt (tema escuro inspirado no GitHub Dark)
- Seleção de pasta de tema via diálogo gráfico
- Preview dos caminhos de destino antes de instalar
- Edição automática de `/etc/default/grub` via regex (suporta linhas comentadas)
- Execução de `update-grub` com checkbox para habilitar/desabilitar
- Log de instalação em tempo real com thread dedicada (`QThread`)
- Auto-elevação de privilégios: tenta `pkexec` (diálogo gráfico) com fallback para `sudo`
- Repasse manual de variáveis `DISPLAY`/`XAUTHORITY`/`WAYLAND_DISPLAY` para o `pkexec`
- Pacote `.deb` nativo com `postinst` que instala PySide6 via `pip3`
- Atalho no menu de aplicativos com ícone e nome corretos
- Script `build-deb.sh` para recriar o pacote a partir da árvore-fonte
