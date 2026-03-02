# juego/main.py
from juego.entorno_juego import EntornoJuego
from juego.visualizador import Visualizador


def main():
    entorno = EntornoJuego()
    vis = Visualizador(entorno)
    vis.run()


if __name__ == "__main__":
    main()