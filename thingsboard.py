#!/usr/bin/env python3
# -*- coding: utf-8 -*-

## @file thingsboard.py
# @brief Contiene clases para interactuar con servidor Thingsboard.
# @see config/config.py

# import paho.mqtt.client as mqtt
import json, requests, threading, time
import numpy as np

## @class ThingsBoardHTTP
class ThingsBoardHTTP:
    ## @brief Constructor de la clase.
    # @param[in] token Token de acceso del dispositivo.
    # @param[in] host Host con plataforma thingsboard.
    # @param[in] port Puerto de acceso MQTT.
    # @param[in] timeout Tiempo de espera máximo para las peticiones.
    def __init__(self, host, port = 8080, timeout = 5):
        ## Token asociado al dispositivo.
        # self.token 		= token		
        ## Host con plataforma thingsboard.
        self.host 		= host		
        ## Puerto de acceso a plataforma en el host.
        self.port 		= port		
        ## Timeout para peticion http.
        self.timeout 	= timeout	
        self.userToken 	= ""

    # ## @brief Publica telemetría.
    # # @param[in] data Paquete de telemetría a publicar.
    # # @param[out] res Bandera que indica si la publicación fue exitosa.
    # def publishTelemetry(self, data):
    # 	headers = {'content-type': 'application/json'}
    # 	try:
    # 		#Publica telemetria
    # 		r = requests.post(
    # 			url 	= "http://%s:%d/api/v1/%s/telemetry"%(self.host, self.port, self.token), 
    # 			data 	= json.dumps(data), 
    # 			headers	= headers,
    # 			timeout = self.timeout
    # 		)
    # 		return r.status_code == 200
    # 	except:
    # 		import traceback
    # 		traceback.print_exc()
    # 		return False

    # ## @brief Publica los atributos del dispositivo.
    # # @param[in] data Atributos del dispositivo.
    # # @param[out] res Bandera que indica si la publicación fue exitosa.
    # def publishAttributes(self, data):
    # 	headers = {'content-type': 'application/json'}
    # 	try:
    # 		#Publica atributos del dispositivo
    # 		r = requests.post(
    # 			url 	= "http://%s:%d/api/v1/%s/attributes"%(self.host, self.port, self.token), 
    # 			data 	= json.dumps(data), 
    # 			headers = headers,
    # 			timeout = self.timeout
    # 		)
    # 		return r.status_code == 200
    # 	except:
    # 		return False

    ## @brief Autentica al usuario en thingsboard.
    # @param[in] username Usuario.
    # @param[in] password Contraseña.
    # @param[out] res Bandera que indica si la publicación fue exitosa.
    def login(self, username, password):
        headers = {'Content-Type': 'application/json','Accept': 'application/json'}
        data 	= {"username": username, "password": password}
        url 	= 'http://%s:%d/api/auth/login'%(self.host, self.port)
        try:
            r = requests.post(url = url, data = json.dumps(data), headers = headers, timeout = self.timeout)
            resp = r.json()
            self.userToken = "Bearer %s"%resp["token"]
            return r.status_code == 200
        except:
            return False

    def customerDeviceList(self, customerId, page, pageSize):
        headers = {'Accept': 'application/json','X-Authorization': self.userToken}
        url 	= 'http://%s:%d/api/customer/%s/devices?pageSize=%d&page=%d'%(
            self.host, self.port, customerId, pageSize, page
        )
        print(url)
        try:
            r = requests.get(url = url, headers = headers, timeout = self.timeout)
            resp = r.json()
            return resp
        except:
            pass
    
    def customerList(self, page, pageSize):
        headers = {'Accept': 'application/json','X-Authorization': self.userToken}
        url 	= 'http://%s:%d/api/customers?pageSize=%d&page=%d'%(
            self.host, self.port, pageSize, page
        )
        print(url)
        try:
            r = requests.get(url = url, headers = headers, timeout = self.timeout)
            resp = r.json()
            return resp
        except:
            pass

    ## @brief Autentica al usuario en thingsboard.
    # keys - comma separated list of telemetry keys to fetch.
    # startTs - unix timestamp that identifies start of the interval in milliseconds.
    # endTs - unix timestamp that identifies end of the interval in milliseconds.
    # interval - the aggregation interval, in milliseconds.
    # agg - the aggregation function. One of MIN, MAX, AVG, SUM, COUNT, NONE.
    # pageSize - the max amount of data points to return or intervals to process.
    def getTimeSeries(self, deviceID, keys, startTs, endTs, interval = 1000, pageSize = 10000, agg = None):
        headers = {'Content-Type': 'application/json','X-Authorization': self.userToken}
        keyss = ','.join(keys)
        url = "http://%s:%d/api/plugins/telemetry/DEVICE/%s/values/timeseries?keys=%s&startTs=%d&endTs=%d&interval=%d&pageSize=%d"%(
            self.host, self.port, deviceID, keyss, startTs, endTs, interval, pageSize
        )
        # url = "http://%s:%d/api/plugins/telemetry/DEVICE/%s/values/timeseries?keys=%s&startTs=%d&endTs=%d&pageSize=%d"%(
        # 	self.host, self.port, deviceID, keyss, startTs, endTs, pageSize
        # )
        print(url)
        if not agg is None:
            url = url + "&agg=%s"%agg

        try:
            r = requests.get(url = url, headers = headers, timeout = self.timeout)
            # print(r.text)
            if r.status_code == 200:
                return r.json()
            
        except:
            pass
        return None
        
        # curl -v -X GET "http://localhost:8080/api/plugins/telemetry'
        # '/DEVICE/ac8e6020-ae99-11e6-b9bd-2b15845ada4e/values
        # '/timeseries?keys=gas,temperature'
        # '&startTs=1479735870785&endTs=1479735871858&interval=60000&pageSize=100&agg=AVG" \
        # --header "Content-Type:application/json" \
        # --header "X-Authorization: $JWT_TOKEN"
def thingsboardJSON2CSV(data):
    # data = json.loads(data)
    # print(data)
    keys = list(data.keys())
    length = len(data[keys[0]])
    last_key_data_idx = [0]*len(keys)
    output = ['ts,'+','.join(keys.copy())+"\n"]
    for data_idx in range(length):
        ts = data[keys[0]][data_idx]["ts"]
        values = [ts, data[keys[0]][data_idx]["value"]]
        value = ''
        for key_idx in range(1, len(keys)):
            for data2_idx in range(last_key_data_idx[key_idx], len(data[keys[key_idx]])):
                ts2 = data[keys[key_idx]][data2_idx]["ts"]
                if ts == ts2:
                    last_key_data_idx[key_idx] = data2_idx
                    value = data[keys[key_idx]][data2_idx]["value"]
                    break
            values.append(value)
        values[0] = str(values[0])
        output.append(','.join(values)+"\n")
    return output