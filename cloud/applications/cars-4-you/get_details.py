import os
import json
from cfenv import AppEnv

env = AppEnv()


def get_details(local_name, bx_name):
    service = None

    if bx_name is not None:
        service = env.get_service(label=bx_name)

    if service is None:
        try:
            file = open(os.path.join('.', 'settings', local_name + '.json'), 'r')
            content = file.read()
            file.close()

            return json.loads(content)
        except:
            raise Exception('Unable to get json:', local_name)
    else:
        return service.credentials


def get_wml_details():
    return get_details('wml', 'pm-20')


def get_cos_details():
    return get_details('cos', None)