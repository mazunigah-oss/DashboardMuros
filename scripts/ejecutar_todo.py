"""Ejecuta los 5 pasos en orden:  python ejecutar_todo.py"""
import runpy
import sys
from pathlib import Path

carpeta = Path(__file__).resolve().parent
sys.path.insert(0, str(carpeta))
for paso in ["paso1_regiones", "paso2_muros", "paso3_agrupar", "paso4_dxf", "paso5_dashboard"]:
    print(f"--- {paso} ---")
    runpy.run_path(str(carpeta / f"{paso}.py"), run_name="__main__")
