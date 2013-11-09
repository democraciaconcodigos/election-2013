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

<p>Los circulos son de color para representar a ese partido que obtuvo la mayoria de votos y de tamanio para mostrar el margen de victoria..</p>
""",
        about = """
<p>
    This is a modified take on <a href="http://www.lanacion.com.ar/1633333-como-fueron-los-resultados-de-las-elecciones-en-la-escuela-donde-votaste">a map</a> published by <em>La Nacion</em>
    last week.
    It was developed by Team Hollywood Palermo at <a href="http://blogs.lanacion.com.ar/datafest/">Datafest 2013</a> in Buenos Aires.
    The source is <a href="https://github.com/palermo-hollywood/election-2013">available on GitHub</a>.
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
