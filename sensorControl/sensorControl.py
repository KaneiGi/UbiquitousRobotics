#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

"""
 @file sensorControl.py
 @brief ModuleDescription
 @date $Date$


"""
import sys
import time

sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist

# Import Service implementation class
# <rtc-template block="service_impl">

# </rtc-template>

# Import Service stub modules
# <rtc-template block="consumer_import">
# </rtc-template>


# This module's spesification
# <rtc-template block="module_spec">
sensorcontrol_spec = ["implementation_id", "sensorControl",
                      "type_name", "sensorControl",
                      "description", "ModuleDescription",
                      "version", "1.0.0",
                      "vendor", "KaneiGi",
                      "category", "Category",
                      "activity_type", "STATIC",
                      "max_instance", "1",
                      "language", "Python",
                      "lang_type", "SCRIPT",
                      "conf.default.stop_distance", "300",

                      "conf.__widget__.stop_distance", "text",

                      "conf.__type__.stop_distance", "short",

                      ""]


# </rtc-template>

##
# @class sensorControl
# @brief ModuleDescription
#
#
class sensorControl(OpenRTM_aist.DataFlowComponentBase):

    ##
    # @brief constructor
    # @param manager Maneger Object
    #
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        self._d_distance_sensor = OpenRTM_aist.instantiateDataType(RTC.TimedShortSeq)
        """
        """
        self._distance_sensorIn = OpenRTM_aist.InPort("distance_sensor", self._d_distance_sensor)
        self._d_senor_control = OpenRTM_aist.instantiateDataType(RTC.TimedShort)
        """
        """
        self._senor_controlOut = OpenRTM_aist.OutPort("senor_control", self._d_senor_control)

        # initialize of configuration-data.
        # <rtc-template block="init_conf_param">
        """
        
         - Name:  stop_distance
         - DefaultValue: 300
        """
        self._stop_distance = [300]

    def onInitialize(self):
        # Bind variables and configuration variable
        self.bindParameter("stop_distance", self._stop_distance, "300")

        # Set InPort buffers
        self.addInPort("distance_sensor", self._distance_sensorIn)

        # Set OutPort buffers
        self.addOutPort("senor_control", self._senor_controlOut)

        # Set service provider to Ports

        # Set service consumers to Ports

        # Set CORBA Service Ports
        self._last_sensor_data = [0, 0, 0, 0]

        return RTC.RTC_OK

    def onActivated(self, ec_id):
        return RTC.RTC_OK

    def onDeactivated(self, ec_id):
        self._d_senor_control.data = 1
        OpenRTM_aist.setTimestamp(self._d_senor_control)
        self._senor_controlOut.write()

        return RTC.RTC_OK

    def onExecute(self, ec_id):
        if self._distance_sensorIn.isNew():
            data = self._distance_sensorIn.read()
            if len(data.data) == 4:
                self._last_sensor_data = data.data[:]
        for d in self._last_sensor_data:
            if d > self._stop_distance[0]:
                self._d_senor_control.data = 0
                OpenRTM_aist.setTimestamp(self._d_senor_control)
                self._senor_controlOut.write()
                return RTC.RTC_OK
        self._d_senor_control.data = 1
        OpenRTM_aist.setTimestamp(self._d_senor_control)
        self._senor_controlOut.write()
        # print(self._d_senor_control)
        return RTC.RTC_OK


def sensorControlInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=sensorcontrol_spec)
    manager.registerFactory(profile,
                            sensorControl,
                            OpenRTM_aist.Delete)


def MyModuleInit(manager):
    sensorControlInit(manager)

    # Create a component
    comp = manager.createComponent("sensorControl")


def main():
    mgr = OpenRTM_aist.Manager.init(sys.argv)
    mgr.setModuleInitProc(MyModuleInit)
    mgr.activateManager()
    mgr.runManager()


if __name__ == "__main__":
    main()
