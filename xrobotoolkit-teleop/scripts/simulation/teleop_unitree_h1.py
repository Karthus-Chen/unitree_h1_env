import os

import tyro

from xrobotoolkit_teleop.simulation.placo_teleop_controller import (
    PlacoTeleopController,
)
from xrobotoolkit_teleop.utils.path_utils import ASSET_PATH

import numpy as np
from robot_joint_client import ZMQClient


def main(
    robot_urdf_path: str = os.path.join(ASSET_PATH, "unitree/h1_2/h1_2.urdf"),
    scale_factor: float = 1,
):
    """
    Main function to run the Unitree G1 dual arm teleoperation with Placo visualization.
    """
    # Define dual arm configuration for Unitree G1
    config = {
        "left_arm": {
            "link_name": "left_wrist_yaw_link",
            "pose_source": "left_controller",
            "control_trigger": "left_grip",
            # "motion_tracker": {
            #     "serial": "PC2310BLH9020707B",
            #     "link_target": "L_elbow_pitch",
            # },
        },
        "right_arm": {
            "link_name": "right_wrist_yaw_link",
            "pose_source": "right_controller",
            "control_trigger": "right_grip",
            # "motion_tracker": {
            #     "serial": "PC2310BLH9020740B",
            #     "link_target": "R_elbow_pitch",
            # },
        },
    }
    default_joints = {
        # Left arm default positions (slightly bent, natural pose)
        "torso_joint":0.0,

        "left_shoulder_pitch_joint": 0,
        "left_shoulder_roll_joint": 0,
        "left_shoulder_yaw_joint": 0.0,
        "left_elbow_pitch_joint": 0,
        "left_elbow_roll_joint": 0.0,
        "left_wrist_yaw_joint": 0.0,
        "left_wrist_pitch_joint": 0.0,
        # Right arm default positions (mirrored)
        "right_shoulder_pitch_joint": 0,
        "right_shoulder_roll_joint": 0,
        "right_shoulder_yaw_joint": 0.0,
        "right_elbow_pitch_joint": 0,
        "right_elbow_roll_joint": 0.0,
        "right_wrist_yaw_joint": 0.0,
        "right_wrist_pitch_joint": 0.0,
    }

    # Create and initialize the teleoperation controller
    controller = PlacoTeleopController(
        robot_urdf_path=robot_urdf_path,
        manipulator_config=config,
        scale_factor=scale_factor,
        is_vis=False,
        q_init=np.zeros(15)
    )

    # Add joint regularization task to keep arms in natural position
    joints_task = controller.solver.add_joints_task()

    # Define default joint positions for natural arm pose


    joints_task.set_joints(default_joints)
    joints_task.configure("joints_regularization", "soft", 1e-2)

    zmq_client=ZMQClient()
    while not controller._stop_event.is_set():
        try:
            controller.run_single_step()
            if(controller.reset_flag):
                zmq_client.send_data(mode="reset", data=np.zeros(32))
            else:
                sol_q=np.zeros(32)
                sol_q[14]=controller.placo_robot.state.q[7]
                sol_q[0:14]=controller.placo_robot.state.q[8:22]
                sol_q[15]=controller.xr_client.get_key_value_by_name("left_trigger")
                sol_q[16]=controller.xr_client.get_key_value_by_name("right_trigger")
                # print(sol_q[:15])
                zmq_client.send_data(mode="eval", data=sol_q.copy())
                
        except KeyboardInterrupt:
            print("\nTeleoperation stopped.")
            controller._stop_event.set()


if __name__ == "__main__":
    tyro.cli(main)
