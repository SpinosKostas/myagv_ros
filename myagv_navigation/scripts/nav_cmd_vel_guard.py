#!/usr/bin/env python
# Forwards /nav_cmd_vel (move_base) to /cmd_vel. If move_base goes silent while
# the robot is moving, publish ONE zero command. Ctrl+C also sends a stop.
import time
import rospy
from geometry_msgs.msg import Twist


class Guard(object):
    def __init__(self):
        self.timeout = rospy.get_param("~timeout", 0.5)
        self.pub = rospy.Publisher("/cmd_vel", Twist, queue_size=1)
        rospy.Subscriber("/nav_cmd_vel", Twist, self.on_cmd, queue_size=1)
        self.last_rx = rospy.Time.now()
        self.moving = False
        rospy.Timer(rospy.Duration(0.1), self.on_timer)
        rospy.on_shutdown(self.on_shutdown)

    def on_cmd(self, msg):
        self.last_rx = rospy.Time.now()
        self.moving = (abs(msg.linear.x) > 1e-3 or abs(msg.linear.y) > 1e-3
                       or abs(msg.angular.z) > 1e-3)
        self.pub.publish(msg)

    def on_timer(self, _event):
        silent = (rospy.Time.now() - self.last_rx).to_sec()
        if self.moving and silent > self.timeout:
            rospy.logwarn("move_base silent for %.1f s -> stopping", silent)
            self.pub.publish(Twist())
            self.moving = False

    def on_shutdown(self):
        self.pub.publish(Twist())
        time.sleep(0.2)


if __name__ == "__main__":
    rospy.init_node("nav_cmd_vel_guard")
    Guard()
    rospy.spin()
