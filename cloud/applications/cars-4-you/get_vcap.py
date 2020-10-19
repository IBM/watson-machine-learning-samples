import os
import json
from cfenv import AppEnv

env = AppEnv()


def get_vcap(local_name, bx_name):
    vcap = None

    if bx_name is not None:
        vcap = env.get_service(label=bx_name)

    if vcap is None:
        try:
            file = open(os.path.join('.', 'vcaps',  local_name + '.vcap'), 'r')
            content = file.read()
            file.close()

            return json.loads(content)
        except:
            raise Exception('Unable to get vcap:', local_name)
    else:
        return vcap.credentials


def get_wml_vcap():
    return get_vcap('wml', 'pm-20')


def get_cos_vcap():
    return get_vcap('cos', None)