# Source and third-party notices

Repository packaging and maintenance: Haneul Jeon.

The research code originates from [Holiclife-KTH/Multi-layered-3D-NDT-Scan-Matching](https://github.com/Holiclife-KTH/Multi-layered-3D-NDT-Scan-Matching), published commit `babfbc2b40f4d5a35d19305e0542ce69191a7189`. The associated paper is by Taeho Kim, Haneul Jeon, and Donghun Lee. Maintenance metadata does not replace original authorship.

The following dependencies are included as local source directories. Their existing copyright notices, author information, and license files are retained.

| Directory | Upstream repository | Pinned commit |
| --- | --- | --- |
| `LIO-SAM` | [TixiaoShan/LIO-SAM](https://github.com/TixiaoShan/LIO-SAM) | `0be1fbe6275fb8366d5b800af4fc8c76a885c869` |
| `fast_gicp` | [koide3/fast_gicp](https://github.com/koide3/fast_gicp) | `b1ff53f06f0a2fa6b6d84d6963766d4891000c3c` |
| `isaac_sim_pointcloud_tool` | [liuxiao916/isaac_sim_pointcloud_tool](https://github.com/liuxiao916/isaac_sim_pointcloud_tool) | `25c4df40035aad0e81693e22a3915b60e16a396f` |
| `pointcloud2_merge` | [aaryanmurgunde/pointcloud2_merge](https://github.com/aaryanmurgunde/pointcloud2_merge) | `957190a618e07a0d5d119cc0950cb19adf79c813` |
| `fast_gicp/thirdparty/Sophus` | [strasdat/Sophus](https://github.com/strasdat/Sophus) | `d63ad09177f6b99ba605d684bac7f4b8d6820f5a` |
| `fast_gicp/thirdparty/nvbio` | [NVlabs/nvbio](https://github.com/NVlabs/nvbio) | `9bb7e6363c65f65e46f21df09bef98e404250f10` |
| `fast_gicp/thirdparty/pybind11` | [pybind/pybind11](https://github.com/pybind/pybind11) | `0e01c243c7ffae3a2e52f998bacfe82f56aa96d9` |
| `fast_gicp/thirdparty/Eigen` | [eigenteam/eigen-git-mirror](https://github.com/eigenteam/eigen-git-mirror) | `1fd5ce1002a6f30e1169b529b291216a18be2f7e` |
| `NDT_scan_matching/autoware_messages` | [autowarefoundation/autoware_ai_messages](https://github.com/autowarefoundation/autoware_ai_messages) | `0a210c604176b0a77098507f6691d627a3249631` |

Eigen is obtained from the official `eigenteam/eigen-git-mirror` at the same commit referenced by fast_gicp's original GitLab submodule.

The existing `NDT_scan_matching` code also contains Autoware components. Their original per-file and package notices remain in place. This repository does not apply a new blanket license over those components. Some original research-package metadata contains `TODO` license fields, which are retained rather than replaced with an invented license.

Local integration changes are listed in [Runtime notes](docs/runtime-notes.md). `isaac_sim_pointcloud_tool` has a target alias and configurable topics/frame. LIO-SAM and converter documentation media are linked to the pinned upstream source rather than copied. No Git author history was rewritten.
