# -*- coding: utf-8 -*-
from flask import Flask
from flask import render_template
app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html',
        headline = u"Resultados Hackatón 2013 Córdoba",
        pubdate = "Nov. 9, 2013",
        description = u"""
<p>Resultados de las elecciones de diputados de Octubre en las escuelas a donde los ciudadanos de Córdoba votaron.</p>
<p>Cada círculo representa una escuela y el color representa al partido que obtuvo la mayoría de votos en esa escuela.</p>
""",
        disclaimer = u"""Los resultados totales corresponden sólo a los votos de las escuelas que están geolocalizadas.
                     Falta geolocalizar aproximadamente un 10% de las escuelas.
                     Es por eso que los números totales pueden diferir de los del escrutinio oficial.""",
        about = u"""
<p>Este mapa fue realizado en el marco del <a href="http://democraciaconcodigos.github.io/">1er Hackatón Sobre Datos Públicos de Córdoba: Democracia con Códigos</a>.
El código se encuentra disponible en <a href="https://github.com/democraciaconcodigos/election-2013">GitHub</a>.
</p>
<!--p>
    This is the test map taken from <a href="http://blogs.lanacion.com.ar/datafest/">Datafest 2013</a>.
    The source is <a href="http://palermo-hollywood.github.io/election-2013/">available on GitHub</a>.
</p-->
""",
    initial_lat=-31.94284,
    initial_lon=-63.599854
    )


if __name__ == '__main__':
  app.run(
        host="0.0.0.0",
        port=int("8000"),
        use_reloader=True,
        debug=True,
  )
