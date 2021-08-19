from random import choice
from flask import Flask
from experta import *
import queue


class Corona(Fact):
    pass


class Raiz(Fact):
    pass


class Casos(Fact):
    pass


class PiezaDentaria(Fact):
    pass


class ExtraccionDentaria(Fact):
    pass


class AsistenteDental(KnowledgeEngine):

    q = queue.Queue()

    @Rule(
        OR(Corona(fracturada='si'),
            AND(Corona(cariada='si'), Corona(destruida='si')),
            Raiz(raizRecuperable="no"),
            Casos(supernumerario="si"),
            PiezaDentaria(malUbicada="si")), salience=1)
    def extraccion(self):
        self.result = "Extracción"

    @Rule(ExtraccionDentaria(realizada="si"), salience=2)
    def colocacion(self):
        self.result = "Colocación"

    @Rule(Corona())
    def any(self):
        self.q.put(self.result)
    
    def reset(self):
        self.result = "Sin tratamiento"
        super().reset()

    def get(self):
        return self.q.get()


engine = AsistenteDental()
app = Flask(__name__)


@app.route("/test")
def test():
    engine.reset()
    # choice(['si', 'no'])
    engine.declare(
        Corona(fracturada="no", cariada="no", destruida="no"),
        Raiz(raizRecuperable="no"),
        Casos(supernumerario="no"),
        PiezaDentaria(malUbicada="no"),
        ExtraccionDentaria(realizada="si"))
    engine.run()
    result = engine.get()
    return "<h2 style='color:grey'>" + result + "</h2>"

@app.route("/")
def main():
    return "<h2 style='color:grey'>Fallas Backend</h2>"


if __name__ == "__main__":
    app.run(host='0.0.0.0')
