#!/usr/bin/env bash
set -eo pipefail
repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -f /opt/ros/noetic/setup.bash ]]; then
  echo "ROS 1 Noetic is required. Use an Ubuntu 20.04 environment with ROS Noetic installed." >&2
  exit 1
fi
source /opt/ros/noetic/setup.bash
sudo apt-get update
sudo apt-get install -y python3-catkin-tools python3-rosdep python3-numpy \
  python3-opencv python3-openpyxl python3-pandas libeigen3-dev libpcl-dev \
  libopencv-dev libcurl4-openssl-dev libyaml-cpp-dev
if [[ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]]; then
  sudo rosdep init
fi
rosdep update --include-eol-distros
# The archived Autoware message bundle also contains an unused LGSVL adapter.
# It is excluded from the default build and is the sole skipped rosdep key.
rosdep install --from-paths \
  "$repo_dir/NDT_scan_matching" "$repo_dir/ZW_ScanMatching" \
  "$repo_dir/pcd_clustering" "$repo_dir/isaac_sim_pointcloud_tool" \
  "$repo_dir/pointcloud2_merge" "$repo_dir/chasss_for_urdf2" \
  --ignore-src --rosdistro noetic --skip-keys lgsvl_msgs -r -y
