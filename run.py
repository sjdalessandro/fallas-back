from flask import Flask, request, jsonify
from experta import *
import queue


class Encia(Fact):
    pass


class Corona(Fact):
    pass


class Esmalte(Fact):
    pass


class Dentina(Fact):
    pass


class Raiz(Fact):
    pass


class Pulpa(Fact):
    pass


class Casos(Fact):
    pass


class PiezaDentaria(Fact):
    pass


class AsistenteDental(KnowledgeEngine):

    q = queue.Queue()

    @Rule(OR(Esmalte(cariado='si'), Dentina(cariada='si')), salience=3)
    def reparación(self):
        self.result = {'Tratamiento': 'Reparación dentaria',
                       'Procedimiento': 'Primero eliminar la carie con un torno, removiendo así el tejido necrótico, luego aplicar ácido grabador para mejorar la adhesión de un elemento restaurativo, que puede ser de composite o una cerámica fotocurable, como ser amalgama o resina restauradora.',
                       'Herramientas': 'Fresas, torno, anestesia de ser necesario, ácido grabador, espátula, elemento restaurador.'}


    @Rule(OR(Encia(infectada='si'), Pulpa(cariada='si')), salience=2)
    def endodoncia(self):
        self.result = {'Tratamiento': 'Tratamiento de conducto',
                       'Procedimiento': 'Primero limpiar los conductos con las limas, luego taparlos con los conos de gutapercha. Finalmente para restaurar el diente aplicar ácido grabador para mejorar la adhesión de un elemento restaurativo, que puede ser de composite o una cerámica fotocurable, como ser amalgama o resina restauradora.',
                       'Herramientas': 'Limas, conos de gutapercha, anestesia, fresas, torno, ácido grabador, espátula, elemento restaurador.'}


    @Rule(
        OR(Corona(fracturada='si'),
            Raiz(recuperable="no"),
            Casos(supernumerario="si"),
            PiezaDentaria(malUbicada="si")), salience=1)
    def extraccion(self):
        self.result = {'Tratamiento': 'Extracción dentaria',
                       'Procedimiento': 'Primero aplicar la anestesia, luego con ayuda de fórceps y elevadores remover la pieza. De producirse una hemorragia utilizar las gasas para controlar el sangrado.',
                       'Herramientas': 'Anestesia, fórceps, elevadores y gasas'}


    @Rule(Corona())
    def any(self):
        self.q.put(self.result)
    

    def reset(self):
        self.result = {'Tratamiento': "Sin tratamiento",
                       'Procedimiento': '',
                       'Herramientas': ''}
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
    setArgument(json, 'esmalteCariado', 'no')
    setArgument(json, 'dentinaCariada', 'no')
    setArgument(json, 'enciaInfectada', 'no')
    setArgument(json, 'pulpaCariada', 'no')
    setArgument(json, 'coronaFracturada', 'no')
    setArgument(json, 'casoSupernumerario', 'no')
    setArgument(json, 'piezaDentariaMalUbicada', 'no')
    setArgument(json, 'raizRecuperable', 'si')


@app.route("/consulta", methods=['POST'])
def test():
    if not request.json:
        return jsonify({'Message': 'Request without JSON body.'})

    json = request.json
    setArguments(json)

    engine.reset()
    engine.declare(
        Corona(fracturada=json['coronaFracturada']),
        Raiz(recuperable=json['raizRecuperable']),
        Casos(supernumerario=json['casoSupernumerario']),
        PiezaDentaria(malUbicada=json['piezaDentariaMalUbicada']),
        Esmalte(cariado=json['esmalteCariado']),
        Dentina(cariada=json['dentinaCariada']),
        Encia(infectada=json['enciaInfectada']),
        Pulpa(cariada=json['pulpaCariada']))
    engine.run()
    result = engine.get()
    return jsonify(result)


@app.route("/")
def main():
    return "<h2 style='color:grey'>Fallas Backend</h2>"


if __name__ == "__main__":
    app.run(host='0.0.0.0')
