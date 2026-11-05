#!/usr/bin/env python
import rospy
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from tf.transformations import quaternion_from_euler

# (x [m], y [m], yaw [rad]) in the MAP frame - replace with your own points
WAYPOINTS = [
    (1.0, 0.0, 0.0),
    (1.0, 1.0, 1.57),
    (0.0, 0.0, 3.14),
]


def make_goal(x, y, yaw):
    goal = MoveBaseGoal()
    goal.target_pose.header.frame_id = "map"
    goal.target_pose.header.stamp = rospy.Time.now()
    goal.target_pose.pose.position.x = x
    goal.target_pose.pose.position.y = y
    qx, qy, qz, qw = quaternion_from_euler(0, 0, yaw)
    goal.target_pose.pose.orientation.x = qx
    goal.target_pose.pose.orientation.y = qy
    goal.target_pose.pose.orientation.z = qz
    goal.target_pose.pose.orientation.w = qw
    return goal


if __name__ == "__main__":
    rospy.init_node("patrol")
    client = actionlib.SimpleActionClient("move_base", MoveBaseAction)
    rospy.on_shutdown(client.cancel_all_goals)
    client.wait_for_server()
    while not rospy.is_shutdown():
        for x, y, yaw in WAYPOINTS:
            rospy.loginfo("going to (%.2f, %.2f)", x, y)
            client.send_goal(make_goal(x, y, yaw))
            if not client.wait_for_result(rospy.Duration(90)):
                rospy.logwarn("timeout, cancelling goal")
                client.cancel_goal()
            else:
                rospy.loginfo("result state %d (3 = reached)", client.get_state())
