from scripts.parse_images_utils import *

lista_de_precios_por_semana = os.listdir("lista_de_precios_por_semana")

# test 1
process_tio_central_pdf(lista_de_precios_por_semana[0])