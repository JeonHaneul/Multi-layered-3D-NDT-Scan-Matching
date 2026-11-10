#!/usr/bin/env bash
set -eo pipefail
repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
source_dir="$(dirname -- "$repo_dir")"
if [[ "$(basename -- "$source_dir")" != src ]]; then
  echo "Place the repository in <catkin-workspace>/src/<repository-name>." >&2
  exit 1
fi
if [[ ! -f /opt/ros/noetic/setup.bash ]]; then
  echo "ROS Noetic was not found at /opt/ros/noetic." >&2
  exit 1
fi
source /opt/ros/noetic/setup.bash
workspace_dir="$(dirname -- "$source_dir")"
export AUTOWARE_COMPILE_WITH_CUDA=OFF
python3 "$repo_dir/scripts/check_repository.py"
catkin build --workspace "$workspace_dir" -j2 -p2 --summarize \
  ZW_ScanMatching ndt_matching map_file points_downsampler pcd_clustering \
  isaac_sim_pointcloud_tool pointcloud2_merge chasss_for_urdf2 \
  --cmake-args -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_STANDARD=14 \
  -DCATKIN_ENABLE_TESTING=OFF
printf '\nBuild finished. Source this workspace before launching:\nsource %s/devel/setup.bash\n' "$workspace_dir"
