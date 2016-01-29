#! /usr/bin/python

from websocket import create_connection, WebSocketException
import json
from PIL import Image
import base64
import numpy as np
import io, StringIO
import MyUtils
import threading
import time
import os

class OpenFaceClient(object):
    def __init__(self, server_ip=u"ws://128.2.211.75", server_port=9000):
        self.logger=MyUtils.getLogger(__name__)        
        server_ip_port = server_ip + ':' +str(server_port)
        self.ws = create_connection(server_ip_port)

        self.receive_thread = threading.Thread(target=self.onReceive, name='receive_thread')
        self.receive_thread_running = threading.Event()
        self.receive_thread_running.set()
        self.receive_thread.start()

    def addPerson(self,person):
        msg = {
            'type': 'ADD_PERSON',
            'val': person
        }
        msg = json.dumps(msg)
        self.ws.send(msg)

    def setTraining(self,training_on):
        msg = {
            'type': 'TRAINING',
            'val': training_on
        }
        msg = json.dumps(msg)
        self.ws.send(msg)

    def getTSNE(self, people):
        msg = {
            'type': 'REQ_TSNE',
            'people': people
        }
        msg = json.dumps(msg)
        self.ws.send(msg)

    def setState(self,images, people, training_on):
        msg = {
            'type': 'ALL_STATE',
            'images': images,
            'people': people,
            'training': training_on
        }
        msg = json.dumps(msg)
        self.ws.send(msg)

    # current processing frame
    def addFrame(self, data_url, name):
        msg = {
            'type': 'FRAME',
            'dataURL': data_url,
            'name': name
        }
        msg = json.dumps(msg)
        self.ws.send(msg)

    def terminate(self):
        self.receive_thread_running.clear()
        self.ws.close()

    def onReceive(self):
        while (self.receive_thread_running.isSet()):
            try:
                resp = self.ws.recv()
                self.logger.debug('server said: {}'.format(resp))
            except WebSocketException as e:
                self.logger.debug("web socket error: {0}".format(e))
                  
    
if __name__ == '__main__':

    client = OpenFaceClient()

    base_dir = '/home/junjuew/gabriel/gabriel/bin/img/'
    people_dir = ['Hu_Jintao', 'Jeb_Bush']
    test_dir = ['test']
    
    for people in people_dir:
        client.addPerson(people)

    client.setTraining(True)
    for (idx, pdir) in enumerate(people_dir):
        cur_dir = base_dir+pdir
        for (dirpath, dirnames, filenames) in os.walk(cur_dir):
            for filename in filenames:
                print 'adding file: {}'.format(filename)
                image = Image.open(dirpath + '/' +filename)                
                image_output = StringIO.StringIO()
                image.save(image_output, 'JPEG')

                jpeg_image = image_output.getvalue()
                face_string = base64.b64encode(jpeg_image)

                face_string = "data:image/jpeg;base64," + face_string
                client.addFrame(face_string, idx)

    client.setTraining(False)

    for pdir in test_dir:
        cur_dir = base_dir+pdir
        for (dirpath, dirnames, filenames) in os.walk(cur_dir):
            for filename in filenames:
                print 'testing file: {}'.format(filename)
                image = Image.open(dirpath + '/' +filename)
                image_output = StringIO.StringIO()
                image.save(image_output, 'JPEG')

                jpeg_image = image_output.getvalue()
                face_string = base64.b64encode(jpeg_image)

                face_string = "data:image/jpeg;base64," + face_string
                client.addFrame(face_string, 'test')

    
    time.sleep(20)
    print 'waked up'
    client.terminate()
    
    # print "Sent"
    # print "Receiving..."
    # result =  ws.recv()
    # print "Received '%s'" % result
    # ws.close()

    # log.startLogging(sys.stdout)
    # client = OpenFaceClient(server_ip)
