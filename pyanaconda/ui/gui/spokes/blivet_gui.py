#
# Copyright (C) 2015  Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# the GNU General Public License v.2, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY expressed or implied, including the implied warranties of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.  You should have received a copy of the
# GNU General Public License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.  Any Red Hat trademarks that are incorporated in the
# source code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission of
# Red Hat, Inc.
#
# Red Hat Author(s): Vratislav Podzimek <vpodzime@redhat.com>
#

"""Module with the BlivetGuiSpoke class."""

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

from pyanaconda.ui.gui.spokes import NormalSpoke
from pyanaconda.ui.helpers import StorageChecker
from pyanaconda.ui.categories.system import SystemCategory
from pyanaconda.ui.gui.spokes.lib.summary import ActionSummaryDialog
from pyanaconda.i18n import _, N_, CP_, C_
from pyanaconda import isys
from pyanaconda.bootloader import BootLoaderError

from blivetgui import osinstall

import logging
log = logging.getLogger("anaconda")

# export only the spoke, no helper functions, classes or constants
__all__ = ["BlivetGuiSpoke"]

class BlivetGuiSpoke(NormalSpoke, StorageChecker):
    ### class attributes defined by API ###

    # list all top-level objects from the .glade file that should be exposed
    # to the spoke or leave empty to extract everything
    builderObjects = ["blivetGuiSpokeWindow"]

    # the name of the main window widget
    mainWidgetName = "blivetGuiSpokeWindow"

    # name of the .glade file in the same directory as this source
    uiFile = "blivet_gui.glade"

    # category this spoke belongs to
    category = SystemCategory

    # title of the spoke (will be displayed on the hub)
    title = N_("_BLIVET-GUI PARTITIONING")

    helpFile = "BlivetGuiSpoke.xml"

    ### methods defined by API ###
    def __init__(self, data, storage, payload, instclass):
        """
        :see: pyanaconda.ui.common.Spoke.__init__
        :param data: data object passed to every spoke to load/store data
                     from/to it
        :type data: pykickstart.base.BaseHandler
        :param storage: object storing storage-related information
                        (disks, partitioning, bootloader, etc.)
        :type storage: blivet.Blivet
        :param payload: object storing packaging-related information
        :type payload: pyanaconda.packaging.Payload
        :param instclass: distribution-specific information
        :type instclass: pyanaconda.installclass.BaseInstallClass

        """

        self._error = None
        self._back_already_clicked = False
        self._storage_playground = None

        StorageChecker.__init__(self, min_ram=isys.MIN_GUI_RAM)
        NormalSpoke.__init__(self, data, storage, payload, instclass)

    def initialize(self):
        """
        The initialize method that is called after the instance is created.
        The difference between __init__ and this method is that this may take
        a long time and thus could be called in a separated thread.

        :see: pyanaconda.ui.common.UIObject.initialize

        """

        NormalSpoke.initialize(self)

        self._storage_playground = None

        # FIXME: do not use self.storage -- make copy in refresh and use it
        self.client = osinstall.BlivetGUIAnacondaClient()
        box = self.builder.get_object("BlivetGuiViewport")

        self.blivetgui = osinstall.BlivetGUIAnaconda(self.client, self, box)


    def refresh(self):
        """
        The refresh method that is called every time the spoke is displayed.
        It should update the UI elements according to the contents of
        self.data.

        :see: pyanaconda.ui.common.UIObject.refresh

        """

        self._back_already_clicked = False

        self._storage_playground = self.storage.copy()
        self.client.initialize(self._storage_playground)
        self.blivetgui.initialize()

    def apply(self):
        """
        The apply method that is called when the spoke is left. It should
        update the contents of self.data with values set in the GUI elements.

        """

        pass

    def execute(self):
        """
        The excecute method that is called when the spoke is left. It is
        supposed to do all changes to the runtime environment according to
        the values set in the GUI elements.

        """

        # nothing to do here
        pass

    @property
    def indirect(self):
        return True

    # This spoke has no status since it's not in a hub
    @property
    def status(self):
        return None

    def clear_errors(self):
        self._error = None
        self.clear_info()

    def _do_check(self):
        self.clear_errors()
        StorageChecker.errors = []
        StorageChecker.warnings = []

        # We can't overwrite the main Storage instance because all the other
        # spokes have references to it that would get invalidated, but we can
        # achieve the same effect by updating/replacing a few key attributes.
        self.storage.devicetree._devices = self._storage_playground.devicetree._devices
        self.storage.devicetree._actions = self._storage_playground.devicetree._actions
        self.storage.devicetree._hidden = self._storage_playground.devicetree._hidden
        self.storage.devicetree.names = self._storage_playground.devicetree.names
        self.storage.roots = self._storage_playground.roots

        # set up bootloader and check the configuration
        try:
            self.storage.set_up_bootloader()
        except BootLoaderError as e:
            log.error("storage configuration failed: %s", e)
            StorageChecker.errors = str(e).split("\n")
            self.data.bootloader.bootDrive = ""

        StorageChecker.checkStorage(self)

        if self.errors:
            self.set_warning(_("Error checking storage configuration.  <a href=\"\">Click for details</a> or press Done again to continue."))
        elif self.warnings:
            self.set_warning(_("Warning checking storage configuration.  <a href=\"\">Click for details</a> or press Done again to continue."))

        # on_info_bar_clicked requires self._error to be set, so set it to the
        # list of all errors and warnings that storage checking found.
        self._error = "\n".join(self.errors + self.warnings)

        return self._error == ""

    ### handlers ###
    def on_info_bar_clicked(self, *args):
        log.debug("info bar clicked: %s (%s)", self._error, args)
        if not self._error:
            return

        dlg = Gtk.MessageDialog(flags=Gtk.DialogFlags.MODAL,
                                message_type=Gtk.MessageType.ERROR,
                                buttons=Gtk.ButtonsType.CLOSE,
                                message_format=str(self._error))
        dlg.set_decorated(False)

        with self.main_window.enlightbox(dlg):
            dlg.run()
            dlg.destroy()

    def on_back_clicked(self, button):
        # Clear any existing errors
        self.clear_errors()

        # And then display the summary screen.  From there, the user will either
        # head back to the hub, or stay on the custom screen.
        self._storage_playground.devicetree.actions.prune()
        self._storage_playground.devicetree.actions.sort()

        # If back has been clicked on once already and no other changes made on the screen,
        # run the storage check now.  This handles displaying any errors in the info bar.
        if not self._back_already_clicked:
            self._back_already_clicked = True

            # If we hit any errors while saving things above, stop and let the
            # user think about what they have done
            if self._error is not None:
                return

            if not self._do_check():
                return

        if len(self._storage_playground.devicetree.actions.find()) > 0:
            dialog = ActionSummaryDialog(self.data)
            dialog.refresh(self._storage_playground.devicetree.actions.find())
            with self.main_window.enlightbox(dialog.window):
                rc = dialog.run()

            if rc != 1:
                # Cancel.  Stay on the custom screen.
                return

        NormalSpoke.on_back_clicked(self, button)
