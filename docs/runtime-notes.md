# Runtime notes

## Environment and inputs

This packaging pass targets ROS 1 Noetic on Ubuntu 20.04. The previous README named Melodic, while the checked-in editor paths named Noetic and active scripts used Python 3. No exact Isaac Sim release or complete environment lock was recorded in the supplied source.

The core pipeline uses `ndt_cpu` through `method_type=1`. The build script sets `AUTOWARE_COMPILE_WITH_CUDA=OFF` because the separate Autoware `ndt_gpu` package is absent. Bundling fast_gicp does not provide Autoware's `ndt_gpu` backend.

| Input | Required by | Notes |
| --- | --- | --- |
| `/point_cloud` | Bundled converter | `sensor_msgs/PointCloud2` with XYZ coordinates |
| `/VLP16_pointcloud` | Core perception nodes | Published by the converter, or supplied directly with `use_converter:=false` |
| `/rgb` | Rejection and fusion | RGB image using the same image geometry as the depth input |
| `/depth_img` | Rejection and fusion | Depth convertible to `32FC1`, with scale matching `camera_factor` |
| `/initialpose` | NDT | `geometry_msgs/PoseWithCovarianceStamped` in the map frame |
| `/clock` | Simulation-time operation | Required when `use_sim_time=true` |

`camera.yaml` retains the original intrinsics as defaults. The color thresholds in `lineExtraction.py` and the cluster thresholds in `clustering.cpp` and `clustering_ml.cpp` are warehouse-specific. They must be checked against the sensor data being used. Map, scan, camera, and robot transforms must describe the same geometry.

The converter's `sensor_frame` option changes the header label only. Leave it empty to preserve the incoming frame. Transform point coordinates upstream if the input is expressed in a different frame.

## Two-layer processing

`lineExtraction.py` detects shelf features and publishes left/right ROI boundaries. `lidarROI` extracts points in that ROI. `clustering_ml` estimates a height and publishes upper/lower scan subsets. The voxel filter produces the two filtered inputs to `ndt_matching_ml`. That node publishes the layer poses and covariance matrices. `fusion.py` combines the estimates and publishes `/fusion_position`.

This two-layer implementation uses a shared full-map NDT target for the two scan subsets. Do not describe this implementation as building a separate map target for each of the two layers. The older three-layer code contains a different map-slicing path.

The fusion calculation is preserved from the source. Packaging adds input readiness checks, a 10 Hz loop, and controlled handling of singular covariance matrices. This does not establish that the covariance estimates, angular behavior, or experimental results reproduce the paper under a new sensor configuration.

## Main launch changes

- Replaced personal absolute map paths with package-relative paths and corrected the missing `230522/` directory in the baseline map path.
- Enabled the existing baseline converter, filter, and NDT nodes that were commented out in `normal.launch`.
- Added a `points_converter` executable alias from the upstream `converter.cpp`, with configurable input/output topics and optional output frame.
- Started `fusion.py` from the two-layer launch file and installed the Python entry points with catkin.
- Added image-topic remaps, a camera configuration file, simulation-time selection, and optional RViz startup.
- Added message-generation dependencies and guards against missing depth, incomplete ROI messages, and uninitialized cluster height.

No NDT objective, solver, covariance formula, or reported paper metric was changed.

## Older experimental files

`NDT_scan_matching/ndt_matching/launch/scan.launch` and `scan_multi.launch` are retained for reference. Use the three main `ZW_ScanMatching` launch files for the documented setup.

`scan_multi.launch` expects a locally modified converter and a `pcd_slicer` executable that are absent from the recorded upstream submodule. Its three-layer filtering interfaces also differ from the active two-layer filter implementation. This entry point is not a complete runnable experiment. Adding the upstream submodule alone cannot recover uncommitted local modifications.

`dataset.py` is an experiment helper rather than a general evaluation tool. It assumes `/tf2` and `/tf3` reference streams, contains experiment-specific offsets, and has CSV logging disabled. `Obstacle_randomization.py` requires the simulation's `teleport` service and scene prim `/World/object`. The full warehouse scene, service implementation, and original bag files are not part of this repository.

## Optional packages

The full fast_gicp source and its Eigen, Sophus, nvbio, and pybind11 dependency trees are included at the pinned commits. Its CPU, CUDA, and Python builds have separate upstream requirements. Use `fast_gicp/README.md` and its CMake options for those optional targets.

LIO-SAM's source, build files, configuration, license, and README are included. Upstream demonstration images, videos, and the LIO-SAM paper PDF are omitted. The README's media links refer to its pinned upstream version. GTSAM is a separate system dependency when building LIO-SAM.

The Autoware message bundle includes `autoware_external_msgs`, which depends on `lgsvl_msgs`. It is not required by this NDT pipeline and is not selected by the default build. The installer skips that unused rosdep key.

## Checks and limitations

```bash
python3 scripts/check_repository.py
python3 -m unittest discover -s tests
```

These checks cover packaged sources, main launch references, Python syntax, and fusion startup/numerical behavior. They do not compile ROS C++ code or validate a robot trajectory. The packaging host had no usable ROS, Docker, or WSL Linux environment, so the full Linux build and sensor-data replay remain unverified.

Before comparing modes, use one reference map, the same sensor data and initial pose, and the same coordinate conventions. Validate the core baseline first, then the rejection and fusion pipelines.
