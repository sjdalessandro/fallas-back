from flask import Flask, request, jsonify
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

    @Rule(ExtraccionDentaria(realizada="si"), salience=2)
    def colocacion(self):
        self.result = "colocación"

    @Rule(
        OR(Corona(fracturada='si'),
            AND(Corona(cariada='si'), Corona(destruida='si')),
            Raiz(raizRecuperable="no"),
            Casos(supernumerario="si"),
            PiezaDentaria(malUbicada="si")), salience=1)
    def extraccion(self):
        self.result = "extracción"

    @Rule(Corona())
    def any(self):
        self.q.put(self.result)
    
    def reset(self):
        self.result = "sin tratamiento"
        super().reset()

    def get(self):
        return self.q.get()


engine = AsistenteDental()
app = Flask(__name__)


def setArgument(json, key, defaultValue):
    if not key in json:
        json[key] = defaultValue
    value = json[key]
    if (value != 'si' and value != 'no'):
        json[key] = defaultValue


def setArguments(json):
    setArgument(json, 'fracturada', 'no')
    setArgument(json, 'cariada', 'no')
    setArgument(json, 'destruida', 'no')
    setArgument(json, 'raizRecuperable', 'si')
    setArgument(json, 'supernumerario', 'no')
    setArgument(json, 'malUbicada', 'no')
    setArgument(json, 'realizada', 'no')


@app.route("/consulta", methods=['POST'])
def test():
    if not request.json:
        return jsonify({'Message': 'Request without JSON body.'})

    json = request.json
    setArguments(json)

    engine.reset()
    engine.declare(
        Corona(fracturada=json['fracturada'], cariada=json['cariada'], destruida=json['destruida']),
        Raiz(raizRecuperable=json['raizRecuperable']),
        Casos(supernumerario=json['supernumerario']),
        PiezaDentaria(malUbicada=json['malUbicada']),
        ExtraccionDentaria(realizada=json['realizada']))
    engine.run()
    result = engine.get()
    return jsonify({'Tratamiento': result})


@app.route("/")
def main():
    return "<h2 style='color:grey'>Fallas Backend</h2>"


if __name__ == "__main__":
    app.run(host='0.0.0.0')
