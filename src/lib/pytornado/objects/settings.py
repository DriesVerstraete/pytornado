#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# Copyright 2017-2019 Airinnova AB and the PyTornado authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------

# Authors:
# * Alessandro Gastaldi
# * Aaron Dettmann

"""
Data structures for execution settings.

Developed for Airinnova AB, Stockholm, Sweden.
"""

import os
import logging
import shutil

from pytornado.objects.utils import FixedOrderedDict

logger = logging.getLogger(__name__)

DIR_AIRCRAFT = 'aircraft'
DIR_AIRFOILS = 'airfoils'
DIR_DEFORMATION = 'deformation'
DIR_PLOTS = '_plots'
DIR_RESULTS = '_results'
DIR_SETTINGS = 'settings'
DIR_STATE = 'state'
DIR_TEMPLATE_WKDIR = 'pytornado'

#####################
#####################

from pathlib import Path, PurePath


class ProjectPaths:

    UID_ROOT = 'root'

    def __init__(self, root_dir):
        """
        Class providing tools for filepath handling

        Args:
            :root_dir: Project root directory
        """

        self.abs_paths = {}
        self._set_project_root_dir(root_dir)

    @property
    def root(self):
        """TODO"""

        return self.abs_paths[self.UID_ROOT]

    def _set_project_root_dir(self, root_dir):
        """
        Set the project root directory

        Args:
            :root_dir: Project root directory
        """

        self.abs_paths[self.UID_ROOT] = Path(root_dir).resolve()

    def add_path(self, uid, path, is_absolute=False):
        """
        Add a path

        Args:
            :uid: unique identifier
            :path: path string
            :is_absolute: flag
        """

        if uid in self.abs_paths.keys():
            raise ValueError(f"UID {uid} already used")

        path = Path(path)

        if not is_absolute:
            path = self.__class__.join_paths(self.root, path)

        self.abs_paths[uid] = path

    def add_sub_path(self, parent_uid, uid, path):
        """
        TODO
        """

        if uid_parent not in self.abs_paths.keys():
            raise ValueError(f"Parent UID {uid_parent} not found")

        parent_path = self.abs_paths[uid_parent]

        assembled_path = self.__class__.join_paths(parent_path, path2)
        self.abs_path

    def format_path(self, *args, **kwargs):
        """
        TODO
        """

        pass

    @staticmethod
    def join_paths(path1, path2):
        """
        TODO
        """

        path = PurePath(path1).joinpath(path2)
        return Path(path)

#####################
#####################


class Settings:
    """
    Data structure for the PyTornado execution settings

    Settings defines the tasks to be performed during execution.
    Settings also stores location of project files.

    Attributes:
        :settings: (dict) provided input data
        :plot: (dict) figures to be generated
        :wkdir: (string) location of project files
    """

    def __init__(self, project_basename, wkdir, settings_dict=None, make_dirs=True):
        """
        Initialise instance of settings.
        """

        make_template_only = True if settings_dict is None else False

        self.settings = FixedOrderedDict()
        self.settings['aircraft'] = None
        self.settings['state'] = None
        self.settings['deformation'] = False
        self.settings['horseshoe_type'] = 2
        self.settings['epsilon'] = 1e-6
        self.settings['_do_normal_rotations'] = True
        self.settings['_deformation_check'] = True
        self.settings['vlm_autopanels_c'] = None
        self.settings['vlm_autopanels_s'] = None
        self.settings['save_results'] = [
            "NO_global",
            "NO_panelwise",
            "NO_loads_with_undeformed_mesh",
            "NO_loads_with_deformed_mesh"
        ]
        self.settings._freeze()

        # SETTINGS -- user-provided visualisation tasks
        self.plot = FixedOrderedDict()
        self.plot['geometry_aircraft'] = False
        self.plot['geometry_wing'] = None
        self.plot['geometry_segment'] = None
        self.plot['geometry_property'] = None
        self.plot['lattice_aircraft'] = False
        self.plot['lattice_aircraft_optional'] = []
        self.plot['lattice_wing'] = None
        self.plot['lattice_segment'] = None
        self.plot['results_downwash'] = False
        self.plot['results_panelwise'] = None
        self.plot['show'] = True
        self.plot['save'] = False
        self.plot._freeze()

        self.aircraft_name = None

        if not make_template_only:
            self.update_from_dict(**settings_dict)
            self.aircraft_name = os.path.splitext(self.settings['aircraft'])[0]

    ####################################################
        self.paths = ProjectPaths(wkdir)
        self.paths.add_path(uid='dir_aircraft', path=DIR_AIRCRAFT)
        self.paths.add_path(uid='dir_airfoils', path=DIR_AIRFOILS)
        self.paths.add_path(uid='dir_deformation', path=DIR_DEFORMATION)
        self.paths.add_path(uid='dir_plots', path=DIR_PLOTS)
        self.paths.add_path(uid='dir_results', path=DIR_RESULTS)
        self.paths.add_path(uid='dir_settings', path=DIR_SETTINGS)
        self.paths.add_path(uid='dir_state', path=DIR_STATE)


#         self.files = {
#                 "aircraft": ,
#                 "deformation": f"{DIR_DEFORMATION}/{self.aircraft_name}.json",
#                 "settings": f"{DIR_SETTINGS}/{self.project_basename}.json",
#                 "state": f"{DIR_STATE}/{self.settings['state']}.json",
#                 "results_global": f"{DIR_RESULTS}/{self.project_basename}_global.json",
#                 "results_panelwise": f"{DIR_RESULTS}/{self.project_basename}_panelwise.json",
#                 "results_apm_global": f"{DIR_RESULTS}/{self.project_basename}_APM.json",
#                 }
    ####################################################

        # Project directories (will be converted to abs. paths when wkdir is set)
        self.dirs = {
                "aircraft": DIR_AIRCRAFT,
                "airfoils": DIR_AIRFOILS,
                "deformation": DIR_DEFORMATION,
                "plots": DIR_PLOTS,
                "results": DIR_RESULTS,
                "settings": DIR_SETTINGS,
                "state": DIR_STATE,
                }

        self.files = {}
        self.project_basename = project_basename
        self.wkdir = wkdir

        self.generate_file_names()
        self.make_abs_paths()

        if make_dirs:
            self.make_project_subdirs()

        if not make_template_only:
            ac_file_extension = os.path.splitext(self.files['aircraft'])[-1].lower()
            if ac_file_extension not in ['.xml', '.json']:
                raise ValueError("Aircraft file must have extension '.json' or '.xml'")

            if ac_file_extension.lower() == '.json':
                self.aircraft_is_cpacs = False
            else:
                self.aircraft_is_cpacs = True

        if make_template_only is False:
            self.check()

    def generate_file_names(self):
        """Generate file names"""

        self.files = {
                "aircraft": f"{DIR_AIRCRAFT}/{self.settings['aircraft']}",
                "deformation": f"{DIR_DEFORMATION}/{self.aircraft_name}.json",
                "settings": f"{DIR_SETTINGS}/{self.project_basename}.json",
                "state": f"{DIR_STATE}/{self.settings['state']}.json",
                "results_global": f"{DIR_RESULTS}/{self.project_basename}_global.json",
                "results_panelwise": f"{DIR_RESULTS}/{self.project_basename}_panelwise.json",
                "results_apm_global": f"{DIR_RESULTS}/{self.project_basename}_APM.json",
                }

    def make_abs_paths(self):
        """Make filepaths absolute"""

        for key, dirname in self.dirs.items():
            subdir = os.path.basename(dirname)
            self.dirs[key] = os.path.join(self.wkdir, subdir)

        for key, filename in self.files.items():
            self.files[key] = os.path.join(self.wkdir, filename)

    def make_project_subdirs(self):
        """Create project subdirectories"""

        for dirpath in self.dirs.values():
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)

    def update_from_dict(self, settings, plot):
        """
        Update settings
        """

        for key, value in settings.items():
            self.settings[key] = value

        for key, value in plot.items():
            self.plot[key] = value

    def clean(self):
        """
        Remove old files in project directory
        """

        dir_keys = ['plots', 'results']

        for dir_key in dir_keys:
            abs_dir = self.dirs[dir_key]
            shutil.rmtree(abs_dir, ignore_errors=True)

    def check(self):
        """Check definition of SETTINGS properties and data"""

        logger.debug("Checking settings...")

        # 2. CHECK INPUTS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
        if self.settings['aircraft'] is None:
            logger.info("'settings.aircraft' is not defined")
        elif not isinstance(self.settings['aircraft'], str):
            raise TypeError("'settings.aircraft' must be a valid STRING")

        if not self.settings['aircraft']:
            raise ValueError("Must provide AIRCRAFT file!")

        if self.settings['state'] is None:
            raise ValueError("must provide CPACS state uID or PyTornado state file!")
        elif not isinstance(self.settings['state'], str):
            raise TypeError("'settings.state' must be valid STRING")

        if not isinstance(self.settings['horseshoe_type'], int) \
                or self.settings['horseshoe_type'] not in [0, 1, 2]:
            raise ValueError("'horseshoe_type' must be of type int (0, 1, 2)")

        if not isinstance(self.settings['epsilon'], float) or \
                not (0 < self.settings['epsilon'] < 1):
            raise ValueError("'epsilon' must be a (small) float in range (0, 1)")

        if not isinstance(self.settings['_do_normal_rotations'], bool):
            raise ValueError("'_do_normal_rotations' must be 'True' or 'False'")
        if not self.settings['_do_normal_rotations']:
            logger.warning("Normal rotations are turned off (no controls and airfoils)")

        if not isinstance(self.settings['_deformation_check'], bool):
            raise ValueError("'_deformation_check' must be 'True' or 'False'")

        # 4. CHECK PLOTS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
        if not self.plot['geometry_aircraft']:
            logger.info("'geometry_aircraft' not defined")
        elif not isinstance(self.plot['geometry_aircraft'], bool):
            raise TypeError("'plot.geometry_aircraft' must be True or False")

        if isinstance(self.plot['geometry_wing'], str):
            self.plot['geometry_wing'] = [self.plot['geometry_wing']]
        if self.plot['geometry_wing'] is None:
            logger.info("'geometry_wing' not defined")
            self.plot['geometry_wing'] = list()
        elif not isinstance(self.plot['geometry_wing'], list):
            raise TypeError("'plot.geometry_wing' must be LIST")
        elif not all(isinstance(v, str) for v in self.plot['geometry_wing']):
            raise TypeError("'plot.geometry_wing' must be LIST of STRING")

        if isinstance(self.plot['geometry_segment'], str):
            self.plot['geometry_segment'] = [self.plot['geometry_segment']]
        if self.plot['geometry_segment'] is None:
            logger.info("'geometry_segment' not defined")
            self.plot['geometry_segment'] = list()
        elif not isinstance(self.plot['geometry_segment'], list):
            raise TypeError("'plot.geometry_segment' must be LIST")
        elif not all(isinstance(v, str) for v in self.plot['geometry_segment']):
            raise TypeError("'plot.geometry_segment' must be LIST of STRING")

        if isinstance(self.plot['geometry_property'], str):
            self.plot['geometry_property'] = [self.plot['geometry_property']]
        if self.plot['geometry_property'] is None:
            logger.info("'geometry_property' not defined")
            self.plot['geometry_property'] = list()
        elif not isinstance(self.plot['geometry_property'], list):
            raise TypeError("'plot.geometry_property' must be LIST")
        elif not all(isinstance(v, str) for v in self.plot['geometry_property']):
            raise TypeError("'plot.geometry_property' must be LIST of STRING")

        if not isinstance(self.plot['lattice_aircraft'], bool):
            raise TypeError("'plot.lattice_aircraft' must be True or False")

        if isinstance(self.plot['lattice_wing'], str):
            self.plot['lattice_wing'] = [self.plot['lattice_wing']]
        if self.plot['lattice_wing'] is None:
            logger.info("'lattice_wing' not defined")
            self.plot['lattice_wing'] = list()
        elif not isinstance(self.plot['lattice_wing'], list):
            raise TypeError("'plot.lattice_wing' must be LIST")
        elif not all(isinstance(v, str) for v in self.plot['lattice_wing']):
            raise TypeError("'plot.lattice_wing' must be LIST of STRING")

        if isinstance(self.plot['lattice_segment'], str):
            self.plot['lattice_segment'] = [self.plot['lattice_segment']]
        if self.plot['lattice_segment'] is None:
            logger.info("'lattice_segment' not defined")
            self.plot['lattice_segment'] = list()
        elif not isinstance(self.plot['lattice_segment'], list):
            raise TypeError("'plot.lattice_segment' must be LIST")
        elif not all(isinstance(v, str) for v in self.plot['lattice_segment']):
            raise TypeError("'plot.lattice_segment' must be LIST of STRING")

        if not isinstance(self.plot['results_downwash'], bool):
            raise TypeError("'plot.results_downwash' must be True or False")

        if isinstance(self.plot['results_panelwise'], str):
            self.plot['results_panelwise'] = [self.plot['results_panelwise']]
        if self.plot['results_panelwise'] is None:
            logger.info("'results_panelwise' not defined")
            self.plot['results_panelwise'] = list()
        elif not isinstance(self.plot['results_panelwise'], list):
            raise TypeError("'plot.results_panelwise' must be LIST")
        elif not all(isinstance(v, str) for v in self.plot['results_panelwise']):
            raise TypeError("'plot.results_panelwise' must be LIST of STRING")

        if not isinstance(self.plot['show'], bool):
            raise TypeError("'plot.show' must be True or False")
        if not isinstance(self.plot['save'], bool):
            raise TypeError("'plot.save' must be True or False")
