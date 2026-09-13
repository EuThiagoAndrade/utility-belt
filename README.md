# Utility Belt (`belt`)

Canivete suíço pessoal de terminal para Windows e Linux.

## Instalação e Atualização

Instalação isolada recomendada via `uv`:
```bash
uv tool install "git+https://github.com/EuThiagoAndrade/utility-belt.git@main"
uv tool update-shell
```

Para atualizar em qualquer máquina:
```bash
uv tool upgrade utility-belt
```

## Uso Rápido

```bash
belt --help
belt list
belt doctor
belt menu

# Informações do sistema (ferramenta piloto)
belt run system.info

# Docker
belt docker export --help
belt docker import --help

# Restic
belt restic backup --help
belt restic restore --help
belt restic check --help
```
