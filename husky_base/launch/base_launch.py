import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution, LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

import xacro


ARGUMENTS = [
    DeclareLaunchArgument('urdf_extras', default_value='empty.urdf',
                          description='Path to URDF extras file. In order to add stuff to the husky'),

    DeclareLaunchArgument('localization_params', default_value=PathJoinSubstitution([FindPackageShare("husky_control"),"config","localization.yaml"],),
                          description='Path to Localization .yaml file. In order to add for example um7(set publish tf to true)'),

    DeclareLaunchArgument('control_params', default_value=PathJoinSubstitution([FindPackageShare("husky_control"),"config","control.yaml"],),
                          description='Path to control .yaml file. In order to add for example um7(set publish tf to false)'),

    DeclareLaunchArgument('urdf_extras', default_value='empty.urdf',
                          description='Path to URDF extras file. In order to add stuff to the husky'),

    DeclareLaunchArgument('localization_params', default_value=PathJoinSubstitution([FindPackageShare("husky_control"),"config","localization.yaml"],),
                          description='Path to Localization .yaml file. In order to add for example um7(set publish tf to true)'),

    DeclareLaunchArgument('control_params', default_value=PathJoinSubstitution([FindPackageShare("husky_control"),"config","control.yaml"],),
                          description='Path to control .yaml file. In order to add for example um7(set publish tf to false)'),                          
]

os.environ["HUSKY_TOP_PLATE_ENABLED"] = "false"
os.environ["HUSKY_IMU_XYZ"] = "0 0 0"
os.environ["HUSKY_IMU_RPY"] = "0 0 0"


def generate_launch_description():

    urdf_extras_path = LaunchConfiguration("urdf_extras")
    config_husky_velocity_controller = LaunchConfiguration("control_params")
    localization_params = LaunchConfiguration("localization_params")

    # Get URDF via xacro
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare("husky_description"), "urdf", "husky.urdf.xacro"]
            ),
            " ",
            "name:=husky",
            " ",
            "prefix:=''",
            " ",
            "urdf_extras:=",urdf_extras_path
        ]
    )
    robot_description = {"robot_description": robot_description_content}

    node_robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[robot_description],
    )

    node_controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_description, config_husky_velocity_controller],
        output={
            "stdout": "screen",
            "stderr": "screen",
        },
    )

    spawn_controller = Node(
        package="controller_manager",
        executable="spawner.py",
        arguments=["joint_state_broadcaster"],
        output="screen",
    )

    spawn_husky_velocity_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["husky_velocity_controller"],
        output="screen",
    )

    #Launch husky_control
    launch_husky_control = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution(
        [FindPackageShare("husky_control"), 'launch', 'control_launch.py'])),
        launch_arguments ={
            "params_file" : localization_params
        }.items()
    )

    #Launch husky_teleop_base
    launch_husky_teleop_base = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution(
        [FindPackageShare("husky_control"), 'launch', 'teleop_base_launch.py'])),
    )

    #Launch husky_teleop_joy
    launch_husky_teleop_joy = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution(
        [FindPackageShare("husky_control"), 'launch', 'teleop_joy_launch.py'])),
    )



    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(node_robot_state_publisher)
    ld.add_action(node_controller_manager)
    ld.add_action(spawn_controller)
    ld.add_action(spawn_husky_velocity_controller)
    ld.add_action(launch_husky_control)
    ld.add_action(launch_husky_teleop_base)
    ld.add_action(launch_husky_teleop_joy)

    return ld
