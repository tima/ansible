# Copyright 2012, Dag Wieers <dag@wieers.com>
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
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.action import ActionBase
# import galaxy

class ActionModule(ActionBase):
    ''' Print statements during execution '''

    TRANSFERS_FILES = False
    VALID_ARGS = set(['role_file', 'path', 'state', 'no_dependencies'])
    VALID_STATE = set(['present', 'latest'])

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        for arg in self._task.args:
            if arg not in self.VALID_ARGS:
                return {"failed": True, "msg": "'%s' is not a valid option in galaxy_install" % arg}

        #roles_file = self._task.args.get("role_file", os.getcwd() + "/roles/requirements.yml")
        #roles_path = self._task.args.get("path", os.getcwd() + "/roles")
        #state = self._task.args.get("state", "present")
        #no_dependencies = self._task.args.get("no_dependencies", False)
        
        #galaxy = Galaxy(self.options)

        #if 'msg' in self._task.args and 'var' in self._task.args:
        #    return {"failed": True, "msg": "'msg' and 'var' are incompatible options"}

        result = super(ActionModule, self).run(tmp, task_vars)


        return result
