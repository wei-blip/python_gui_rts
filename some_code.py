    # tmp = ThngBrd.client.get_asset_types("BearingAssetType")
    # print(tmp)

    # asset = Asset(name="Building 1234", type="building")
    # tmp = ThngBrd.client.get_customers(text_search="Customer A")
    # print(tmp)

    # tmp = ThngBrd.put_device("123", "Customer A")
    # print(tmp)

    # tmp = ThngBrd.get_token_by_dev_name(name="VTS_00004")

    # page = 0
    # page_size = 100
    # tmp = ThngBrd.client.get_tenant_devices(text_search="VTS", page_size=page_size, page=page).data
    # print(type(tmp))
    # for i in tmp:
    #     print(i)
    # print("stop")
    # dev = tmp[0]
    # print(type(dev))
    # print(type(tmp[0]))
    # print(dev)
    # dev.id.id = str(uuid.uuid4())
    # dev.name = "VTS-00005"
    # dev.label = "VTS on MCU STM32L4 series"
    # dev.tenant_id.id = "55c38a80-3221-11eb-848f-a17a24dde584" #dev.id.id[:-2] + "00"
    # # uid = uuid.uuid4()
    # # print(dev)
    # ThngBrd.client.save_device(dev)
    # cred = ThngBrd.client.get_device_credentials_by_device_id(dev.id)
    # print(cred)
    # cred.credentials_id = cred.credentials_id[:-2] + '00'
    # print(type(cred.credentials_id))
    # ThngBrd.client.save_device_credentials(cred)
    # tmp = None
    # a = time.time()
    # while tmp is None or tmp.has_next:
    #     tmp = ThngBrd.client.get_tenant_devices(text_search="VTS", page_size=page_size, page=page)
    #     page = page + 1
    #     for i in tmp.data:
    #         print(i.name, ThngBrd.client.get_device_credentials_by_device_id(i.id), tmp.has_next)
    #     # print(tmp, f"\n page =  {page}")
    # print((time.time() - a))
    # ThngBrd.client.set_user_credentials_enabled()
    # for i in range(1, 5):
    #     asset = Asset(name=f"ЭЦПНС НАШ №{i}", type="PumpAssetType")
    #     asset.
    #     ThngBrd.client.save_asset(asset)
    # for i in range(0,len(tmp.data)):
    #     print(tmp.data[i].id, "\n\n")
    # aa = ThngBrd.client.get_assets_by_ids("045975a0-41e5-11eb-9829-fb1d442bdddd")
    # print(aa)
    customer_ids = ThngBrd.client.get_customers()['data']
    print(type(customer_ids))
    for i in customer_ids:
        if i['name'] == "АГК":
            print(i, "\n", i['name'], "\n")
            customer = Customer(id=i['id'], name=i['name'])
            customer_id = customer.id
            print(type(i))
    print(customer_id)

    bb = ThngBrd.client.get_customer_assets(customer)
    print(bb)
    # ThngBrd.client.get_relation(from_id=)
    # ThngBrd.client.save_relation('{"from":{"id":"6b18fd20-6c2d-11eb-9829-fb1d442bdddd","entityType":"ASSET"},"type":"Contains","to":{"entityType":"DEVICE","id":"b4d04f40-3fa0-11eb-9829-fb1d442bdddd"}}')

    # aa = print(aa)
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