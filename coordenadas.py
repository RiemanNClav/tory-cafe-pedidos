import requests
from geopy.geocoders import Nominatim
import time
from datetime import datetime
import pandas as pd
import os
import math
import json


 
class ApiAddress():
    def __init__(self):
        self.app = Nominatim(user_agent="tutorial")
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.path_colonias = os.path.join(self.base_dir, 'notebook', 'data', 'colonias_final.csv')
        self.path_alcaldias = os.path.join(self.base_dir, 'notebook', 'data', 'alcaldias_final.csv')


    def get_location_by_address(self, address):
        """This function returns a location as raw from an address
        will repeat until success"""
        time.sleep(1)
        try:
            return self.app.geocode(address).raw
        except:
            return 'NO SE ENCONTRO'


    def get_address_by_location(self, latitude, longitude, language="es"):
        """This function returns an address as raw from a location
        will repeat until success"""
        # build coordinates string to pass to reverse() function
        coordinates = f"{latitude}, {longitude}"
        # sleep for a second to respect Usage Policy
        time.sleep(1)
        try:
            return self.app.reverse(coordinates, language=language).raw
        except:
            return 'NO SE ENCONTRO'
        
        
    def get_day_month(self):
        meses = {1: 'ENERO', 2: 'FEBRERO', 3: 'MARZO', 4:'ABRIL',
                5: 'MAYO', 6: 'JUNIO', 7: 'JULIO', 8: 'AGOSTO',
                9: 'SEPTIEMBRE', 10: 'OCTUBRE', 11: 'NOVIEMBRE',
                12: 'DICIEMBRE'}
        
        dia, mes = datetime.now().day, datetime.now().month
        return dia, meses[mes]
    
    
    def api_request_object_1(self, latitud, longitud):
        address = self.get_address_by_location(latitud, longitud)
        direccion = address['address']
        direccion_str = json.dumps(direccion)
        return direccion_str
        alcaldia = address['address']['borough'].upper()
        #alcaldia_inal = self.categoria_mas_parecida(alcaldia, alcaldias)
        colonia = address['address']['neighbourhood'].upper()
        #colonia_final = self.categoria_mas_parecida(colonia, colonias)
        dia, mes = self.get_day_month()


        return alcaldia, colonia, dia, mes
    

    def api_request_object_2(self, complete_address):

        address = self.get_location_by_address(complete_address)

        print(address)

        latitud = address["lat"]
        longitud = address['lon']
        dia, mes = self.get_day_month()

        return latitud, longitud, dia, mes

    def haversine(self, lat2, lon2, lat1=19.4891421, lon1=-99.153497):
        R = 6371.0
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        distance = R * c
        return distance
        
    def bola_cerrada(self, latitud, longitud, radio=100):

        # latitud, longitud, dia, mes = self.api_request_object_2(direccion)
        distancia = self.haversine(float(latitud), float(longitud))

        if distancia <= radio:
            result = 1
        else:
            result = 0

        return result, radio, distancia



if __name__=="__main__":
    import json

    api = ApiAddress()

    alcaldia = api.api_request_object_1(19.498145, -99.182421)

    print(alcaldia)
