#!/usr/bin/env python

import roslib; roslib.load_manifest('ap_msgs')
from time import sleep
import sys
import actionlib
import rospy
from ap_msgs.srv import PauseResumePatroller
from scitos_msgs.msg import ChargerStatus
import scitos_apps_msgs.msg

class Initialiser():
    _charger_received=False
    _at_charger=True

    def __init__(self, name):
        rospy.init_node('initialiser', anonymous=True)
        resp=self.pause_client()
        print resp
        self.listener()
        timeout=0
        while (not self._charger_received) and timeout < 100:
            sleep(0.1)
            timeout=timeout+1
        print self._at_charger
        if self._at_charger :
            self.client = actionlib.SimpleActionClient('/chargingServer', scitos_apps_msgs.msg.ChargingAction)
            print "wait for Server"
            self.client.wait_for_server()
            charging_goal = scitos_apps_msgs.msg.ChargingGoal()
            charging_goal.Command = 'undock'
            charging_goal.Timeout = 1000
            print "sending goal"
            print charging_goal
            self.client.send_goal(charging_goal)
            self.client.wait_for_result()
        resp=self.pause_client()
        print resp


    def charger_callback(self, data):
        #rospy.loginfo(rospy.get_name() + ": I heard %s" % data.charging)
        self._at_charger=data.charging
        self._charger_received=True

    def listener(self):
        rospy.Subscriber("/charger_status", ChargerStatus, self.charger_callback)

    def pause_client(self):
        rospy.wait_for_service('/pause_resume_patroller')
        try:
            pause = rospy.ServiceProxy('/pause_resume_patroller', PauseResumePatroller)
            resp1 = pause()
            return resp1.result
        except rospy.ServiceException, e:
            print "Service call failed: %s"%e



if __name__ == "__main__":
    ps = Initialiser(rospy.get_name())
    #rospy.spin()
