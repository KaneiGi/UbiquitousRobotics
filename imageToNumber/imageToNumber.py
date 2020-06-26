#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

"""
 @file imageToNumner.py
 @brief ModuleDescription
 @date $Date$


"""
import sys
import time

sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist
from PIL import Image
import tensorflow as tf
import cv2
import os
import threading

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

enumber = 0
timedFrame = 100
count = 1
predint = []

imagetonumner_spec = ["implementation_id", "imageToNumner",
                      "type_name", "imageToNumner",
                      "description", "ModuleDescription",
                      "version", "1.0.0",
                      "vendor", "KaneiGi",
                      "category", "Category",
                      "activity_type", "STATIC",
                      "max_instance", "1",
                      "language", "Python",
                      "lang_type", "SCRIPT",
                      ""]


class imageToNumner(OpenRTM_aist.DataFlowComponentBase):

    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        self._d_out = OpenRTM_aist.instantiateDataType(RTC.TimedShort)
        """
        """
        self._outOut = OpenRTM_aist.OutPort("out", self._d_out)

    def onInitialize(self):
        self.addOutPort("out", self._outOut)

        return RTC.RTC_OK

    def onActivated(self, ec_id):
        self._d_out.data = 1
        OpenRTM_aist.setTimestamp(self._d_out)
        self._outOut.write()
        return RTC.RTC_OK

    def onDeactivated(self, ec_id):
        # cv2.destroyAllWindows()
        cap.release()
        cv2.destroyAllWindows()
        self._d_out.data = 1
        OpenRTM_aist.setTimestamp(self._d_out)
        self._outOut.write()
        return RTC.RTC_OK

    def onExecute(self, ec_id):
        imagePush(self)
        return RTC.RTC_OK


def imagePrepare(image):
    res = cv2.resize(image, (28, 28), interpolation=cv2.INTER_CUBIC)
    res = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    ret, res = cv2.threshold(res, 80, 255, cv2.THRESH_BINARY)
    filename = 'TEMP/' + str(enumber) + ".png"
    cv2.imwrite(filename, res)
    im = Image.open(filename).convert('L')
    tv = list(im.getdata())
    tva = [(255 - x) * 1.0 / 255.0 for x in tv]
    return tva


def imageGet(ret, frame):
    global count
    while ret:

        # cv2.imshow('capture', frame)
        capture = frame[150:350, 200:400]
        # cv2.imshow('capture1', capture)
        if count % timedFrame == 0:
            return capture
        count = count + 1
        if count >= 10e9:
            count = 1


def imagePush(self):
    global enumber

    x = tf.placeholder(tf.float32, [None, 784])
    # y = tf.placeholder(tf.float32, [None, 10])
    W1 = tf.Variable(tf.random_normal([784, 300], stddev=0.03), name='W1')
    b1 = tf.Variable(tf.random_normal([300]), name='b1')
    W2 = tf.Variable(tf.random_normal([300, 10], stddev=0.03), name='W2')
    b2 = tf.Variable(tf.random_normal([10]), name='b2')
    hidden_out = tf.add(tf.matmul(x, W1), b1)
    hidden_out = tf.nn.relu(hidden_out)

    y_ = tf.nn.softmax(tf.add(tf.matmul(hidden_out, W2), b2))

    init_op = tf.global_variables_initializer()

    if cap.isOpened() is False:
        print('error opening video stream or file')
    while cap.isOpened():
        ret, frame = cap.read()
        cv2.rectangle(frame, (int(200), int(150)), (int(400), int(350)), (255, 255, 255), 4)
        cv2.imshow('capture', frame)
        image = imageGet(ret, frame)
        enumber = enumber + 1

        result = imagePrepare(image)
        saver = tf.train.Saver()
        with tf.Session() as sess:
            sess.run(init_op)
            saver.restore(sess, 'MNIST/test.ckpt')

            prediction = tf.argmax(y_, 1)
            predint = prediction.eval(feed_dict={x: [result]}, session=sess)
            self._d_out.data = int(predint[0])
            OpenRTM_aist.setTimestamp(self._d_out)
            print(self._d_out)
            self._outOut.write()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


def imageToNumnerInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=imagetonumner_spec)
    manager.registerFactory(profile,
                            imageToNumner,
                            OpenRTM_aist.Delete)


def MyModuleInit(manager):
    imageToNumnerInit(manager)

    # Create a component
    comp = manager.createComponent("imageToNumner")


def main():
    mgr = OpenRTM_aist.Manager.init(sys.argv)
    mgr.setModuleInitProc(MyModuleInit)
    mgr.activateManager()
    mgr.runManager()


if __name__ == "__main__":
    while True:
        i=input('please input your camera number,starting from 0:\n')
        cap=cv2.VideoCapture(int(i))
        if not cap.isOpened():
            print('camera not existing,try another number')
        else:
            print('camera choosed')
            break
    main()
