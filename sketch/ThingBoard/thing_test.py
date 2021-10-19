import logging
import json
import getpass 
import sys

#  https://github.com/ascentio-tech/thingsboard-swagger-client

# Importing models and REST client class from Community Edition version
from tb_rest_client.rest_client_ce import RestClientCE, Device
# Importing the API exception
from tb_rest_client.rest import ApiException


class RTS_Things():

    def __init__(self, url, username, password=None):
        self.__client = RestClientCE(base_url=url)
        if password == None:
            password = getpass.getpass(prompt='Password: ', stream=None)
        try:
            self.__client.login(username=username, password=password)
            if self.__client.configuration.api_key['X-Authorization'] == None:
                self.is_logged = False
            else:
                self.is_logged = True
        except ApiException as e:
            self.is_logged = False
            logging.exception(e)

    def __del__(self):        
        if self.is_logged:
            self.__client.logout()

    def get_customers_id_by_name(self, name=""):
        tmp = self.__client.get_customers(text_search=name)         
        return tmp

    def get_token_by_dev_name(self, name=""):
        tmp = self.__client.get_tenant_devices(text_search=name)
        tmp = self.__client.get_device_by_id(tmp.data[0].id)
        tmp = self.__client.get_device_credentials_by_device_id(tmp.id.id)
        return tmp.credentials_id

# ThingsBoard REST API URL

if __name__ == "__main__":

    url = "http://iot.rs24.tw1.su:9090"
    # Default Tenant Administrator credentials
    username = "tenant@thingsboard.org"
    password = "tenant"

    sys.exit(0)

    ThngBrd = RTS_Things(url, username, password=password)
    # print(ThngBrd.is_logged)

    tmp = ThngBrd.get_customers_id_by_name(name="")
    tmp = ThngBrd.get_token_by_dev_name(name="DevFromPython")
    print(tmp)
    # for i in range(0,len(tmp.data)):
    #     print(tmp.data[i].id, "\n\n")
    







# with RestClientCE(base_url=url) as rest_client:
# try:
    # Auth with credentials
   
    # Creating an Asset
    # asset = Asset(name="Building 1", type="building")
    # asset = rest_client.save_asset(asset)

    # logging.info("Asset was created:\n%r\n", asset)

    # creating a Device
    # aa = rest_client.get_customers(text_search="Customer A")
    # if ~aa.has_next and len(aa.data) == 1:
    #     b = aa.data[0].id
    # b = aa.to_dict().get("data")[0].get("id").get("id")
    # print(b)
    # print(type(b))
    # Customer
    # customer_id = json.dumps("'id': {'entity_type': 'CUSTOMER', 'id': 'dbca3ab0-33cc-11ea-a3d9-77cfe767bda4'},'")
    # print(customer_id)
    
    # device = Device(name="DevFromPython", type="default", customer_id=b)
    # # device = rest_client.save_device(device)
    # device = rest_client.get_device_by_id("cf9f96f0-53b5-11ea-a0e9-71251473da97")
    

    # accessTocken = rest_client.get_device_credentials_by_device_id("cf9f96f0-53b5-11ea-a0e9-71251473da97")
    # print(type(device.id))
    # print(device)
    # print("DevFromPython token: ", accessTocken.credentials_id)
        
        # rest_client.assign_device_to_customer(customer_id=b, device_id=device.id)
        

        # logging.info(" Device was created:\n%r\n", device)



        # Creating relations from device to asset
        # relation = EntityRelation(_from=asset.id, to=device.id, type="Contains")
        # relation = rest_client.save_relation(relation)

        # logging.info(" Relation was created:\n%r\n", relation)
# except ApiException as e:
#     logging.exception(e)


# if 'password' not in locals() or password == None:
#     password = getpass.getpass(prompt='Password: ', stream=None) 

# rest_client = RestClientCE(base_url=url)


# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s',
#                     datefmt='%Y-%m-%d %H:%M:%S')
