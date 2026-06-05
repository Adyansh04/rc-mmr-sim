import rclpy
from lifecycle_msgs.srv import GetState

nodes = [
    'controller_server', 'smoother_server', 'planner_server', 
    'route_server', 'behavior_server', 'velocity_smoother', 
    'collision_monitor', 'bt_navigator', 'waypoint_follower', 
    'docking_server', 'slam_toolbox'
]

def main():
    rclpy.init()
    node = rclpy.create_node('check_states')
    
    for n in nodes:
        cli = node.create_client(GetState, f'/rc/{n}/get_state')
        if not cli.wait_for_service(timeout_sec=2.0):
            print(f'{n}: service not available')
            continue
        req = GetState.Request()
        future = cli.call_async(req)
        rclpy.spin_until_future_complete(node, future, timeout_sec=1.0)
        if future.done():
            res = future.result()
            print(f'{n}: {res.current_state.label} ({res.current_state.id})')
        else:
            print(f'{n}: service call timed out')
            
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
