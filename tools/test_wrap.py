import textwrap

MENSAJE_LOCAL = ("En Unimark encontrarás productos de calidad a precios "
                 "justos y atención rápida y amable. Visítanos hoy y descubre "
                 "por qué nuestros clientes confían en nosotros.")

linea = "=" * 50
width = len(linea)
mensaje_lineas = textwrap.wrap(MENSAJE_LOCAL, width=width, break_long_words=False, break_on_hyphens=False)
mensaje_formateado = "\n".join([ml.center(width) for ml in mensaje_lineas]) + "\n"
print(linea)
print('\n' + mensaje_formateado + '\n')
print(linea)

