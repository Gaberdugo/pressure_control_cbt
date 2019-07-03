#! /usr/bin/env python
from __future__ import print_function

import rospy

# Brings in the SimpleActionClient
import actionlib

# Brings in the messages used by the fibonacci action, including the
# goal message and the result message.
import pressure_controller_ros.msg
import validate_commands


import time
import sys
import os
import numbers



class configSender:
    def __init__(self):       
        self._client = actionlib.SimpleActionClient('pressure_control', pressure_controller_ros.msg.CommandAction)
        self._client.wait_for_server()

        self.config = rospy.get_param(rospy.get_name())     


    def set_config(self):

        if self.config:

            self.send_command("echo",True)
            self.send_command("load",[])  
            self.send_command("off",[])
            self.send_command("chan",1)
            self.send_command("mode",0)
            self.send_command("valve",-1)
            self.send_command("valve",0)
            
            self.num_channels = self.config.get("channels").get("num_channels")
            
            self.send_command("chan",self.config.get("channels").get("states"))
            self.send_command("maxp", self.config.get("max_pressure") )
            self.send_command("minp", self.config.get("min_pressure") )

            
            self.handle_pid()
            
            self.send_command("time",int(self.config.get("data_loop_time")))
            self.send_command("valve",0)
            self.send_command("mode",1)
            self.send_command("echo",bool(self.config.get("echo")))
            self.send_command("save",[])


    def send_command(self, command, args):
        command, args = validate_commands.go(command, args)
        # Send commands to the commader node and wait for things to be taken care of
        goal = pressure_controller_ros.msg.CommandGoal(command=command, args=args, wait_for_ack = True)
        self._client.send_goal(goal)
        self._client.wait_for_result()

        if not self._client.get_result():
            raise serial_coms.SerialIssue('Something went wrong and a setting was not validated')
        else:
            pass




    def handle_pid(self):
        pid = self.config.get("PID")

        all_equal = pid.get("all_equal")
        if all_equal:
            values = []
            for idx in range(self.num_channels):
                values.append(pid.get("values"))
        else:
            values = pid.get("values")
            
        # Send out the settings for all channels
        for idx in range(self.num_channels):
            vals = [idx]+values[idx]
            self.send_command("pid",vals)



    def shutdown(self):
        self._client.cancel_all_goals()
        




if __name__ == '__main__':
    try:
        rospy.init_node('command_client')
        node = configSender()
        node.set_config()
        node.shutdown()


    except rospy.ROSInterruptException:
        print("program interrupted before completion", file=sys.stderr)