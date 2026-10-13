from pysentimiento import create_analyzer

analyzer = create_analyzer(task="sentiment", lang="es")

frases = [
    "Perdimos el partido pero estoy feliz",
    "No estoy feliz ni triste",
    "No me gustó nada la atención",
    "Qué bonito día, me encanta",
    "Hoy fui al mercado",
]
for f in frases:
    r = analyzer.predict(f)
    print(f, "->", r.output, r.probas)