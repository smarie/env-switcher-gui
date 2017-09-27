import sys

import os
from typing import Dict, List
from warnings import warn

from PyQt5.QtCore import pyqtSignal, QObject, QFileInfo, QSettings
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QAbstractButton, QDialogButtonBox, QWidget, \
    QGridLayout, QFormLayout, QLabel, QLineEdit, QErrorMessage, QMessageBox

from copy import deepcopy

from envswitch.env_config import GlobalEnvsConfig
from envswitch.qt_design import Ui_MainWindow


import pkg_resources  # part of setuptools
_app_version = pkg_resources.require("envswitch")[0].version


class CouldNotRestoreStateException(Exception):
    """ Raised whenever the current state can not be restored from persistence layer. """


class CouldNotSaveCurrentConfigurationException(Exception):
    """ Raised whenever the current configuration cannot be saved """


class DirtyStateException(Exception):
    """ Raised whenever an action is attempted that is not allowed for a dirty state. You should save the current
    configuration first"""


class Communicate(QObject):
    """
    see http://pyqt.sourceforge.net/Docs/PyQt5/signals_slots.html#PyQt5.QtCore.pyqtSignal : we have to create an
    independent class

    We define two signals here
    * slot_current_configuration_changed_or_saved that will be triggered whenever the current configuration is modified
    (for example, the user edits the form), or is saved.
    * slot_current_file_changed that will be triggered whenever the current opened file changes (a new file is opened
    for example).
    """
    current_configuration_changed_or_saved = pyqtSignal(QObject)  # the arg is the cause
    current_file_changed = pyqtSignal(QFileInfo)


# MVC in https://openclassrooms.com/courses/programmez-avec-le-langage-c/l-architecture-mvc-avec-les-widgets-complexes
class EnvSwitcherState:  # (QAbstractListModel):  QStandardItemModel
    """
    The Model(s) in the MVC pattern.

    The state of the application is composed of several things:
    * self.current_config_file: the path to the currently open configuration file. It can't be None and always
    represents a valid file
    * self.current_configuration: the currently loaded configuration. It is the same than the one in the file if
    self.is_dirty = False
    * self.is_dirty: True if the current configuration has some modifications that are yet not saved.

    This object is able to return a Qt Model for all aspects of the state.
    """

    def __init__(self, configuration_file_path: str):
        """
        Loads a state from the given 'current configuration' file path.
        Note that you cant create a state if you don't have a valid configuration file :)

        :param configuration_file_path: the path of the configuration file to open.
        """
        # channel to communicate that the current configuration has changed or the file has changed
        self.comm_qt = Communicate()

        # init the fields so that the IDE knows them :)
        self.current_configuration = None
        self.current_configuration_bak = None

        # Load the configuration at the given path (see property setter)
        self.current_config_file = configuration_file_path

    @property
    def current_config_file(self):
        return self._current_config_file

    # noinspection PyUnresolvedReferences
    @current_config_file.setter
    def current_config_file(self, new_conf_file_path):
        """
        Opens a new configuration file at `path new_conf_file_path`, and sets the field to that path.

        If the state is dirty, this is forbidden: raises a DirtyStateException.

        Otherwise,
        * opens the configuration file at the given conf_file_path (path = None raises a TypeError, while nonexistent
        file raises a FileNotFoundError)
        * replaces the current_configuration with its contents.
        * remembers the file name in current_config_file

        :param new_conf_file_path:
        :return:
        """
        self.ensure_not_dirty()

        # open the file and read the new current configuration
        with open(new_conf_file_path, 'r') as f:
            self.current_configuration = GlobalEnvsConfig.from_yaml(f)

        # keep a backup for 'cancel'
        self.current_configuration_bak = deepcopy(self.current_configuration)

        # remember the new file path - use the private field not the property
        self._current_config_file = new_conf_file_path

        # alert of the changes
        self.comm_qt.current_file_changed.emit(QFileInfo(new_conf_file_path))
        self.comm_qt.current_configuration_changed_or_saved.emit(None)

    def is_dirty(self):
        return self.current_configuration != self.current_configuration_bak

    def ensure_not_dirty(self):
        """
        If the state is dirty, raises a DirtyStateException.
        :return:
        """
        if self.is_dirty():
            raise DirtyStateException()

    # def to_dict(self, only_dump_persisted_fields: bool = True) -> Dict:
    #     """
    #     Returns a dictionary containing the state fields. By default only the persisted fields are dumped and it only
    #     can return if the state is not dirty (otherwise a DirtyStateException is raised)
    #
    #     :param only_dump_persisted_fields:
    #     :return:
    #     """
    #     if only_dump_persisted_fields:
    #         self.ensure_not_dirty()
    #         return {'current_config_file': self.current_config_file}
    #     else:
    #         return {'current_config_file': self.current_config_file,
    #                 'current_configuration': self.current_configuration,
    #                 'is_dirty': self.is_dirty}
    #
    # @staticmethod
    # def from_dict(dct):
    #     return EnvSwitcherState(**dct)
    #
    # def to_yaml(self, only_dump_persisted_fields: bool = True, stream=None) -> str:
    #     """
    #     Returns a yaml string version of this state. By default only the persisted fields are dumped and it only
    #     can return if the state is not dirty (otherwise a DirtyStateException is raised)
    #
    #     :param only_dump_persisted_fields:
    #     :return:
    #     """
    #     return yaml.safe_dump(self.to_dict(only_dump_persisted_fields=only_dump_persisted_fields), stream=stream)
    #
    # @staticmethod
    # def from_yaml(stream):
    #     """
    #     Returns an EnvSwitcherState from the provided yaml
    #     :param stream:
    #     :return:
    #     """
    #     state_as_dict = yaml.safe_load(stream)
    #     return EnvSwitcherState.from_dict(state_as_dict)
    #
    # def persist_state_to_disk(self, file_path) -> bool:
    #     """
    #     Persists the STATE on disk at the given file path (this is different from saving the current configuration !)
    #     Returns True if it was able to persist the state, false otherwise
    #     :return:
    #     """
    #     try:
    #         # save to yaml file
    #         with open(file_path) as f:
    #             self.current_state.to_yaml(f)
    #         return True
    #     except Exception as e:
    #         warn('Caught exception while writing persisted state file at ' + file_path + ': ')
    #         warn(e)
    #
    #     # we could not write state to disk
    #     return False
    #
    # @staticmethod
    # def restore_state_from_disk(file_path):
    #     """
    #     Reads last known state from disk and returns the corresponding EnvSwitcherState. If there is an error reading
    #     the state or if the file does not exist, a warning is raised and this method raises a
    #     CouldNotRestoreStateException.
    #     :return:
    #     """
    #     if os.path.exists(file_path):
    #         try:
    #             # load from yaml file
    #             print("restoring state from yaml file: '" + str(file_path) + "'")
    #             with open(file_path) as f:
    #                 return EnvSwitcherState.from_yaml(f)
    #         except Exception as e:
    #             warn('Caught exception while loading persisted state file at ' + file_path + ': ')
    #             warn(e)
    #
    #     raise CouldNotRestoreStateException()

    def save_modifications(self):
        """
        Saves self.current_configuration to the disk at self.configuration_file_path
        :return:
        """
        if os.path.exists(self.current_config_file):
            print("saving current configuration to : '" + str(self.current_config_file) + "'")
            with open(self.current_config_file, mode='w') as f:
                # save to yaml file
                self.current_configuration.to_yaml(f)
                # update the 'reference' data
                self.current_configuration_bak = deepcopy(self.current_configuration)
                # alert the view
                # noinspection PyUnresolvedReferences
                self.comm_qt.current_configuration_changed_or_saved.emit(None)
        else:
            raise CouldNotSaveCurrentConfigurationException('File does not exist any more: ' + self.current_config_file)

    def save_as(self, new_file_path, overwrite: bool=False):
        """
        Saves self.current_configuration to the disk at new_file_path. The new_file_path should not already exist
        :return:
        """
        if overwrite or not os.path.exists(new_file_path):
            print("saving current configuration to : '" + str(new_file_path) + "'")
            with open(new_file_path, mode='w') as f:
                # save to yaml file
                self.current_configuration.to_yaml(f)
                # reopen it to update the backup and alert the view
                self.current_config_file = new_file_path
        else:
            raise CouldNotSaveCurrentConfigurationException('File already exists: ' + new_file_path)

    def cancel_modifications(self):
        """
        Cancels modifications to self.current_configuration by restoring self.current_configuration_bak
        :return:
        """
        # set back to reference data
        self.current_configuration = deepcopy(self.current_configuration_bak)
        # alert the view
        # noinspection PyUnresolvedReferences
        self.comm_qt.current_configuration_changed_or_saved.emit(None)

    # class EnvConfigQtModel(QAbstractTableModel):
    #     """
    #     Wraps an EnvConfig in a Qt model so that it can be mapped to a table view (Model-View Qt pattern).
    #
    #     According to Qt documentation
    #     * The model does not know when it will be used or which data is needed. It simply provides data each time
    #     the view requests it, thanks to rowCount, columnCount, and data methods. The flags() method is also called by
    #     the view in order to know which cells are editable
    #     * the model is edited by the view through the insertRows, removeRows, and setData
    #     * The model has to emit a signal to tell the view that data has changed, indicating what range of cells has
    #     changed (self.dataChanged(index, index))
    #
    #     A good example is provided here : http://doc.qt.io/qt-5/qtwidgets-itemviews-addressbook-example.html
    #
    #     """
    #     def __init__(self, env_config: EnvConfig, c: Communicate):
    #         """
    #         Constructor to create a model for the given EnvConfig.
    #         :param env_config:
    #         """
    #         super(EnvSwitcherState.EnvConfigQtModel, self).__init__()
    #         self.env_config = env_config
    #         self.c = c
    #         self.setObjectName("envQtModel_" + env_config.id)
    #
    #     def rowCount(self, parent: QModelIndex = ...):
    #         """
    #         Called by the view to know the number of rows available
    #         :param parent:
    #         :return:
    #         """
    #         return len(self.env_config.env_variables_dct)
    #
    #     def columnCount(self, parent: QModelIndex = ...):
    #         """
    #         Called by the view to know the number of columns available
    #         :param parent:
    #         :return:
    #         """
    #         return 2
    #
    #     def flags(self, index: QModelIndex):
    #         """
    #         This tells the view that cells are editable.
    #
    #         :param index:
    #         :return:
    #         """
    #         if not index.isValid():
    #             return Qt.ItemIsEnabled
    #
    #         if index.column() == 1:
    #             # values are editable
    #             return super(EnvSwitcherState.EnvConfigQtModel, self).flags(index) | Qt.ItemIsEditable
    #         else:
    #             # not labels
    #             return super(EnvSwitcherState.EnvConfigQtModel, self).flags(index)
    #
    #     def data(self, index: QModelIndex, role: int = ...):
    #         """
    #         Used by the view to access the data
    #
    #         :param index:
    #         :param role:
    #         :return:
    #         """
    #         if not index.isValid():
    #             return QVariant()
    #
    #         # the row and column requested
    #         row = index.row()
    #         col = index.column()
    #
    #         if row >= len(self.env_config.env_variables_dct) or row < 0:
    #             return QVariant()
    #
    #         elif role == Qt.DisplayRole or role == Qt.EditRole:
    #             return list(self.env_config.env_variables_dct.items())[row][col]
    #         # see http://doc.qt.io/qt-5/modelview.html#2-2-extending-the-read-only-example-with-roles
    #         # to further customize  font, background, text alignment, checkbox...
    #         # elif role == Qt.FontRole:
    #         #     pass
    #         # elif role == Qt.BackgroundRole:
    #         #     if col == 0:
    #         #         return QColor(Qt.gray)
    #
    #         return QVariant()
    #
    #     # def insertRows(self, row: int, count: int, parent: QModelIndex = ...):
    #     #     """
    #     #     see http://doc.qt.io/qt-5/qtwidgets-itemviews-addressbook-example.html
    #     #     """
    #
    #     # def removeRows(self, row: int, count: int, parent: QModelIndex = ...):
    #     # """
    #     #     see http://doc.qt.io/qt-5/qtwidgets-itemviews-addressbook-example.html
    #     #     """
    #
    #     def get_data_setter_for_index(self, row: int, col: int):
    #         """
    #         Generates a data setter (a 'slot') for the given row and column
    #         :param row:
    #         :param col:
    #         :return:
    #         """
    #         # @pyqtSlot()
    #         return lambda x: self.setData(index=self.index(row, col), value=x, role=Qt.EditRole)
    #
    #     def setData(self, index: QModelIndex, value: Any, role: int = ...):
    #         """
    #         Called when data is modified by the view
    #
    #         :param index:
    #         :param value:
    #         :param role:
    #         :return:
    #         """
    #         if index.isValid() and role == Qt.EditRole:
    #             row = index.row()
    #
    #             # modify the underlying configuration
    #             var_name = list(self.env_config.env_variables_dct.keys())[row]
    #             self.env_config.env_variables_dct[var_name] = value
    #
    #             print('[' + self.env_config.name + '] Set \'' + var_name + '\' to \'' + value + '\'')
    #
    #             # emit the 'data changed' message for a single element (so between index and index)
    #             # self.comm_qt.slot_current_configuration_changed_or_saved.emit(index, index)
    #             # no need for index right now
    #             self.c.slot_current_configuration_changed_or_saved.emit()
    #             return True
    #
    #         return False
    #
    # def get_qt_models(self) -> Dict[str, QAbstractTableModel]:
    #     """
    #     Returns a dictionary of environment id, environment model for the view to use
    #     :return:
    #     """
    #     # we have to do it like that to keep the order
    #     res = OrderedDict()
    #     for env_id, env_config in self.current_configuration.envs.items():
    #         res[env_id] = EnvSwitcherState.EnvConfigQtModel(env_config, self.comm_qt)
    #     return res

    def get_env_ids(self) -> List[str]:
        return list(self.current_configuration.envs)

    def get_env_name(self, env_id: str) -> str:
        return self.current_configuration.envs[env_id].name

    def get_env_variables(self, env_id: str) -> Dict[str, str]:
        return self.current_configuration.envs[env_id].env_variables_dct

    def set_env_variable(self, env_id: str, var_name: str, var_value: str, cause: QObject=None):
        self.current_configuration.envs[env_id].env_variables_dct[var_name] = var_value
        # print('[' + env_id + '] Set \'' + var_name + '\' to \'' + var_value + '\'')
        # emit the 'data changed' message
        # noinspection PyUnresolvedReferences
        self.comm_qt.current_configuration_changed_or_saved.emit(cause)

    def create_slot_set_env_variable(self, env_id, var_name, var_value_editor):
        def set_data(x):
            self.set_env_variable(env_id, var_name, x, var_value_editor)
        return set_data


class EnvSwitcherView(QMainWindow, Ui_MainWindow):
    """
    The 'View' in the MVC pattern.

    The static design is generated from qt_designer in qt_design.py. The rest concerns
    * how the view is dynamically created when a new model is loaded (see recreate_tabs_view)
    * the slots related to file menu actions, See also Main window tutorial:
    http://doc.qt.io/qt-5/qtwidgets-mainwindows-application-example.html

    """

    ENV_TAB_WIDGET_PREFIX = "envTab_"

    # TODO allow user to add & rename tabs see https://stackoverflow.com/questions/44450775/pyqt-gui-with-multiple-tabs

    def __init__(self, apply_current_tab_hook, quit_hook=None, save_config_hook=None, cancel_modifications_hook=None,
                 open_config_file_hook=None, save_config_as_hook=None):
        """
        Creates the main application's window.
        The controller should provide method hooks for all main events.

        :param apply_current_tab_hook:
        :param quit_hook:
        :param save_config_hook:
        :param cancel_modifications_hook:
        :param open_config_file_hook:
        :param save_config_as_hook:
        """
        super(EnvSwitcherView, self).__init__()

        # **** setup generated by qt designer
        self.setupUi(self)

        # remove the hardcoded window title so that the title will become the file name
        # noinspection PyTypeChecker
        self.setWindowTitle(None)

        # **** remove the part of generated code responsible for the tab, it will be replaced with dynamic tabs later
        # -- retrieve various information we want to remember about the tab
        self.env_tab_size_policy_from_design = self.envTab1.sizePolicy()
        self.var_line_edit_size_policy_from_design = self.var1LineEdit.sizePolicy()
        # -- delete all fields associated with the tab from self.
        self.envTab1.close()
        self.envTab1.deleteLater()
        del self.envTab1
        del self.envTab1GridLayout
        del self.envTab1FormLayout
        del self.var1Label
        del self.var1LineEdit
        del self.var2Label
        del self.var2LineEdit
        # del self.envTab1TableView

        # **** connect buttons and menu actions to events
        # -- save
        self.okCancelApplyButtonBox.accepted.connect(save_config_hook or self.slot_save_config)
        self.actionSave.triggered.connect(save_config_hook or self.slot_save_config)
        # -- cancel
        self.okCancelApplyButtonBox.rejected.connect(cancel_modifications_hook or self.slot_cancel_modifications)

        # -- apply
        def clicked_hook(button: QAbstractButton):
            # button.text()
            if button.foregroundRole() == QDialogButtonBox.ApplyRole:
                current_tab_widget = self.envsTabWidget.currentWidget()
                apply_current_tab_hook(current_tab_widget.objectName()[len(EnvSwitcherView.ENV_TAB_WIDGET_PREFIX):])
        self.okCancelApplyButtonBox.clicked.connect(clicked_hook)

        # *** connect remaining menu actions to events
        self.actionOpen.triggered.connect(open_config_file_hook or self.slot_open_config)
        self.actionSave_As.triggered.connect(save_config_as_hook or self.slot_save_config_as)
        self.actionQuit.triggered.connect(quit_hook or self.closeEvent)

        # *** the list of value editors that will be used in slot_current_configuration_changed_or_saved
        self.line_editors = []

    # class QLineEditDelegate(QItemDelegate):
    #     """
    #     A delegate responsible to provide a QLineEditor for table cells. It is used for 'values' column.
    #     From http://www.qtcentre.org/threads/27956-QLineEdit-Delegate-value-update
    #     """
    #     def createEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QModelIndex):
    #         return QLineEdit(parent)
    #
    #     def setEditorData(self, editor: QWidget, index: QModelIndex):
    #         value = index.model().data(index, Qt.EditRole)
    #         editor.setText(value)
    #
    #     def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex):
    #         model.setData(index, value=editor.text(), role=Qt.EditRole)
    #
    #     def updateEditorGeometry(self, editor: QWidget, option: 'QStyleOptionViewItem', index: QModelIndex):
    #         editor.setGeometry(option.rect)

    # noinspection PyUnresolvedReferences
    def set_model(self, state: EnvSwitcherState):
        """
        Associates the view with the given state.

        Binds the QTabWidget http://doc.qt.io/qt-5/qtabwidget.html to the state, by
        * creating one tab for each environment
        * and binding each tab widgets to the model thanks to a QDataWidgetMapper

        :param state:
        :return:
        """
        # connect the model to the view and save it in self for future references
        state.comm_qt.current_configuration_changed_or_saved.connect(self.slot_current_configuration_changed_or_saved)
        state.comm_qt.current_file_changed.connect(self.slot_current_file_changed)
        self.state = state

        # refresh the tabs and current file name
        self.slot_current_file_changed()
        # update the button status
        self.slot_current_configuration_changed_or_saved()

    class EnvVarEditor(QLineEdit):
        def __init__(self, parent, env_id, var_name):
            super(EnvSwitcherView.EnvVarEditor, self).__init__(parent)
            self.env_id = env_id
            self.var_name = var_name

    def recreate_tabs_view(self, state):
        """
        Destroys all tabs in the view and creates them agains according to the given state

        :param state:
        :return:
        """
        # Remove all existing tabs
        for tab_idx in range(0, self.envsTabWidget.count()):
            tab_widget = self.envsTabWidget.widget(0)
            tab_widget.close()
            tab_widget.deleteLater()
            del tab_widget
            self.envsTabWidget.removeTab(0)

        # clean all value editors
        self.line_editors.clear()

        # For each environment described in the state, create a tab
        for env_id in state.get_env_ids():
            # Note: env is an EnvConfig object

            # Create tab widget
            new_env_tab = QWidget()
            new_env_tab.setSizePolicy(self.env_tab_size_policy_from_design)  # reuse size policy from generated code
            new_env_tab.setObjectName(EnvSwitcherView.ENV_TAB_WIDGET_PREFIX + env_id)  # object name > reuse id

            # Apply a Grid layout on the tab
            new_tab_grid_layout = QGridLayout(new_env_tab)
            new_tab_grid_layout.setContentsMargins(11, 11, 11, 11)
            new_tab_grid_layout.setObjectName("envTab_" + env_id + "_GridLayout")

            # There are two ways that we could do this
            # (1) a form >> in that case it is not possible to have a model-view

            # Create a form layout inside the tab
            new_env_tab_form_layout = QFormLayout()
            new_env_tab_form_layout.setObjectName("envTab_" + env_id + "_FormLayout")

            # Fill the form with as many rows as needed
            idx = 0
            for var_name, var_value in state.get_env_variables(env_id).items():
                # for idx in range(0, env_model.rowCount()):
                idx += 1

                # label
                var_label = QLabel(new_env_tab)
                var_label.setObjectName("envTab_" + env_id + "_var_" + str(idx) + "_Label")
                # get the value from the model
                # var_label.setText(env_model.data(env_model.index(idx, 0), role=Qt.DisplayRole))
                var_label.setText(var_name)
                new_env_tab_form_layout.setWidget(idx, QFormLayout.LabelRole, var_label)

                # line edit
                var_value_editor = EnvSwitcherView.EnvVarEditor(new_env_tab, env_id, var_name)
                var_value_editor.setSizePolicy(self.var_line_edit_size_policy_from_design)
                var_value_editor.setObjectName("envTab_" + env_id + "_var_" + str(idx) + "_LineEdit")
                # --link to the model, bidirectional
                # var_value_editor.setText(env_model.data(env_model.index(idx, 1), role=Qt.DisplayRole))
                var_value_editor.setText(var_value)
                # var_value_editor.textEdited.connect(env_model.get_data_setter_for_index(idx, 1))
                # noinspection PyUnresolvedReferences
                var_value_editor.textEdited.connect(state.create_slot_set_env_variable(env_id, var_name,
                                                                                       var_value_editor))
                # def on_value_change():
                #     var_value_editor.setText(env_model.data(env_model.index(idx, 1), role=Qt.DisplayRole))
                # state.comm_qt.slot_current_configuration_changed_or_saved.connect(on_value_change)
                # state.comm_qt.slot_current_configuration_changed_or_saved.connect(
                #     lambda: var_value_editor.setText(env_model.data(env_model.index(idx, 1), role=Qt.DisplayRole)))
                # state.comm_qt.slot_current_configuration_changed_or_saved.connect(self.get_view_updater_slot_for
                # (var_value_editor, state, env_id, var_name))
                self.line_editors.append(var_value_editor)
                # --add to layout
                new_env_tab_form_layout.setWidget(idx, QFormLayout.FieldRole, var_value_editor)

            new_tab_grid_layout.addLayout(new_env_tab_form_layout, 0, 0, 1, 1)

            # # (2) a TableView mapped to a TableModel
            # ------------> too ugly :(
            # new_env_tab_table_view = QTableView(new_env_tab)
            # new_env_tab_table_view.setShowGrid(False)
            # new_env_tab_table_view.setObjectName("envTab_" + env_id + "TableView")
            # # --no background color
            # new_env_tab_table_view.setStyleSheet("background-color: transparent;")
            # # --no row or column headers
            # new_env_tab_table_view.horizontalHeader().setVisible(False)
            # new_env_tab_table_view.verticalHeader().setVisible(False)
            # # --auto stretch size
            # new_env_tab_table_view.horizontalHeader().setStretchLastSection(True)
            # # --no selection is possible
            # new_env_tab_table_view.setSelectionMode(QAbstractItemView.NoSelection)
            # # --bind to delegate
            # new_env_tab_table_view.setItemDelegateForColumn(1, EnvSwitcherView.QLineEditDelegate())
            # # --bind to model
            # new_env_tab_table_view.setModel(env_model)
            # new_env_tab_table_view.show()
            # #new_env_tab_table_view.setIndexWidget()
            #
            # # Add to the tab's layout
            # new_tab_grid_layout.addWidget(new_env_tab_table_view, 0, 0, 1, 1)

            # Finally add the tab with the appropriate name
            # self.envsTabWidget.addTab(new_env_tab, env_model.env_config.name)
            self.envsTabWidget.addTab(new_env_tab, state.get_env_name(env_id))

        print('Done refreshing environment tabs to reflect opened configuration')

    # def get_view_updater_slot_for(self, var_value_editor, state, env_id, var_name):
    #     def update_data(cause: QObject):
    #         if cause != var_value_editor:
    #             var_value_editor.setText(state.get_env_variables(env_id)[var_name])
    #     return update_data

    def slot_current_configuration_changed_or_saved(self, cause=None):
        """
        Called whenever the current configuration data is changed or saved.
        * refresh all QLineEdit widgets in the tabs
        * check the 'dirtiness' and update the window title, menu bar and buttons accordingly
        :return:
        """

        for var_value_editor in self.line_editors:
            if cause != var_value_editor:
                var_value_editor.setText(
                    self.state.get_env_variables(var_value_editor.env_id)[var_value_editor.var_name])

        is_dirty = self.state.is_dirty()
        self.setWindowModified(is_dirty)
        self.actionSave.setEnabled(is_dirty)
        self.okCancelApplyButtonBox.buttons()[0].setEnabled(is_dirty)
        self.okCancelApplyButtonBox.buttons()[1].setEnabled(is_dirty)

    def slot_current_file_changed(self, file: QFileInfo=None):
        """
        Called whenever the configuration file has been changed.
        We have to recreate the tabs view and update the title bar
        :return:
        """
        # refresh the tabs
        self.recreate_tabs_view(self.state)

        # refresh the title bar
        self.setWindowFilePath(self.state.current_config_file)
        # self.setWindowFilePath(QFileInfo(self.state.current_config_file).fileName())

    def closeEvent(self, event: QCloseEvent):
        """
        Called by the view when the user selects File > Quit or closes the application.
        :return:
        """
        if self.maybe_save_modifications_before_continuing():
            # try to save persisted state >> no need anymore, the QSettings() do it for us automatically
            # can_exit = self.internal_state.persist_state_to_disk(
            #                                      self.get_file_path(EnvSwitcherApp.PERSISTED_STATE_FILE))
            event.accept()
        else:
            event.ignore()

    def slot_open_config(self):
        """
        Called by the view when user selects File > Open...
        :return:
        """
        if self.maybe_save_modifications_before_continuing():
            # ask the user to select a configuration file to open
            try:
                config_file_path, _ = QFileDialog.getOpenFileName(self, caption='Open a Configuration File',
                                                                  filter="Configuration files (*.yml *.yaml)")

                # 'cancel' will return without exception but with an empty config_file_path
                if config_file_path == '':
                    print('User cancelled opening file.')
                    return
            except FileNotFoundError:
                # 'exit' button press will raise a FileNotFoundError
                print('User cancelled opening file.')
                return

            # try to open the configuration file
            if self.state is None:
                raise Exception('Internal error - This view does not have a bound state !!! ')
            else:
                # this will automatically load the corresponding config
                self.state.current_config_file = config_file_path

    def slot_save_config(self):
        """
        Called by the view when user selects File > Save, or CTRL+S, or clicks on 'Save' button.
        It tries to save the configuration to disk.
        In case of failure, it triggers the 'save as' action
        :return:
        """
        try:
            self.state.save_modifications()
            return True
        except Exception as e:
            error_dialog = QErrorMessage()
            error_dialog.showMessage(str(e))
            return False

    def slot_save_config_as(self):
        try:
            # popup 'save as', including the checker "file already exists - want to overwrite ?"
            new_file_path, _ = QFileDialog.getSaveFileName(parent=self,
                                                           caption='Save Configuration File As...',
                                                           filter="Configuration files (*.yml *.yaml)")
            # 'cancel' will return without exception but with an empty config_file_path
            if new_file_path == '':
                print('User cancelled saving file.')
                return

            # save
            self.state.save_as(new_file_path=new_file_path, overwrite=True)

        except FileNotFoundError:
            # 'exit' button press will raise a FileNotFoundError
            print('User cancelled saving file.')
            return

        # overwrite=False
        # if os.path.exists(new_file_path):
        #     # popup 'file already exists - are you sure ?'
        #     buttonReply = QMessageBox.warning(self, "Application",
        #                                       "File already exists.\nDo you want to overwite?",
        #                                       QMessageBox.Yes | QMessageBox.No)
        #     if buttonReply == QMessageBox.No:
        #         # cancel the operation
        #         return
        #     elif buttonReply == QMessageBox.Yes:
        #         overwrite = True

    def slot_cancel_modifications(self):
        """
        Called by the view when user clicks on 'Cancel' button.
        :return:
        """
        self.state.cancel_modifications()

    def maybe_save_modifications_before_continuing(self) -> bool:
        """
        If the state is dirty, asks the user whether he/she wants to save or discard the changes before performing the
        next operation, or to cancel the next operation
        :return: a boolean indicating if the next operation should be performed (True) or not (False)
        """
        if not self.state.is_dirty():
            return True
        else:
            button_reply = QMessageBox.warning(self, "Application",
                                               "The document has been modified.\nDo you want to save your changes?",
                                               QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            if button_reply == QMessageBox.Save:
                # try to save and cancel if not successful
                return self.slot_save_config()
            elif button_reply == QMessageBox.Cancel:
                # cancel the operation
                return False
            else:
                # discard the changes and continue
                self.state.cancel_modifications()
                return True


class EnvSwitcherApp(QApplication):
    """
    The main EnvSwitch Application. (the 'Controller' in the MVC pattern)
    * creates (and updates ?) views
    * receives input events from the view
    * query & modifies the internal_state

    It is responsible to handle the current state, map it to persistence layer, and refresh the views
    """

    # PERSISTED_STATE_FILE = 'internal_state'

    def __init__(self, argv):
        # appGuid = 'eec75acc-a20a-11e7-b284-4ceb42c7d9fd'
        super(EnvSwitcherApp, self).__init__(argv)

        # ** self = Controller **
        # -- persistence dirs = user_data_dir, site_data_dir, user_cache_dir, user_log_dir
        # self.dirs = AppDirs("envswitch", "smarie", version=_app_version)

        # ** View **
        # some qt stuff are in the 'application' (self), not the view.
        # self.setApplicationName() automatically defaults to the executable name
        self.setOrganizationName('smarie')
        self.setOrganizationDomain('github.com')
        self.setApplicationDisplayName('EnvSwitch')

        # base: use generated method from qt_design.py to set up layout and widgets that are defined
        print("Creating Main View")
        self.ui = EnvSwitcherView(apply_current_tab_hook=self.apply_current_env,
                                  quit_hook=self.quit)

        # Show so that the 'open file' dialog below can show
        self.ui.show()

        # ** Model **
        # -- try to get a current state
        try:
            # restore last known state if possible
            # self.internal_state = EnvSwitcherState.restore_state_from_disk(self.get_file_path(PERSISTED_STATE_FILE))
            self.settings = QSettings()
            config_file_path = self.settings.value('configuration_file_path', type=str)
            self.internal_state = EnvSwitcherState(configuration_file_path=config_file_path)
            print("Restored last open file successfully: " + config_file_path)

        except Exception as e:  # FileNotFoundError, PermissionError:  # CouldNotRestoreStateException:
            # not possible: we have to ask the user to open a configuration file
            print("Could not restore last open file : " + str(e))
            print("We need a configuration file, ask the user")
            loaded = False
            while not loaded:
                try:
                    # ask the user to select a configuration file to open
                    config_file_path, _ = QFileDialog.getOpenFileName(parent=self.ui,
                                                                      caption='Open a Configuration File',
                                                                      filter="Configuration files (*.yml *.yaml)")
                    # 'cancel' will return without exception but with an empty config_file_path
                    if config_file_path == '':
                        print('User cancelled opening file. Exiting')
                        exit()
                except FileNotFoundError:
                    # 'exit' button press will raise a FileNotFoundError
                    print('User cancelled opening file. Exiting')
                    exit()
                try:
                    # try to create a state = try to open the configuration file
                    self.internal_state = EnvSwitcherState(configuration_file_path=config_file_path)
                    # remember the last opened file
                    self.settings.setValue('configuration_file_path', config_file_path)
                    loaded = True
                except TypeError as e:
                    warn(str(e))
                except FileNotFoundError as f:
                    warn(str(f))

        # keep informed if the file changes
        # noinspection PyUnresolvedReferences
        self.internal_state.comm_qt.current_file_changed.connect(self.slot_current_file_changed)

        # connect the view to the model
        self.ui.set_model(self.internal_state)
        print('Application ready')

    def slot_current_file_changed(self, file: QFileInfo):
        self.settings.setValue('configuration_file_path', file.filePath())

    # def exit(self, returnCode: int = ...):
    #     if os.path.exists(self.get_file_path(EnvSwitcherApp.PERSISTED_STATE_FILE) + '.lock'):
    #         raise
    #     super(EnvSwitcherApp, self).exit(returnCode=returnCode)

    def apply_current_env(self, env_id):
        self.internal_state.current_configuration.envs[env_id].apply()

    # def get_file_path(self, file_name):
    #     """
    #     Gets the absolute path to the given persisted file name. It basically relies on self.user_cache_dir
    #     :param file_name:
    #     :return:
    #     """
    #     # make sure the user_cache_dir is still there
    #     os.makedirs(self.dirs.user_cache_dir, exist_ok=True)
    #     return os.path.join(self.dirs.user_cache_dir, file_name)

# class MainApp(QMainWindow, Ui_MainWindow):
#     """
#     Main window, that contains the Table Widget - itself containing the tabs
#     """
#
#     def __init__(self):
#         super().__init__()
#         self.title = 'PyQt5 tabs - pythonspot.com'
#         self.left = 100
#         self.top = 100
#         self.width = 500
#         self.height = 400
#         self.setWindowTitle(self.title)
#         self.setGeometry(self.left, self.top, self.width, self.height)
#
#         self.table_widget = MyTableWidget(self)
#         self.setCentralWidget(self.table_widget)
#
#         self.show()
#
# class MyTableWidget(QWidget):
#     """
#     The widget that contains the tabs
#     """
#     def __init__(self, parent):
#         super(QWidget, self).__init__(parent)
#         self.layout = QVBoxLayout(self)
#
#         # Initialize tab screen
#         self.tabs = QTabWidget()
#         self.tabs.resize(parent.width, parent.height)
#
#         # Add tabs
#         self.tab1 = QWidget()
#         self.tabs.addTab(self.tab1, "Env 1")
#         self.tab2 = QWidget()
#         self.tabs.addTab(self.tab2, "Env 2")
#         self.tab2 = QWidget()
#         self.tabs.addTab(self.tab2, "Env 3")
#
#         # Create first tab
#         self.tab1.layout = QVBoxLayout(self)
#         self.pushButton1 = QPushButton("PyQt5 button")
#         self.tab1.layout.addWidget(self.pushButton1)
#         self.tab1.setLayout(self.tab1.layout)
#
#         # Add tabs to the layout of widget
#         self.layout.addWidget(self.tabs)
#         self.setLayout(self.layout)
#
#     @pyqtSlot()
#     def on_click(self):
#         print("\n")
#         for currentQTableWidgetItem in self.tableWidget.selectedItems():
#             print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())


def main():

    print('*** ENVSWITCH <' + _app_version + '> ***')

    # create the application (the frame around everything), passing in the possible commandline arguments
    app = EnvSwitcherApp(sys.argv)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
