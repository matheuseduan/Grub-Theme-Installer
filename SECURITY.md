# Política de Segurança

## Versões Suportadas

| Versão  | Suportada           |
| ------- | ------------------- |
| 1.0.1   | :white_check_mark:  |
| < 1.0   | :x:                 |

## Reportando uma Vulnerabilidade

Por favor, reporte vulnerabilidades de segurança através do recurso nativo
de reporte privado de vulnerabilidades do GitHub, em vez de abrir uma issue
pública:

1. Vá até a aba **Security** deste repositório
2. Clique em **Report a vulnerability**
3. Preencha com o máximo de detalhes possível:
   - Uma descrição da vulnerabilidade e seu impacto potencial
   - Passos para reproduzi-la
   - Versão(ões) afetada(s)
   - Qualquer código de prova de conceito, se aplicável

Isso mantém o reporte privado entre você e os mantenedores até que uma
correção seja lançada. Você pode encontrar mais informações sobre esse
recurso na [documentação do GitHub](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing/privately-reporting-a-security-vulnerability).

Nosso objetivo é confirmar o recebimento de novos reportes o mais rápido
possível e mantê-lo informado enquanto trabalhamos na resolução do problema.
Uma vez resolvido, coordenaremos a divulgação com você e daremos os créditos
no anúncio (a menos que você prefira permanecer anônimo).

## Escopo

Esta política se aplica ao código deste repositório. Como este projeto
requer privilégios de root para modificar arquivos de sistema
(`/boot/grub/themes/` e `/etc/default/grub`), preste atenção especial a
qualquer vulnerabilidade que possa permitir escalonamento de privilégio,
escrita arbitrária de arquivos ou execução de código como root.

Problemas em dependências de terceiros (ex: PySide6, Qt) devem ser
reportados diretamente aos respectivos mantenedores.
