"""Punto de entrada: python app.py"""
import os

from app import create_app

app = create_app()

HOST, PUERTO = "127.0.0.1", 5000

if __name__ == "__main__":
    depuracion = os.environ.get("FLASK_DEBUG") == "1"
    # Con recarga automática el script se ejecuta dos veces; el aviso solo se imprime en el proceso que atiende.
    if not depuracion or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        url = f"http://{HOST}:{PUERTO}"
        print("\n" + "=" * 60)
        print("  Monitor Numérico de Centro de Datos")
        print(f"  Abra en el navegador:  {url}")
        print(f"  Glosario:              {url}/glosario/")
        print("  Para detener el servidor: Ctrl+C")
        print("=" * 60 + "\n", flush=True)
    app.run(debug=depuracion, host=HOST, port=PUERTO)
