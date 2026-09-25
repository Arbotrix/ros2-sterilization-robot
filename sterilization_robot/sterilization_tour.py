import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from std_msgs.msg import Bool
from visualization_msgs.msg import Marker

class SterilizationTour(Node):
    def __init__(self):
        super().__init__('sterilization_tour_node')
        
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.uvc_pub = self.create_publisher(Bool, '/uvc_light_status', 10)
        self.marker_pub = self.create_publisher(Marker, '/sterilization_coverage', 10)
        
        self.waypoints = [
            (1.0, 0.5, 1.0),
            (-1.5, 1.0, 1.0)
        ]
        self.current_wp_index = 0
        self.is_sterilizing = False
        self.sterilization_timer = None

    def send_goal(self):
        if self.current_wp_index >= len(self.waypoints):
            self.get_logger().info('Sterilization tour complete! Shutting down.')
            rclpy.shutdown()
            return

        self.nav_client.wait_for_server()
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        
        x, y, w = self.waypoints[self.current_wp_index]
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.orientation.w = w

        self.get_logger().info(f'Navigating to waypoint {self.current_wp_index + 1}...')
        self.send_goal_future = self.nav_client.send_goal_async(goal_msg)
        self.send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected.')
            return
        self.get_result_future = goal_handle.get_result_async()
        self.get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        if future.result().status == 4: # SUCCEEDED
            self.start_sterilization()
        else:
            self.get_logger().error('Navigation failed.')

    def start_sterilization(self):
        self.get_logger().info('Target reached! Starting sterilization sequence...')
        self.is_sterilizing = True
        
        # Turn lights ON
        uvc_msg = Bool()
        uvc_msg.data = True
        self.uvc_pub.publish(uvc_msg)
        self.publish_coverage_marker(state='ACTIVE')
        
        # 10-second sterilization timer
        self.sterilization_timer = self.create_timer(10.0, self.finish_sterilization)

    def finish_sterilization(self):
        if self.is_sterilizing:
            self.is_sterilizing = False
            if self.sterilization_timer:
                self.sterilization_timer.cancel()
            
            # Turn lights OFF
            uvc_msg = Bool()
            uvc_msg.data = False
            self.uvc_pub.publish(uvc_msg)
            self.publish_coverage_marker(state='FINISHED')
            self.get_logger().info('Sterilization complete. Moving on.')
            
            self.current_wp_index += 1
            self.send_goal()

    def publish_coverage_marker(self, state):
        marker = Marker()
        marker.header.frame_id = 'map'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.id = self.current_wp_index 
        marker.type = Marker.CYLINDER
        marker.action = Marker.ADD
        
        x, y, w = self.waypoints[self.current_wp_index]
        marker.pose.position.x = x
        marker.pose.position.y = y
        marker.pose.position.z = 0.05 
        marker.scale.x = 2.0
        marker.scale.y = 2.0
        marker.scale.z = 0.1 
        
        if state == 'ACTIVE':
            marker.color.a = 0.6
            marker.color.r, marker.color.g, marker.color.b = 0.0, 1.0, 1.0 # Cyan
        elif state == 'FINISHED':
            marker.color.a = 0.3
            marker.color.r, marker.color.g, marker.color.b = 0.0, 1.0, 0.0 # Green
            
        self.marker_pub.publish(marker)

def main(args=None):
    rclpy.init(args=args)
    node = SterilizationTour()
    node.send_goal()
    rclpy.spin(node)

if __name__ == '__main__':
    main()
