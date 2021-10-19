import logging
import json
import getpass
import sys
import time
import uuid

#  https://github.com/ascentio-tech/thingsboard-swagger-client

# Importing models and REST client class from Community Edition version
from tb_rest_client32.rest_client_ce import RestClientCE, Device, Customer, Asset
# Importing the API exception
from tb_rest_client32.rest import ApiException


class RTS_Things():

    def __init__(self, url, username, password=None):
        self.client = RestClientCE(base_url=url)
        if password == None:
            password = getpass.getpass(prompt='Password: ', stream=None)
        try:
            self.client.login(username=username, password=password)
            if self.client.configuration.api_key['X-Authorization'] is None:
                self.is_logged = False
            else:
                self.is_logged = True
        except ApiException as e:
            self.is_logged = False
            logging.exception(e)

    def __del__(self):
        if self.is_logged:
            self.client.logout()

    def get_customers_id_by_name(self, name=""):
        tmp = self.client.get_customers(text_search=name)
        return tmp  # .data[0].id

    def get_token_by_dev_name(self, name=""):
        tmp = self.client.get_tenant_devices(text_search=name)
        tmp = self.client.get_device_by_id(tmp.data[0].id)
        tmp = self.client.get_device_credentials_by_device_id(tmp.id)
        return tmp.credentials_id

    def put_device(self, dev_name, customer):
        cstmr_id = self.get_customers_id_by_name(customer)['data'][0]['id']
        device = Device(name=dev_name, type="vts_type", customer_id=cstmr_id)
        self.client.save_device(device)
        return self.get_token_by_dev_name(dev_name)

    def get_device_id_by_name(self, name):
        """ get device id by name """
        ret = None
        tmp = self.client.get_tenant_devices(text_search=name)
        if tmp.total_elements == 1:
            ret = tmp.data[0].id
        return ret

# ThingsBoard REST API URL

if __name__ == "__main__":

    url = "http://rts-iot.tw1.ru:9090"
    # url = "http://iot.rs24.tw1.su:9090"
    # url = "http://192.168.1.2:9090"
    # Default Tenant Administrator credentials
    username = "tenant@thingsboard.org"
    password = "zyt_pf,elegfhjkm"
    # password = "tenant"

    # sys.exit(0)

    ThngBrd = RTS_Things(url, username, password=password)
    print(ThngBrd.is_logged)
    # aa = ThngBrd.client.get_tenant_devices()
    # thng_token = ThngBrd.put_device('06.2106.0001', "АГК")

    aa = ThngBrd.get_device_id_by_name('06.2106.0001.00')
    print(aa)

    pass

