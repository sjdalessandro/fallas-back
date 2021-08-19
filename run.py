from random import choice
from flask import Flask
from experta import *
import queue


class Corona(Fact):
    pass


class AsistenteDental(KnowledgeEngine):

    q = queue.Queue()

    @Rule(Corona(fracturada='no', cariada='si', destruida='no'), salience=1)
    def fracturada(self):
        self.result = "Recuperación"

    @Rule(OR(Corona(fracturada='si'), Corona(destruida='si')), salience=1)
    def cariadaYDestruida(self):
        self.result = "Extracción"

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
    f = choice(['si', 'no'])
    c = choice(['si', 'no'])
    d = choice(['si', 'no'])
    engine.declare(Corona(fracturada=f, cariada=c, destruida=d))
    engine.run()
    result = engine.get()
    return "Fracturada: " + f + "<br>Cariada: " + c + "<br>Destruida: " + d + "<br><h2 style='color:grey'>" + result + "</h2>"

@app.route("/")
def main():
    return "<h2 style='color:grey'>Fallas Backend</h2>"


if __name__ == "__main__":
    app.run(host='0.0.0.0')
