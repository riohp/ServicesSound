"""
Configuración de rutas para el proyecto ServicesSoundAlexa
Este módulo se encarga de configurar correctamente el PYTHONPATH

"""

import sys
import os
from pathlib import Path

def setup_project_paths():
  
    # Obtener el directorio raíz del proyecto
    project_root = Path(__file__).parent.parent
    src_path = project_root / "src"
    
    # Agregar ambas rutas al sys.path si no están ya presentes
    paths_to_add = [str(project_root), str(src_path)]
    
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    # También configurar PYTHONPATH para subprocesos
    current_pythonpath = os.environ.get('PYTHONPATH', '')
    new_paths = [p for p in paths_to_add if p not in current_pythonpath]
    
    if new_paths:
        if current_pythonpath:
            os.environ['PYTHONPATH'] = os.pathsep.join([current_pythonpath] + new_paths)
        else:
            os.environ['PYTHONPATH'] = os.pathsep.join(new_paths)

# Ejecuta la configuración automáticamente cuando se importa este módulo
setup_project_paths()