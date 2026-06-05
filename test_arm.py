import rclpy
from builtin_interfaces.msg import Duration
from control_msgs.action import FollowJointTrajectory
from rclpy.action import ActionClient
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectoryPoint


class ArmTester(Node):
    def __init__(self):
        super().__init__('arm_tester')
        self._action_client = ActionClient(
            self,
            FollowJointTrajectory,
            '/rc/arm_0_joint_trajectory_controller/follow_joint_trajectory',
        )

    def send_goal(self):
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory.joint_names = [
            'arm_0_shoulder_pan_joint',
            'arm_0_shoulder_lift_joint',
            'arm_0_elbow_joint',
            'arm_0_wrist_1_joint',
            'arm_0_wrist_2_joint',
            'arm_0_wrist_3_joint',
        ]

        # Point 1: slightly bent posture
        point1 = JointTrajectoryPoint()
        point1.positions = [0.1, -1.0, 1.0, -0.5, 0.5, 0.1]
        point1.time_from_start = Duration(sec=3, nanosec=0)

        # Point 2: back to zero
        point2 = JointTrajectoryPoint()
        point2.positions = [0.0, -1.57, 1.57, 0.0, 0.0, 0.0]
        point2.time_from_start = Duration(sec=6, nanosec=0)

        goal_msg.trajectory.points = [point1, point2]

        self.get_logger().info('Waiting for action server...')
        self._action_client.wait_for_server()

        self.get_logger().info('Sending goal...')
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg, feedback_callback=self.feedback_callback
        )
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected :(')
            return

        self.get_logger().info('Goal accepted :)')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Result received. Error code: {result.error_code}')
        rclpy.shutdown()

    def feedback_callback(self, feedback_msg):
        pass


def main(args=None):
    rclpy.init(args=args)
    action_client = ArmTester()
    action_client.send_goal()
    rclpy.spin(action_client)


if __name__ == '__main__':
    main()
