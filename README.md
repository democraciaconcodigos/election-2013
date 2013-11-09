
Resultados por escuelas de las elecciones Argentina Octubre 2013

Getting started
---------------

Create a virtualenv to store all the code in a nice tupperware container.

```bash
$ virtualenv election-2013
```

Jump into it.

```bash
$ cd election-2013
$ . bin/activate
```

Clone the repository.

```bash
$ git clone git@github.com:democraciaconcodigos/election-2013.git repo
```

Jump into it.

```bash
$ cd repo
```

Install the other Python dependencies.

```bash
$ pip install -r requirements.txt
```

Fire up the Flask server that hosts our development pages.

```bash
$ python app.py
# Visit http://localhost:8000 in your browser and check it out.
```

To flatten the Flask site so it can be hosted without a server as static files.

```bash
# This will update the files in the ./build directory
$ python freeze.py
```

Heavily Based On The work of 
------------

https://github.com/palermo-hollywood/election-2013

This code was developed at Córdoba, Argentina By the Geolocalization Team 
