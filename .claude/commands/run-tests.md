---
allowed-tools: Bash, Read, Glob
argument-hint: [test-file] | [module] | --coverage | --verbose
description: Ejecuta tests con pytest, muestra coverage y sugiere tests faltantes para ServicesSound
---

# Ejecutar Tests - ServicesSound

Correr tests: $ARGUMENTS

## Estado previo

- Tests existentes: !`find test/ -name "*.py" -exec wc -l {} +`
- Dependencias de test: !`pip show pytest pytest-cov pytest-mock 2>/dev/null | grep -E "^Name|^Version"`

## Pasos

1. **Ejecutar suite de tests**

```bash
# Con coverage
pytest test/ -v --cov=src --cov-report=term-missing $ARGUMENTS

# Solo un modulo
pytest test/test_audio_server.py -v

# Con output detallado
pytest test/ -v -s --tb=short
```

2. **Verificar coverage por modulo**

```bash
pytest test/ --cov=src --cov-report=term-missing --cov-fail-under=60
```

3. **Analizar resultados**
   - Identificar tests que fallan y su causa raiz
   - Reportar porcentaje de coverage por archivo
   - Listar funciones/clases sin ningun test

4. **Sugerir tests faltantes**
   Para cada modulo sin tests, proponer casos de prueba:
   - `audio_server.py`: test de inicio/parada, test de thread safety
   - `service_discovery.py`: mock de Zeroconf, test de registro/deregistro
   - `helpers.py`: test de deteccion de IP, test de disponibilidad de puerto
   - `settings.py`: test de carga/guardado de configuracion

5. **Reporte final**
   - Total tests: pasados / fallidos / skipped
   - Coverage global
   - Archivos con 0% de coverage
   - Proximos 3 tests a implementar (por impacto)
