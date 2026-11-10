# Multi-Layered 3D NDT Scan Matching

## Paper

This repository contains research code for the following paper:

**A Multi-Layered 3D NDT Scan-Matching Method for Robust Localization in Logistics Warehouse Environments**  
Taeho Kim, Haneul Jeon, and Donghun Lee  
*Sensors*, 23(5), 2671, 2023  
[Paper](https://www.mdpi.com/1424-8220/23/5/2671) | [DOI: 10.3390/s23052671](https://doi.org/10.3390/s23052671)

The method partitions point clouds by height and uses the uncertainty of NDT estimates to reduce the effect of changing warehouse layouts. The paper reports simulation experiments in NVIDIA Omniverse Isaac Sim.

## Overview

The code combines a reference point-cloud map with live LiDAR measurements. The two-layer experiment also uses RGB-D shelf features to estimate a region of interest and the height at which the scan is divided. Separate NDT estimates are then combined using their covariance matrices.

Three main launch files are provided:

| Mode | Launch file | Processing |
| --- | --- | --- |
| Baseline | `ZW_ScanMatching/launch/normal.launch` | Point-cloud conversion, voxel filtering, and standard NDT |
| Layer rejection | `ZW_ScanMatching/launch/rejection.launch` | RGB-D ROI extraction, height-based point rejection, and NDT |
| Two-layer fusion | `ZW_ScanMatching/launch/fusion.launch` | RGB-D ROI extraction, upper/lower scan partitioning, two NDT estimates, and pose fusion |

This is a ROS 1 research workspace. It includes the map files and dependency source trees, but requires a compatible sensor stream or recorded ROS bag. The original warehouse scene and evaluation bags are not included. Runtime assumptions and older experimental entry points are described in [Runtime notes](docs/runtime-notes.md).

## Repository layout

| Path | Contents |
| --- | --- |
| `ZW_ScanMatching/` | Main launch files, RGB-D shelf feature extraction, LiDAR ROI, and experiment utilities |
| `pcd_clustering/` | Clustering and height-based scan partitioning or rejection |
| `NDT_scan_matching/ndt_matching/` | NDT localization nodes, covariance-based pose fusion, and evaluation helpers |
| `NDT_scan_matching/ndt_cpu/` | CPU NDT implementation used by the main launch files |
| `NDT_scan_matching/common/` | Map loading and Autoware support packages |
| `NDT_scan_matching/autoware_messages/` | Bundled Autoware message definitions |
| `isaac_sim_pointcloud_tool/`, `pointcloud2_merge/` | Point-cloud conversion and merging dependencies |
| `map/`, `chasss_for_urdf2/` | Reference PCD maps and robot models |
| `LIO-SAM/`, `fast_gicp/` | Optional mapping and registration packages, including fast_gicp's nested dependencies |
| `scripts/`, `docs/` | Dependency installation, CPU build, repository checks, and configuration notes |

The former submodules are included as ordinary directories. **No `git submodule update` is required.** Upstream versions and licenses are recorded in [Third-party notices](THIRD_PARTY_NOTICES.md).

## Setup

The integration target is **Ubuntu 20.04, ROS 1 Noetic, Python 3, and C++14**. PCL, Eigen, OpenCV, ROS packages, and the compiler are system dependencies. Isaac Sim is needed only when using a live simulated sensor source.

Place the repository under `~/ndt_ws/src/Multi-layered-3D-NDT-Scan-Matching`, then run:

```bash
cd ~/ndt_ws/src/Multi-layered-3D-NDT-Scan-Matching
bash scripts/install_dependencies.sh
bash scripts/build.sh
source ../../devel/setup.bash
```

The build script selects the CPU NDT pipeline and its dependencies. LIO-SAM, fast_gicp, and the unused LGSVL message adapter are not built by default. LIO-SAM additionally requires GTSAM and a LiDAR/IMU configuration. Optional package instructions remain in their own README files.

**Validation status:** source integrity, launch references, Python syntax, and fusion unit tests were checked during packaging. A ROS build and an end-to-end Isaac Sim or rosbag run still need to be performed in the target Linux environment.

## Run

Start the sensor source first. The default LiDAR input is `/point_cloud`. The layer-rejection and fusion modes additionally require aligned `/rgb` and `/depth_img` images. Set a starting pose using RViz's **2D Pose Estimate** tool, which publishes `/initialpose` in the `map` frame.

Choose one mode at a time. Use the same map for comparisons:

```bash
MAP="$PWD/map/230512map/GlobalMap.pcd"

# Baseline
roslaunch ZW_ScanMatching normal.launch path_pcd:="$MAP"

# Layer rejection
roslaunch ZW_ScanMatching rejection.launch path_pcd:="$MAP"

# Two-layer fusion, including the fusion.py node
roslaunch ZW_ScanMatching fusion.launch path_pcd:="$MAP"
```

For a ROS bag, launch the selected mode and play a bag containing the required topics with `rosbag play --clock /path/to/experiment.bag`. Simulation time is enabled by default. For a live source without `/clock`, pass `use_sim_time:=false`.

| Argument or setting | Use |
| --- | --- |
| `path_pcd` | Reference PCD file. Defaults use repository-relative paths. |
| `input_points_topic` | LiDAR input to the bundled converter, default `/point_cloud` |
| `use_converter:=false` | Use an existing `/VLP16_pointcloud` stream directly |
| `sensor_frame` | Optional output frame label. Empty preserves the input frame. This does not transform point coordinates. |
| `rgb_topic`, `depth_topic` | Image topics for rejection and fusion |
| `camera_config` | Pinhole intrinsics in `ZW_ScanMatching/config/camera.yaml` |
| `tf_x`, `tf_y`, `tf_z`, `tf_roll`, `tf_pitch`, `tf_yaw` | Existing NDT extrinsic settings, which must match the sensor and map frames |
| `rviz:=false` | Start nodes without the RViz interface |

Inspect `/points_map`, `/filtered_points`, and `/ndt_pose` for the baseline. For fusion, inspect `/filtered_bottom_points`, `/filtered_top_points`, `/bottom_localizer_pose`, `/top_localizer_pose`, and `/fusion_position`.

## Citation

```bibtex
@article{kim2023multilayered,
  author  = {Kim, Taeho and Jeon, Haneul and Lee, Donghun},
  title   = {A Multi-Layered 3D NDT Scan-Matching Method for Robust
             Localization in Logistics Warehouse Environments},
  journal = {Sensors},
  year    = {2023},
  volume  = {23},
  number  = {5},
  pages   = {2671},
  doi     = {10.3390/s23052671}
}
```

Repository maintainer: [Haneul Jeon](https://github.com/JeonHaneul).
