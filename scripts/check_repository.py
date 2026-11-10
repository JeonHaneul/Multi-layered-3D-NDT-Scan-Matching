#!/usr/bin/env python3
"""Check the bundled sources and documented launch files without a ROS install."""
import ast
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def check():
    errors = []
    required = [
        'LIO-SAM/src/mapOptmization.cpp',
        'LIO-SAM/LICENSE',
        'fast_gicp/include/fast_gicp/gicp/fast_gicp.hpp',
        'fast_gicp/LICENSE',
        'fast_gicp/thirdparty/Eigen/Eigen/Core',
        'fast_gicp/thirdparty/Sophus/sophus/so3.hpp',
        'fast_gicp/thirdparty/nvbio/nvbio/basic/types.h',
        'fast_gicp/thirdparty/pybind11/include/pybind11/pybind11.h',
        'isaac_sim_pointcloud_tool/src/converter.cpp',
        'pointcloud2_merge/src/pointcloud2_merge.cpp',
        'map/230512map/GlobalMap.pcd',
    ]
    for name in ['autoware_msgs', 'autoware_config_msgs', 'autoware_system_msgs',
                 'autoware_lanelet2_msgs', 'vector_map_msgs']:
        required.append('NDT_scan_matching/autoware_messages/' + name + '/package.xml')
    for relative in required:
        p = ROOT / relative
        if not p.is_file() or p.stat().st_size == 0:
            errors.append('Missing or empty dependency/asset: ' + relative)
    for relative in ['.gitmodules', 'fast_gicp/.gitmodules']:
        if (ROOT / relative).exists():
            errors.append('A submodule manifest remains: ' + relative)

    packages = {}
    # Stop at package roots so nested dependency examples are not ROS packages.
    def find_packages(folder):
        manifest = folder / 'package.xml'
        if manifest.is_file():
            try:
                name = ET.parse(manifest).getroot().findtext('name')
                if name in packages:
                    errors.append('Duplicate ROS package: ' + str(name))
                packages[name] = folder
            except ET.ParseError as exc:
                errors.append(str(manifest) + ': ' + str(exc))
            return
        for child in folder.iterdir():
            if child.is_dir() and child.name not in {'.git', '__pycache__'}:
                find_packages(child)
    find_packages(ROOT)

    node_count = 0
    for mode in ['normal', 'rejection', 'fusion']:
        launch = ROOT / 'ZW_ScanMatching/launch' / (mode + '.launch')
        text = launch.read_text(encoding='utf-8')
        try:
            tree = ET.fromstring(text)
        except ET.ParseError as exc:
            errors.append(str(launch) + ': ' + str(exc))
            continue
        defaults = {arg.attrib['name']: arg.attrib.get('default', '') for arg in tree.findall('arg')}
        for node in tree.iter('node'):
            node_count += 1
            pkg, target = node.attrib['pkg'], node.attrib['type']
            target = re.sub(r'\$\(arg ([^)]+)\)', lambda match: defaults.get(match.group(1), match.group(0)), target)
            if pkg not in packages:  # System ROS nodes such as tf and rviz.
                continue
            path = packages[pkg]
            cmake = (path / 'CMakeLists.txt').read_text(encoding='utf-8')
            if target.endswith('.py'):
                if not list(path.rglob(target)) or target not in cmake:
                    errors.append('Missing Python source or catkin entry: ' + pkg + '/' + target)
            elif '$(' not in target and not re.search(r'add_executable\(\s*' + re.escape(target) + r'\s', cmake):
                errors.append('Missing executable target: ' + pkg + '/' + target)
        for pkg, tail in re.findall(r'\$\(find ([^)]+)\)([^\s\"\'<>]+)', text):
            if pkg in packages and not (packages[pkg] / tail.lstrip('/')).resolve().exists():
                errors.append('Missing launch resource: ' + pkg + tail)

    python_count = 0
    for relative in ['ZW_ScanMatching/scripts', 'NDT_scan_matching/ndt_matching/src', 'scripts']:
        for path in (ROOT / relative).glob('*.py'):
            try:
                ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
                python_count += 1
            except SyntaxError as exc:
                errors.append(str(exc))

    for relative in ['ZW_ScanMatching', 'pcd_clustering', 'NDT_scan_matching/ndt_matching', '.vscode']:
        for path in (ROOT / relative).rglob('*'):
            if path.is_file() and path.suffix in {'.py', '.cpp', '.h', '.xml', '.launch', '.json', '.yaml'}:
                if re.search(r'/home/[^/\s]+/', path.read_text(encoding='utf-8'), re.I):
                    errors.append('Personal absolute path: ' + str(path.relative_to(ROOT)))

    for error in errors:
        print('ERROR:', error)
    print('Checked {} ROS packages, {} main-launch nodes and {} Python files.'.format(
        len(packages), node_count, python_count))
    print('This check does not compile ROS code or run sensor data.')
    return not errors


if __name__ == '__main__':
    sys.exit(0 if check() else 1)
