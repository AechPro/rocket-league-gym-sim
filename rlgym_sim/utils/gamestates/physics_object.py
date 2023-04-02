"""
A class to represent the state of a physics object from the game.
"""

from rlgym_sim.utils import math
import numpy as np
from typing import Optional


class PhysicsObject(object):
    def __init__(self, position=None, quaternion=None, linear_velocity=None, angular_velocity=None):
        self.position: np.ndarray = position if position is not None else np.zeros(3)

        # ones by default to prevent mathematical errors when converting quat to rot matrix on empty physics state
        self.quaternion: np.ndarray = quaternion if quaternion is not None else np.ones(4)

        self.linear_velocity: np.ndarray = linear_velocity if linear_velocity is not None else np.zeros(3)
        self.angular_velocity: np.ndarray = angular_velocity if angular_velocity is not None else np.zeros(3)
        self._euler_angles: Optional[np.ndarray] = np.zeros(3)
        self._rotation_mtx: Optional[np.ndarray] = np.zeros((3,3))
        self._has_computed_rot_mtx = False
        self._has_computed_euler_angles = False

    def copy(self, other):
        self.position = other.position.copy()
        self.linear_velocity = other.linear_velocity.copy()
        self.angular_velocity = other.angular_velocity.copy()
        self.quaternion = other.quaternion.copy()

        self._euler_angles = other._euler_angles.copy()
        self._rotation_mtx = other._rotation_mtx.copy()
        self._has_computed_rot_mtx = other._has_computed_rot_mtx
        self._has_computed_euler_angles = other._has_computed_euler_angles

    def decode_data(self, physics_data: np.ndarray):
        """
        Function to decode the physics state of a car from the game state array.
        :param car_data: Slice of game state array containing the car data to decode.
        """
        self.position = physics_data[:3]
        self.quaternion = physics_data[3:7]
        self.linear_velocity = physics_data[7:10]
        self.angular_velocity = physics_data[10:13]
        self._rotation_mtx = physics_data[13:22].reshape(3,3).transpose()
        self._euler_angles = physics_data[22:]
        self._has_computed_euler_angles = True
        self._has_computed_rot_mtx = True

    def forward(self) -> np.ndarray:
        return self.rotation_mtx()[:, 0]

    def right(self) -> np.ndarray:
        return self.rotation_mtx()[:, 1]

    def left(self) -> np.ndarray:
        return self.rotation_mtx()[:, 1] * -1

    def up(self) -> np.ndarray:
        return self.rotation_mtx()[:, 2]

    def pitch(self) -> float:
        return self.euler_angles()[0]

    def yaw(self) -> float:
        return self.euler_angles()[1]

    def roll(self) -> float:
        return self.euler_angles()[2]

    # pitch, yaw, roll
    def euler_angles(self) -> np.ndarray:
        if not self._has_computed_euler_angles:
            self._euler_angles = math.quat_to_euler(self.quaternion)
            self._has_computed_euler_angles = True

        return self._euler_angles

    def rotation_mtx(self) -> np.ndarray:
        if not self._has_computed_rot_mtx:
            self._rotation_mtx = math.quat_to_rot_mtx(self.quaternion)
            self._has_computed_rot_mtx = True

        return self._rotation_mtx

    def serialize(self):
        """
        Function to serialize all the values contained by this physics object into a single 1D list. This can be useful
        when constructing observations for a policy.
        :return: List containing the serialized data.
        """
        repr = []

        if self.position is not None:
            for arg in self.position:
                repr.append(arg)
                
        if self.quaternion is not None:
            for arg in self.quaternion:
                repr.append(arg)
                
        if self.linear_velocity is not None:
            for arg in self.linear_velocity:
                repr.append(arg)
                
        if self.angular_velocity is not None:
            for arg in self.angular_velocity:
                repr.append(arg)

        if self._euler_angles is not None:
            for arg in self._euler_angles:
                repr.append(arg)

        if self._rotation_mtx is not None:
            for arg in self._rotation_mtx.ravel():
                repr.append(arg)

        return repr

    def __str__(self):
        return "{} | {} | {} | {} | {} | {}".format(self.position.tolist(),
                                                   self.linear_velocity.tolist(),
                                                   self.angular_velocity.tolist(),
                                                   self.quaternion.tolist(),
                                                   self.euler_angles().tolist(),
                                                   self.rotation_mtx().ravel().tolist())
