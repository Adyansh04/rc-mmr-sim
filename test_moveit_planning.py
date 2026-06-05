import rclpy
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import Constraints, JointConstraint, MotionPlanRequest
from rclpy.action import ActionClient
from rclpy.node import Node


class MoveItPlanner(Node):
    def __init__(self):
        super().__init__('moveit_planner')
        self._action_client = ActionClient(self, MoveGroup, '/rc/move_action')

    def send_goal(self):
        goal_msg = MoveGroup.Goal()
        req = MotionPlanRequest()
        req.group_name = 'arm_0'
        req.num_planning_attempts = 10
        req.allowed_planning_time = 5.0

        # Define a joint constraint
        joint_names = [
            'arm_0_shoulder_pan_joint',
            'arm_0_shoulder_lift_joint',
            'arm_0_elbow_joint',
            'arm_0_wrist_1_joint',
            'arm_0_wrist_2_joint',
            'arm_0_wrist_3_joint',
        ]
        # Target positions: slightly bent posture
        target_positions = [0.1, -1.0, 1.0, -0.5, 0.5, 0.1]

        constraints = Constraints()
        for name, pos in zip(joint_names, target_positions):
            jc = JointConstraint()
            jc.joint_name = name
            jc.position = pos
            jc.tolerance_above = 0.01
            jc.tolerance_below = 0.01
            jc.weight = 1.0
            constraints.joint_constraints.append(jc)

        req.goal_constraints.append(constraints)
        goal_msg.request = req

        # We want to plan and execute
        goal_msg.planning_options.plan_only = False

        self.get_logger().info('Waiting for move_action server...')
        self._action_client.wait_for_server()

        self.get_logger().info('Sending planning goal...')
        self._send_goal_future = self._action_client.send_goal_async(goal_msg)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected :(')
            rclpy.shutdown()
            return

        self.get_logger().info('Goal accepted :)')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Result received. Error code: {result.error_code.val}')
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    client = MoveItPlanner()
    client.send_goal()
    rclpy.spin(client)


if __name__ == '__main__':
    main()
