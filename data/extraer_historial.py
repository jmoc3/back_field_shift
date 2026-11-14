# Realizar solicitudes HTTP hacia los servicios NASA POWER.
import requests


# Cliente encargado de consultar información climática histórica.
class NasaPower:

    # Endpoint principal  del servicio NASA POWER.
    BASE_URL = ("https://power.larc.nasa.gov/api/temporal/daily/point")

    # Variables climáticas que serán utilizadas por el sistema.
    VARIABLES = {

        # Temperatura media.
        "temperatura":"T2M",
        # Temperatura máxima.
        "temperatura_maxima":"T2M_MAX",
        # Temperatura mínima.
        "temperatura_minima":"T2M_MIN",
        # Precipitación corregida.
        "precipitacion":"PRECTOTCORR",

        # Humedad del suelo en la zona de raíces.
        "humedad_raiz": "GWETROOT"
    }

    # Inicializar cliente.
    def __init__(self):

        # Caché local para evitar múltiples consultas iguales.
        self.cache = {}

    # Ejecutar consulta HTTP  a NASA POWER.
    def consultar_nasa(self,parametros):

        # Ejecutar solicitud.
        respuesta = requests.get(self.BASE_URL,params=parametros,timeout=30)

        # Validar respuesta.
        respuesta.raise_for_status()

        # Convertir respuesta a formato JSON.
        return respuesta.json()

    # Obtener todas las variablesclimáticas necesarias para una ubicación específica.
    def obtener_datos_historicos(self,latitud,longitud,fecha_inicio,fecha_fin):

        # Crear clave única para caché.
        clave = (latitud,longitud,fecha_inicio,fecha_fin)

        # Devolver resultado ya calculado anteriormente.
        if clave in self.cache:

            return self.cache[clave]

        # Construir lista de variables NASA POWER.
        parametros_nasa = ",".join(self.VARIABLES.values())

        # Construir parámetros de consulta.
        parametros = {

            # Variables solicitadas.
            "parameters":parametros_nasa,
            # Comunidad agrícola.
            "community":"AG",
            # Latitud.
            "latitude":latitud,
            # Longitud.
            "longitude":longitud,
            # Fecha inicial.
            "start":fecha_inicio,
            # Fecha final.
            "end":fecha_fin,
            # Formato esperado.
            "format":"JSON"
        }

        # Consultar NASA POWER.
        try:
            datos = (self.consultar_nasa(parametros))

        # Capturar errores de red, timeout o respuesta inválida.
        except requests.exceptions.RequestException as error:

            raise RuntimeError(f"Error consultando NASA POWER: {error}")

        # Extraer variables climáticas devueltas.
        parametros_clima = (datos["properties"]["parameter"])

        # Estructura final que consumirá Persona 4.
        resultados = {}

        # Recorrer todas las variables configuradas.
        for nombre_variable, codigo_nasa in (self.VARIABLES.items()):

            # Extraer serie temporal.
            serie = (parametros_clima[codigo_nasa])

            # Eliminar registros inválidos enviados por NASA POWER.
            serie_limpia = {

                fecha: valor

                for fecha, valor

                in serie.items()

                if valor != -999

            }

            # Guardar serie limpia.
            resultados[nombre_variable] = serie_limpia

        # Guardar resultado dentro del caché.
        self.cache[clave] = resultados

        # Retornar datos climáticos completos.
        return resultados