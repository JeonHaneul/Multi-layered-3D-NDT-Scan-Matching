"""ROS-independent behavioral checks for the packaged fusion entry point."""
import importlib.util
import math
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch
import numpy as np


def pose():
    return SimpleNamespace(position=SimpleNamespace(x=0.0, y=0.0, z=0.0),
                           orientation=SimpleNamespace(x=0.0, y=0.0, z=0.0, w=1.0))


def stamped_pose():
    return SimpleNamespace(pose=pose(), header=SimpleNamespace(frame_id='', stamp=None))


def measurement(x, y, variance):
    p = pose()
    p.position.x, p.position.y = x, y
    cov = np.eye(6) * variance
    return SimpleNamespace(pose=SimpleNamespace(pose=p, covariance=cov.ravel().tolist()))


class Publisher:
    def __init__(self, *args, **kwargs):
        self.messages = []

    def publish(self, msg):
        self.messages.append(msg)


def module(name, **attributes):
    result = ModuleType(name)
    result.__dict__.update(attributes)
    return result


class FusionTests(unittest.TestCase):
    def setUp(self):
        rospy = module('rospy', Publisher=Publisher,
                       Time=SimpleNamespace(now=lambda: 1),
                       logdebug=lambda *a: None, logwarn_throttle=lambda *a: None)
        transforms = module('tf.transformations',
                            euler_from_quaternion=lambda q: (0, 0, 2 * math.atan2(q[2], q[3])),
                            quaternion_from_euler=lambda r, p, y: (0, 0, math.sin(y / 2), math.cos(y / 2)))
        modules = {'rospy': rospy, 'tf': module('tf'), 'tf.transformations': transforms}
        for pkg, fields in {
            'geometry_msgs.msg': dict(Pose=pose, PoseStamped=stamped_pose, PoseWithCovarianceStamped=object),
            'std_msgs.msg': dict(Empty=object, Float32=object),
            'autoware_msgs.msg': dict(NDTStat=object),
            'tf2_msgs.msg': dict(TFMessage=object),
        }.items():
            modules[pkg.split('.')[0]] = module(pkg.split('.')[0])
            modules[pkg] = module(pkg, **fields)
        path = Path(__file__).resolve().parents[1] / 'NDT_scan_matching/ndt_matching/src/fusion.py'
        with patch.dict(sys.modules, modules):
            spec = importlib.util.spec_from_file_location('tested_fusion', path)
            loaded = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(loaded)
        self.fusion = loaded.Fusion()

    def test_waits_for_both_layers(self):
        self.fusion.fusion()
        self.fusion.callback_low(measurement(2, 4, 1))
        self.fusion.fusion()
        self.assertEqual(len(self.fusion.pub.messages), 0)

    def test_equal_uncertainty_gives_midpoint(self):
        self.fusion.callback_low(measurement(2, 4, 1))
        self.fusion.callback_mid(measurement(6, 8, 1))
        self.fusion.fusion()
        output = self.fusion.pub.messages[-1]
        self.assertAlmostEqual(output.pose.position.x, 4)
        self.assertAlmostEqual(output.pose.position.y, 6)
        self.assertEqual(output.header.frame_id, 'map')

    def test_more_certain_layer_has_more_influence(self):
        self.fusion.callback_low(measurement(0, 0, 1))
        self.fusion.callback_mid(measurement(8, 4, 3))
        self.fusion.fusion()
        output = self.fusion.pub.messages[-1]
        self.assertAlmostEqual(output.pose.position.x, 2)
        self.assertAlmostEqual(output.pose.position.y, 1)

    def test_singular_covariance_does_not_publish(self):
        self.fusion.callback_low(measurement(1, 2, 0))
        self.fusion.callback_mid(measurement(3, 4, 0))
        self.fusion.fusion()
        self.assertEqual(len(self.fusion.pub.messages), 0)


if __name__ == '__main__':
    unittest.main()
