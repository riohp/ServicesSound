---
allowed-tools: Read, Bash, Grep, Glob
argument-hint: [file-path] | [module] | --full
description: Revision completa de calidad de codigo Python: seguridad, rendimiento, arquitectura y testing
---

# Code Review - ServicesSound

Realizar revision de codigo: $ARGUMENTS

## Estado actual

- Git status: !`git status --porcelain`
- Cambios recientes: !`git diff --stat HEAD~3`
- Ultimos commits: !`git log --oneline -5`
- Entorno Python: !`python --version 2>&1 && conda info --envs 2>/dev/null | head -5`

## Pasos de revision

1. **Estructura del proyecto**
   - Revisar organizacion de modulos (`src/audio`, `src/network`, `src/gui`, `config`)
   - Verificar `__init__.py` con exports correctos
   - Revisar `setup.py` y `environment.yml` por dependencias faltantes o erroneas

2. **Calidad de codigo Python**
   - Buscar code smells, anti-patrones, variables no usadas
   - Verificar consistencia de estilo (PEP 8)
   - Revisar manejo de excepciones y logging
   - Detectar imports no utilizados

3. **Revision de seguridad**
   - Credenciales o secrets hardcodeados
   - Validacion de inputs de red (puertos, IPs)
   - Uso seguro de threads y recursos compartidos
   - Verificar que no haya `eval()` o `exec()` inseguros

4. **Rendimiento**
   - Revisar uso de threads y potenciales race conditions
   - Identificar bloqueos en el hilo principal (GUI)
   - Verificar manejo de buffers de audio (chunk size, queues)
   - Detectar memory leaks en loops de larga duracion

5. **Arquitectura**
   - Separacion entre GUI, audio y red
   - Mecanismo de comunicacion entre componentes (callbacks, queues, eventos)
   - Verificar que `AudioServer` y `ServiceDiscovery` sean reemplazables/testeables

6. **Coverage de tests**
   - Revisar archivos en `test/` — actualmente vacios
   - Identificar funciones criticas sin cobertura
   - Sugerir casos de prueba especificos para audio y red

7. **Documentacion**
   - Docstrings en clases y funciones publicas
   - README actualizado con instrucciones de ejecucion
   - Comentarios en logica compleja (streaming, Zeroconf)

8. **Recomendaciones priorizadas**
   - Critico: bloqueos de funcionalidad core
   - Alto: bugs potenciales o seguridad
   - Medio: calidad y mantenibilidad
   - Bajo: estilo y documentacion

Incluir rutas de archivo y numeros de linea en cada hallazgo.
