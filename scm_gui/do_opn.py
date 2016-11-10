### -*- coding: utf-8 -*-
###
###  Copyright (C) 2016 Peter Williams <pwil3058@gmail.com>
###
### This program is free software; you can redistribute it and/or modify
### it under the terms of the GNU General Public License as published by
### the Free Software Foundation; version 2 of the License only.
###
### This program is distributed in the hope that it will be useful,
### but WITHOUT ANY WARRANTY; without even the implied warranty of
### MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
### GNU General Public License for more details.
###
### You should have received a copy of the GNU General Public License
### along with this program; if not, write to the Free Software
### Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import os

from gi.repository import Gtk

from .. import wsm_icons

from ..scm_gui import scm_gui_ifce
from ..scm_gui import scm_wspce

# NB: this relies on dialogue.ClientMixin or equivalent also bein "mixed in"
class DoOpnMixin:
    def scm_choose_backend(self):
        available_backends = scm_gui_ifce.avail_backends()
        if len(available_backends) == 0:
            self.inform_user(scm_gui_ifce.backend_requirements())
            return None
        elif len(available_backends) == 1:
            return available_backends[0]
        from ..gtx import dialogue
        return self.choose_from_list(alist=available_backends, prompt=_("Choose SCM back end:"))
    def scm_do_create_new_wspce(self):
        req_backend = self.scm_choose_backend()
        if not req_backend:
            return
        new_pgnd_path = self.ask_dir_path(_("New Workspace Directory Path:"))
        if new_pgnd_path is not None:
            result = scm_gui_ifce.create_new_playground(new_pgnd_path, req_backend)
            self.report_any_problems(result)
            if not result.is_ok:
                return
            result = scm_wspce.chdir(new_pgnd_path)
            self.report_any_problems(result)
    def scm_do_initialize_curdir(self):
        req_backend = self.scm_choose_backend()
        if not req_backend:
            return
        result = scm_gui_ifce.init_current_dir(req_backend)
        self.report_any_problems(result)
    def scm_do_clone_repo(self):
        # TODO: think about doing most of scm_clone_repo() in scm_repos
        req_backend = self.scm_choose_backend()
        if not req_backend:
            return
        from ..scm_gui import scm_repos
        clone_dialog = scm_repos.RepoSelectDialog(self.get_toplevel())
        if clone_dialog.run() == Gtk.ResponseType.OK:
            cloned_path = clone_dialog.get_path()
            if not cloned_path:
                clone_dialog.destroy()
                return
            target = os.path.expanduser(clone_dialog.get_target())
            with clone_dialog.showing_busy():
                result = scm_gui_ifce.clone_repo_as(cloned_path, target, req_backend)
                if result.is_less_than_error:
                    scm_repos.add_repo_path(cloned_path)
            clone_dialog.report_any_problems(result)
            if os.path.isdir(target):
                with clone_dialog.showing_busy():
                    result = scm_wspce.chdir(target)
                clone_dialog.report_any_problems(result)
            clone_dialog.destroy()
        else:
            clone_dialog.destroy()
    def scm_do_pull_from_default_repo(self):
        with self.showing_busy():
            result = scm_gui_ifce.SCM.do_pull_from_repo(None)
        self.report_any_problems(result)
    def scm_do_push_to_default_repo(self):
        with self.showing_busy():
            result = scm_gui_ifce.SCM.do_push_to_repo(None)
        self.report_any_problems(result)
    def populate_action_groups(self):
        from ..gtx.actions import AC_DONT_CARE
        from .scm_actions import AC_NOT_IN_SCM_PGND, AC_IN_SCM_PGND
        self.action_groups[AC_DONT_CARE].add_actions(
            [
                ("scm_create_new_workspace", wsm_icons.STOCK_NEW_WORKSPACE, _("New"), "",
                 _("Create a new intitialized workspace"),
                 lambda _action=None: self.scm_do_create_new_wspce()
                ),
            ])
        self.action_groups[AC_NOT_IN_SCM_PGND].add_actions(
            [
                ("scm_initialize_curdir", wsm_icons.STOCK_INIT, _("Initialise"), "",
                 _("Initialise the current working directory"),
                 lambda _action=None: self.scm_do_initialize_curdir()
                ),
                ("scm_clone_repo", wsm_icons.STOCK_CLONE, _("Clone"), None,
                 _("Clone an existing repository."),
                 lambda _action=None: self.scm_do_clone_repo()
                ),
            ])
        self.action_groups[AC_IN_SCM_PGND].add_actions(
            [
                ("scm_pull_from_default_repo", wsm_icons.STOCK_PULL, _("Pull"), None,
                 _("Pull from the default remote repository"),
                 lambda _action=None: self.scm_do_pull_from_default_repo()
                ),
                ("scm_push_to_default_repo", wsm_icons.STOCK_PUSH, _("Push"), None,
                 _("Push to the default remote repository"),
                 lambda _action=None: self.scm_do_push_to_default_repo()
                ),
            ])
