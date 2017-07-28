import xml.etree.cElementTree as ET
import psutil
import os
import threading
import time
import requests
import datetime

"""
Intervals in seconds
"""
CPU_INTERVAL = 0.5
MEM_INTERVAL = 20
NET_INTERVAL = 1
PRO_INTERVAL = 30
USER_INTERVAL = 60

"""
HTTP globals
"""
URL = 'http://127.0.0.1:5000/log'

"""
String conversion utils
"""
def float_str(value):
    return repr(value)

"""
Threading utils
"""
def busy_wait(**kwargs):
    while(1):
        kwargs['routine']()
        time.sleep(kwargs['interval'])

def thread_it(**kwargs):
    t = threading.Thread(target=busy_wait, kwargs=kwargs)
    t.start()
    # t.join()

"""
Initialize the XML trees and subtrees
"""
ROOT = ET.Element("log")
CPU = ET.SubElement(ROOT, "cpu")
MEM = ET.SubElement(ROOT, "memory")

NET = ET.SubElement(ROOT, "network")
NET_S = ET.SubElement(NET, "sent")
NET_R = ET.SubElement(NET, "received")

PRO = ET.SubElement(ROOT, "processes")
USER = ET.SubElement(ROOT, "user")

"""
Auxiliar XML formating functions
"""
def xml_generate_wrap(name):
    return ET.Element(name)

def xml_insert_partial(tree, value):
    partial = xml_generate_wrap('partial')

    time = xml_generate_wrap('time')
    payload = xml_generate_wrap('payload')

    time.text = str(datetime.datetime.utcnow())
    payload.text = value

    partial.append(time)
    partial.append(payload)

    tree.append(partial)
    # ET.dump(tree)

def xml_remove_nodes(tree, name):
    for child in tree:
        tree.remove(child)

def reset_tree(tree, partial_node_name):
    xml_remove_nodes(tree, partial_node_name)

"""
HTTP helpers
"""
def post_request(namespace, tree, partial_node_name):
    try:
        headers = {'Content-Type': 'application/xml'}
        params = {'namespace': namespace}
        xmlstr = ET.tostring(tree, encoding='utf8', method='xml')
        reset_tree(tree, partial_node_name)
        r = requests.post(URL, params=params, data=xmlstr, headers=headers)
        code = r.status_code
        json = r.json()

        print "message: %s - status: %d" % (json['message'], code)
    except Exception as e:
        print 'Unable to complete request'

"""
These functions will obtain the required data
"""
def set_cpu():
    cpu_value = psutil.cpu_percent(CPU_INTERVAL)
    xml_insert_partial(CPU, float_str(cpu_value / 100))
    post_request('cpu', CPU, "partials")

def set_mem():
    mem = psutil.virtual_memory()
    xml_insert_partial(MEM, float_str(float(mem.used) / float(mem.total)))
    post_request('memory', MEM, "partials")

def set_net():
    net = psutil.net_io_counters(pernic=True)
    ethernet = net['Ethernet']

    sent = ethernet.bytes_sent
    received = ethernet.bytes_recv

    xml_insert_partial(NET_S, str(sent))
    xml_insert_partial(NET_R, str(received))

    post_request('sent', NET_S, "partials")
    post_request('received', NET_R, "partials")

def set_pro():
    try:
        pro_pids = psutil.pids()
        for value in pro_pids:
            pro = psutil.Process(value)
            xml_insert_partial(PRO, pro.name())
            pass

        post_request('processes', PRO, "partials")
    except Exception as e:
        print "Some processes ended before iteration"

def set_user():
    xml_insert_partial(USER, os.environ['USERNAME'])
    post_request('users', USER, "partials")

if __name__ == '__main__':
    thread_it(routine = set_cpu, interval = CPU_INTERVAL)
    thread_it(routine = set_mem, interval = MEM_INTERVAL)
    thread_it(routine = set_net, interval = NET_INTERVAL)
    thread_it(routine = set_pro, interval = PRO_INTERVAL)
    thread_it(routine = set_user, interval = USER_INTERVAL)
