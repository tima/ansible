########################################################################
#
# (C) 2015, Brian Coca <bcoca@ansible.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
########################################################################
''' This manages remote shared Ansible objects, mainly roles'''

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import yaml

from ansible.compat.six import string_types

from ansible.errors import AnsibleError
from ansible.galaxy.role import GalaxyRole
from ansible.playbook.role.requirement import RoleRequirement

#      default_readme_template
#      default_meta_template


class Galaxy(object):
    ''' Keeps global galaxy info '''

    def __init__(self, options):

        self.options = options
        # self.options.roles_path needs to be a list and will be by default
        roles_path = getattr(self.options, 'roles_path', [])
        # cli option handling is responsible for making roles_path a list
        self.roles_paths = roles_path

        self.roles =  {}

        # load data path for resource usage
        this_dir, this_filename = os.path.split(__file__)
        self.DATA_PATH = os.path.join(this_dir, "data")

        self._default_readme = None
        self._default_meta = None
        self._default_test = None
        self._default_travis = None

    @property
    def default_readme(self):
        if self._default_readme is None:
            self._default_readme = self._str_from_data_file('readme')
        return self._default_readme

    @property
    def default_meta(self):
        if self._default_meta is None:
            self._default_meta = self._str_from_data_file('metadata_template.j2')
        return self._default_meta

    @property
    def default_test(self):
        if self._default_test is None:
            self._default_test = self._str_from_data_file('test_playbook.j2')
        return self._default_test

    @property
    def default_travis(self):
        if self._default_travis is None:
            self._default_travis = self._str_from_data_file('travis.j2')
        return self._default_travis

    def add_role(self, role):
        self.roles[role.name] = role

    def remove_role(self, role_name):
        del self.roles[role_name]

    def _str_from_data_file(self, filename):
        myfile = os.path.join(self.DATA_PATH, filename)
        try:
            return open(myfile).read()
        except Exception as e:
            raise AnsibleError("Could not open %s: %s" % (filename, str(e)))

    def read_role_file(self, role_file=None, display=None):
        roles_left = []
        if role_file is None:
            role_file = self._find_role_file()
        try:
            f = open(role_file, 'r')
            if role_file.endswith('.yaml') or role_file.endswith('.yml'):
                try:
                    required_roles =  yaml.safe_load(f.read())
                except Exception as e:
                    raise AnsibleError("Unable to load data from the requirements file: %s" % role_file)

                if required_roles is None:
                    raise AnsibleError("No roles found in file: %s" % role_file)

                for role in required_roles:
                    if "include" not in role:
                        role = RoleRequirement.role_yaml_parse(role)
                        if display is not None:
                            display.vvv("found role %s in yaml file" % str(role))
                        if "name" not in role and "scm" not in role:
                            raise AnsibleError("Must specify name or src for role")
                        roles_left.append(GalaxyRole(self, **role))
                    else:
                        with open(role["include"]) as f_include:
                            try:
                                roles_left += [
                                    GalaxyRole(self, **r) for r in
                                    map(RoleRequirement.role_yaml_parse,
                                        yaml.safe_load(f_include))
                                ]
                            except Exception as e:
                                msg = "Unable to load data from the include requirements file: %s %s"
                                raise AnsibleError(msg % (role_file, e))
            else:
                # display.deprecated("going forward only the yaml format will be supported")
                # roles listed in a file, one per line
                for rline in f.readlines():
                    if rline.startswith("#") or rline.strip() == '':
                        continue
                    if display is not None:
                        display.debug('found role %s in text file' % str(rline))
                    role = RoleRequirement.role_yaml_parse(rline.strip())
                    roles_left.append(GalaxyRole(self, **role))
            f.close()
        except (IOError, OSError) as e:
            if display is not None:
                display.error('Unable to open %s: %s' % (role_file, str(e)))
            raise AnsibleError('Unable to open %s: %s' % (role_file, str(e)))
        return roles_left

    def _find_role_file(self):
        role_file_paths = [ # Order?
            os.getcwd() + "/requirements.yml",
            os.getcwd() + "/requirements.yaml",
            os.getcwd() + "/roles/requirements.yml",
            os.getcwd() + "/roles/requirements.yaml"
        ]
        for path in role_file_path:
            if os.path.exists(path):
                return path
        raise AnsibleError('Role file could not be found')
