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

logger = logging.getLogger(__name__)

# ===== Directories =====
# Input directories
DIR_AIRCRAFT = 'aircraft'
DIR_AIRFOILS = 'airfoils'
DIR_DEFORMATION = 'deformation'
DIR_SETTINGS = 'settings'
DIR_STATE = 'state'
# Output directories
DIR_PLOTS = '_plots'
DIR_RESULTS = '_results'
# Template directory name
DIR_TEMPLATE_WKDIR = 'pytornado'

#############################################################################

from collections import defaultdict
from pathlib import Path, PurePath
import os
import shutil
import string


class ProjectPaths:

    UID_ROOT = 'root'
    FORMATTER_COUNTER = 'counter'

    def __init__(self, root_dir):
        """
        Class providing tools for filepath handling

        This class automatically converts filepaths into absolute paths,
        which helps to avoid change directories during runtime of a script.

        Paths stored and returned in this class are based on the 'Path()'
        object from the pathlib standard library, see also:

            * https://docs.python.org/3/library/pathlib.html

        Args:
            :root_dir: Project root directory (as abs. or rel. path)

        The 'root_dir' is the project root directory. All other other added
        to this class are assumed to reside inside the 'root_dir'. In other
        words, absolute file paths are assembled based on the 'root_dir'.

        Attributes:
            :_counter: Index to create numbered paths
            :_abs_paths: Dictionary with absolute paths
            :groups: Dictionary with grouped file UIDs
        """

        self._counter = 0
        self._abs_paths = {}
        self._groups = defaultdict(list)

        self._set_root_dir(root_dir)

    def __call__(self, uid, make_dirs=False, is_dir=False):
        """
        Return a path for given UID

        Args:
            :uid: Unique identifier for the path
        """

        path = self._format_path(uid)

        if make_dirs:
            parent_dirs = path if is_dir else path.parent
            parent_dirs.mkdir(parents=True, exist_ok=True)

        return path

    def _set_root_dir(self, root_dir):
        """
        Set the project root directory (rel. path will be converted to abs.)

        Args:
            :root_dir: Project root directory
        """

        self._abs_paths[self.UID_ROOT] = Path(root_dir).resolve()

    @property
    def root(self):
        """Return the Path() object for the project root directory"""

        return self.__call__(self.UID_ROOT)

    @property
    def counter(self):
        return self._counter

    @counter.setter
    def counter(self, counter):
        if not isinstance(counter, int):
            raise ValueError("Counter must be of type 'int'")

        self._counter = counter

    def add_path(self, uid, path, uid_groups=None, is_absolute=False):
        """
        Add a path

        Args:
            :uid: Unique identifier for the path
            :path: Path string or Path() object
            :uid_groups: Optional UID(s) to identify files by groups
            :is_absolute: Flag indicating if given 'path' is absolute
        """

        if uid in self._abs_paths.keys():
            raise ValueError(f"UID '{uid}' already used")

        path = Path(path)

        if not is_absolute:
            path = self.__class__.join_paths(self.root, path)

        self._abs_paths[uid] = path

        # ----- Group bookkeeping -----
        if uid_groups is not None:
            if not isinstance(uid_groups, (str, list, tuple)):
                raise TypeError(f"'uid_groups' must be of type (str, list, tuple)")

            if isinstance(uid_groups, str):
                uid_groups = (uid_groups,)

            for uid_group in uid_groups:
                self._groups[uid_group].append(uid)

    def add_subpath(self, uid_parent, uid, path, uid_groups=None):
        """
        Add a child path to an existing parent path

        Args:
            :uid_parent: UID of the parent directory
            :uid: UID of the new path
            :path: relative path to add
            :uid_groups: Optional UID(s) to identify files by groups
        """

        if uid_parent not in self._abs_paths.keys():
            raise ValueError(f"Parent UID '{uid_parent}' not found")

        parent_path = self._abs_paths[uid_parent]
        assembled_path = self.__class__.join_paths(parent_path, path)
        self.add_path(uid, assembled_path, uid_groups)

    def _format_path(self, uid):
        """
        TODO: UPDATE docstring

        Run a string format() method on a path and return new path

        Args:
            :uid: Unique identifier

        All other standard arguments and keyword arguments are forwarded to the
        format() method of 'str'
        """

        if uid not in self._abs_paths.keys():
            raise ValueError(f"UID '{uid}' not found")

        formatted_path = str(self._abs_paths[uid])
        # formatted_path = str(self._abs_paths[uid]).format(*args, **kwargs)

        ##### TODO: IMPROVE!!! ####
        # - Make more general
        formatters = [f for (_, f, _, _) in string.Formatter().parse(formatted_path)]
        if self.FORMATTER_COUNTER in formatters:
            formatted_path = formatted_path.format(counter=self.counter)
        ###########################

        return Path(formatted_path)

    @staticmethod
    def join_paths(path1, path2):
        """
        Join two paths

        Args:
            :path1: Leading path
            :path2: Trailing path
        """

        path = PurePath(path1).joinpath(path2)
        return Path(path)

    def iter_group_paths(self, uid_groups, make_dirs=False, is_dir=False):
        """
        Return a generator with paths belong to group with given UID

        Args:
            :uid_groups: Optional UID(s) to identify files by groups
        """

        if not isinstance(uid_groups, (str, list, tuple)):
            raise TypeError(f"'uid_groups' must be of type (str, list, tuple)")

        if isinstance(uid_groups, str):
            uid_groups = (uid_groups,)


        for uid_group in uid_groups:
            for uid in self._groups[uid_group]:
                yield self.__call__(uid, make_dirs=make_dirs, is_dir=is_dir)

    def make_dirs_for_groups(self, uid_groups, is_dir=True):
        """
        Create directories for all paths belonging to specified group(s)

        Args:
            :uid_groups: Optional UID(s) to identify files by groups
        """

        for _ in self.iter_group_paths(uid_groups, make_dirs=True, is_dir=is_dir):
            pass

    def rm_dirs_for_groups(self, uid_groups):
        """
        TODO

        Args:
            :uid_groups: Optional UID(s) to identify files by groups
        """

        for path in self.iter_group_paths(uid_groups):
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            else:
                ############## TODO : better
                # - ignore_errors etc...
                try:
                    os.remove(path)
                except:
                    pass

#############################################################################


class Settings:

    def __init__(self, settings_filename, project_dir, *,
                 settings_dict=None, make_dirs=True, check_ac_file_type=True):
        """
        Data structure with PyTornado execution settings

        Attributes:
            :settings_filename: Name of the settings file
            :project_dir: PyTornado project directory (where all data is expected)
            :settings_dict: Basic settings data as a dictionary
            :make_dirs: (bool) Flag for creation of project directories
        """

        self.project_dir = Path(project_dir).resolve()
        self.project_basename = os.path.splitext(settings_filename)[0]

        self.settings = {}
        self.settings['aircraft'] = None
        self.settings['state'] = None
        self.settings['deformation'] = None
        self.settings['vlm_autopanels_c'] = None
        self.settings['vlm_autopanels_s'] = None
        self.settings['save_results'] = [
            "NO_global",
            "NO_panelwise",
            "NO_loads_with_undeformed_mesh",
            "NO_loads_with_deformed_mesh"
        ]
        # Underscore settings are "hidden" settings that generally shouldn't be changed
        self.settings['_do_normal_rotations'] = True
        self.settings['_deformation_check'] = True
        self.settings['_horseshoe_type'] = 2
        self.settings['_epsilon'] = 1e-6

        self.plot = {}
        self.plot['geometry_aircraft'] = False
        self.plot['geometry_wing'] = []
        self.plot['geometry_segment'] = []
        self.plot['geometry_property'] = []
        self.plot['lattice_aircraft'] = False
        self.plot['lattice_aircraft_optional'] = []
        self.plot['lattice_wing'] = []
        self.plot['lattice_segment'] = []
        self.plot['results_downwash'] = False
        self.plot['results_panelwise'] = []
        self.plot['show'] = True
        self.plot['save'] = False

        if settings_dict is not None:
            self.update_from_dict(**settings_dict)

        self.paths = None
        self.generate_paths()

        self.aircraft_is_cpacs = None
        if check_ac_file_type:
            self.check_aircraft_file_type()

        if make_dirs:
            self.paths.make_dirs_for_groups('dir')

    def generate_paths(self):
        """
        Initialise the file structure
        """

        # Output subdirectory to structure results from APM analyses
        output_subdir = f"/{self.project_basename}" + "_{counter:03d}"

        # ===== Directories =====
        self.paths = ProjectPaths(self.project_dir)
        self.paths.add_path(uid='d_aircraft', path=DIR_AIRCRAFT, uid_groups='dir')
        self.paths.add_path(uid='d_airfoils', path=DIR_AIRFOILS, uid_groups='dir')
        self.paths.add_path(uid='d_deformation', path=DIR_DEFORMATION, uid_groups='dir')
        self.paths.add_path(uid='d_settings', path=DIR_SETTINGS, uid_groups='dir')
        self.paths.add_path(uid='d_state', path=DIR_STATE, uid_groups='dir')
        # Output directories
        self.paths.add_path(uid='d_plots_TOP', path=DIR_PLOTS, uid_groups=('dir', 'tmp'))
        self.paths.add_path(uid='d_results_TOP', path=DIR_RESULTS, uid_groups=('dir', 'tmp'))
        self.paths.add_path(uid='d_plots', path=DIR_PLOTS+output_subdir, uid_groups=('dir', 'tmp'))
        self.paths.add_path(uid='d_results', path=DIR_RESULTS+output_subdir, uid_groups=('dir', 'tmp'))

        # ===== Files =====
        self.paths.add_subpath(uid_parent='d_aircraft', uid='f_aircraft', path=f"{self.settings['aircraft']}")
        self.paths.add_subpath(uid_parent='d_deformation', uid='f_deformation', path=f"{self.settings['deformation']}")
        self.paths.add_subpath(uid_parent='d_settings', uid='f_settings', path=f"{self.project_basename}.json")
        self.paths.add_subpath(uid_parent='d_state', uid='f_state', path=f"{self.settings['state']}")
        # Output files
        self.paths.add_subpath(uid_parent='d_results', uid='f_results_global', path=f"{self.project_basename}_global.json")
        self.paths.add_subpath(uid_parent='d_results', uid='f_results_panelwise', path=f"{self.project_basename}_global.json")
        self.paths.add_subpath(uid_parent='d_results', uid='f_results_apm_global', path=f"{self.project_basename}_APM.json")

    def check_aircraft_file_type(self):
        """Check whether aircraft is a CPACS or a JSON file"""

        ac_file_extension = self.paths('f_aircraft').suffix.lower()

        if ac_file_extension not in ['.xml', '.json']:
            raise ValueError("Aircraft file must have extension '.json' or '.xml' (CPACS)")

        if ac_file_extension == '.json':
            self.aircraft_is_cpacs = False
        else:
            self.aircraft_is_cpacs = True

    def update_from_dict(self, settings, plot):
        """
        Update settings from dictionary structures

        Args:
            :settings: Dictionary with general settings
            :plot: Dictionary with plot settings
        """

        for key, value in settings.items():
            self.settings[key] = value

        for key, value in plot.items():
            self.plot[key] = value

    def clean(self):
        """
        Remove old files in project directory
        """

        self.paths.rm_dirs_for_groups('tmp')

###################################################

    # def check(self):
    #     """Check definition of SETTINGS properties and data"""

    #     logger.debug("Checking settings...")

    #     # 2. CHECK INPUTS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    #     if self.settings['aircraft'] is None:
    #         logger.info("'settings.aircraft' is not defined")
    #     elif not isinstance(self.settings['aircraft'], str):
    #         raise TypeError("'settings.aircraft' must be a valid STRING")

    #     if not self.settings['aircraft']:
    #         raise ValueError("Must provide AIRCRAFT file!")

    #     if self.settings['state'] is None:
    #         raise ValueError("must provide CPACS state uID or PyTornado state file!")
    #     elif not isinstance(self.settings['state'], str):
    #         raise TypeError("'settings.state' must be valid STRING")

    #     if not isinstance(self.settings['horseshoe_type'], int) \
    #             or self.settings['horseshoe_type'] not in [0, 1, 2]:
    #         raise ValueError("'horseshoe_type' must be of type int (0, 1, 2)")

    #     if not isinstance(self.settings['epsilon'], float) or \
    #             not (0 < self.settings['epsilon'] < 1):
    #         raise ValueError("'epsilon' must be a (small) float in range (0, 1)")

    #     if not isinstance(self.settings['_do_normal_rotations'], bool):
    #         raise ValueError("'_do_normal_rotations' must be 'True' or 'False'")
    #     if not self.settings['_do_normal_rotations']:
    #         logger.warning("Normal rotations are turned off (no controls and airfoils)")

    #     if not isinstance(self.settings['_deformation_check'], bool):
    #         raise ValueError("'_deformation_check' must be 'True' or 'False'")

    #     # 4. CHECK PLOTS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    #     if not self.plot['geometry_aircraft']:
    #         logger.info("'geometry_aircraft' not defined")
    #     elif not isinstance(self.plot['geometry_aircraft'], bool):
    #         raise TypeError("'plot.geometry_aircraft' must be True or False")

    #     if isinstance(self.plot['geometry_wing'], str):
    #         self.plot['geometry_wing'] = [self.plot['geometry_wing']]
    #     if self.plot['geometry_wing'] is None:
    #         logger.info("'geometry_wing' not defined")
    #         self.plot['geometry_wing'] = list()
    #     elif not isinstance(self.plot['geometry_wing'], list):
    #         raise TypeError("'plot.geometry_wing' must be LIST")
    #     elif not all(isinstance(v, str) for v in self.plot['geometry_wing']):
    #         raise TypeError("'plot.geometry_wing' must be LIST of STRING")

    #     if isinstance(self.plot['geometry_segment'], str):
    #         self.plot['geometry_segment'] = [self.plot['geometry_segment']]
    #     if self.plot['geometry_segment'] is None:
    #         logger.info("'geometry_segment' not defined")
    #         self.plot['geometry_segment'] = list()
    #     elif not isinstance(self.plot['geometry_segment'], list):
    #         raise TypeError("'plot.geometry_segment' must be LIST")
    #     elif not all(isinstance(v, str) for v in self.plot['geometry_segment']):
    #         raise TypeError("'plot.geometry_segment' must be LIST of STRING")

    #     if isinstance(self.plot['geometry_property'], str):
    #         self.plot['geometry_property'] = [self.plot['geometry_property']]
    #     if self.plot['geometry_property'] is None:
    #         logger.info("'geometry_property' not defined")
    #         self.plot['geometry_property'] = list()
    #     elif not isinstance(self.plot['geometry_property'], list):
    #         raise TypeError("'plot.geometry_property' must be LIST")
    #     elif not all(isinstance(v, str) for v in self.plot['geometry_property']):
    #         raise TypeError("'plot.geometry_property' must be LIST of STRING")

    #     if not isinstance(self.plot['lattice_aircraft'], bool):
    #         raise TypeError("'plot.lattice_aircraft' must be True or False")

    #     if isinstance(self.plot['lattice_wing'], str):
    #         self.plot['lattice_wing'] = [self.plot['lattice_wing']]
    #     if self.plot['lattice_wing'] is None:
    #         logger.info("'lattice_wing' not defined")
    #         self.plot['lattice_wing'] = list()
    #     elif not isinstance(self.plot['lattice_wing'], list):
    #         raise TypeError("'plot.lattice_wing' must be LIST")
    #     elif not all(isinstance(v, str) for v in self.plot['lattice_wing']):
    #         raise TypeError("'plot.lattice_wing' must be LIST of STRING")

    #     if isinstance(self.plot['lattice_segment'], str):
    #         self.plot['lattice_segment'] = [self.plot['lattice_segment']]
    #     if self.plot['lattice_segment'] is None:
    #         logger.info("'lattice_segment' not defined")
    #         self.plot['lattice_segment'] = list()
    #     elif not isinstance(self.plot['lattice_segment'], list):
    #         raise TypeError("'plot.lattice_segment' must be LIST")
    #     elif not all(isinstance(v, str) for v in self.plot['lattice_segment']):
    #         raise TypeError("'plot.lattice_segment' must be LIST of STRING")

    #     if not isinstance(self.plot['results_downwash'], bool):
    #         raise TypeError("'plot.results_downwash' must be True or False")

    #     if isinstance(self.plot['results_panelwise'], str):
    #         self.plot['results_panelwise'] = [self.plot['results_panelwise']]
    #     if self.plot['results_panelwise'] is None:
    #         logger.info("'results_panelwise' not defined")
    #         self.plot['results_panelwise'] = list()
    #     elif not isinstance(self.plot['results_panelwise'], list):
    #         raise TypeError("'plot.results_panelwise' must be LIST")
    #     elif not all(isinstance(v, str) for v in self.plot['results_panelwise']):
    #         raise TypeError("'plot.results_panelwise' must be LIST of STRING")

    #     if not isinstance(self.plot['show'], bool):
    #         raise TypeError("'plot.show' must be True or False")
    #     if not isinstance(self.plot['save'], bool):
    #         raise TypeError("'plot.save' must be True or False")
