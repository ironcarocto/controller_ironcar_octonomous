import io
import subprocess

import os
import pytest

ROOT_DIR = os.path.realpath(os.path.join(__file__, '..', '..', '..'))


@pytest.fixture(scope='module')
def build_source_distribution():
    os.chdir(ROOT_DIR)
    subprocess.check_output(['python', 'setup.py', 'egg_info'])
    yield None


def test_requirement1_controller_ironcar_code_is_present(build_source_distribution):
    egg_info_dir = 'controller_ironcar_octonomous.egg-info'
    source_list_file = os.path.join(ROOT_DIR, egg_info_dir, 'SOURCES.txt')
    with io.open(source_list_file) as f:
        sources = f.read()
        assert 'controller_ironcar/' in sources

def test_requirement2_default_autopilot_is_present(build_source_distribution):
    egg_info_dir = 'controller_ironcar_octonomous.egg-info'
    source_list_file = os.path.join(ROOT_DIR, egg_info_dir, 'SOURCES.txt')
    with io.open(source_list_file) as f:
        sources = f.read()
        assert 'controller_ironcar/resources/autopilots/autopilot_500k.hdf5' in sources