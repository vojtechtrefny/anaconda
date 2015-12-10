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

from pyanaconda.ui.gui.spokes import NormalSpoke
from pyanaconda.ui.categories.system import SystemCategory
from pyanaconda.i18n import N_

# export only the spoke, no helper functions, classes or constants
__all__ = ["BlivetGuiSpoke"]

class BlivetGuiSpoke(NormalSpoke):
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

        NormalSpoke.__init__(self, data, storage, payload, instclass)

    def initialize(self):
        """
        The initialize method that is called after the instance is created.
        The difference between __init__ and this method is that this may take
        a long time and thus could be called in a separated thread.

        :see: pyanaconda.ui.common.UIObject.initialize

        """

        NormalSpoke.initialize(self)
        # TODO: load and embed blivet-gui here

    def refresh(self):
        """
        The refresh method that is called every time the spoke is displayed.
        It should update the UI elements according to the contents of
        self.data.

        :see: pyanaconda.ui.common.UIObject.refresh

        """

        pass

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

    ### handlers ###
    def on_back_clicked(self, button):
        # TODO: any checks needed here?
        NormalSpoke.on_back_clicked(self, button)
