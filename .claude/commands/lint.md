1---
allowed-tools: Bash, Read, Glob
argument-hint: [file-path] | [--fix] | --all
description: Linting y analisis estatico de codigo Python con ruff, flake8 y bandit
---

# Lint - ServicesSound

Analizar codigo: $ARGUMENTS

## Herramientas disponibles

- **ruff** — linter rapido (reemplaza flake8 + isort + pyupgrade)
- **flake8** — linter clasico PEP8
- **bandit** — analisis de seguridad Python
- **mypy** — type checking estatico

## Pasos

1. **Linting general**

```bash
# Con ruff (preferido)
ruff check src/ config/ --fix $ARGUMENTS

# Con flake8 como fallback
flake8 src/ config/ --max-line-length=100 --ignore=E203,W503

# Ver estadisticas
ruff check src/ --statistics
```

2. **Analisis de seguridad**

```bash
bandit -r src/ config/ -ll -f text
```

3. **Type checking**

```bash
mypy src/ --ignore-missing-imports --no-strict-optional 2>/dev/null || echo "mypy no disponible"
```

4. **Imports no utilizados**

```bash
ruff check src/ --select F401 --fix
```

5. **Formato de codigo**

```bash
# Ver diferencias sin aplicar
ruff format src/ config/ --diff

# Aplicar formato
ruff format src/ config/
```

6. **Reporte consolidado**
   - Errores criticos (E) vs advertencias (W)
   - Issues de seguridad por nivel (LOW/MEDIUM/HIGH)
   - Archivos con mas problemas
   - Sugerencia de reglas a agregar a `pyproject.toml`
