# -*- coding: utf-8 -*-
from flask import Flask
from flask import render_template
app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html',
        headline = "Resultados Hackaton 2013 Cordoba",
        pubdate = "Nov. 9, 2013",
        description = """
<p>Los resultados de las elecciones de diputados de Octubre en las escuelas donde los ciudadanos de Cordoba votaron </p>

<p>Cada circulo representa una escuela y el color representa al partido que obtuvo la mayoria de votos en esa escuela.</p>
""",
        about = """
<p>
    This is the test map taken from <a href="http://blogs.lanacion.com.ar/datafest/">Datafest 2013</a>.
    The source is <a href="http://palermo-hollywood.github.io/election-2013/">available on GitHub</a>.
</p>
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
