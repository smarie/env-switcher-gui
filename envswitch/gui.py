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
from envswitch.utils import get_version


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
    * rslot_current_config_changed_or_saved that will be triggered whenever the current configuration is modified
    (for example, the user edits the form), or is saved.
    * rslot_current_file_changed that will be triggered whenever the current opened file changes (a new file is opened
    for example).
    """
    current_config_changed_or_saved = pyqtSignal(QObject)  # the arg is the cause
    current_file_changed = pyqtSignal(QFileInfo)


class EnvSwitcherState:  # maybe one day convert to a QStandardItemModel ?
    """
    The Model(s) in the MVC pattern.

    The state of the application is composed of several things:
    * self.current_config_file: the path to the currently open configuration file. It can't be None and always
    represents a valid file
    * self.current_configuration: the currently loaded configuration. It is the same than the one in the file if
    self.is_dirty = False
    * self.is_dirty: True if the current configuration has some modifications that are yet not saved.
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

        If the state is dirty, this is forbidden: raises a DirtyStateException. Otherwise,
        * opens the configuration file at the given conf_file_path (path = None raises a TypeError, while nonexistent
        file raises a FileNotFoundError)
        * replaces the current_configuration with its contents.
        * remembers the file name in current_config_file

        :param new_conf_file_path:
        :return:
        """
        self.ensure_not_dirty()

        # open the file and read the new current configuration
        print("Opening configuration file : '" + new_conf_file_path + "'")
        with open(new_conf_file_path, 'r') as f:
            self.current_configuration = GlobalEnvsConfig.from_yaml(f)

        # keep a backup for 'cancel'
        self.current_configuration_bak = deepcopy(self.current_configuration)

        # remember the new file path - use the private field not the property
        self._current_config_file = new_conf_file_path

        # alert of the changes
        self.comm_qt.current_file_changed.emit(QFileInfo(new_conf_file_path))
        self.comm_qt.current_config_changed_or_saved.emit(None)

    def is_dirty(self):
        return self.current_configuration != self.current_configuration_bak

    def ensure_not_dirty(self):
        """
        If the state is dirty, raises a DirtyStateException.
        :return:
        """
        if self.is_dirty():
            raise DirtyStateException()

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
                self.comm_qt.current_config_changed_or_saved.emit(None)
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
                # update the backup otherwise reopening the file will raise a DirtyStateException
                self.current_configuration_bak = deepcopy(self.current_configuration)
                # reopen it to alert the view
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
        self.comm_qt.current_config_changed_or_saved.emit(None)

    def get_env_ids(self) -> List[str]:
        return list(self.current_configuration.envs)

    def get_env_name(self, env_id: str) -> str:
        return self.current_configuration.envs[env_id].name

    def get_env_variables(self, env_id: str) -> Dict[str, str]:
        return self.current_configuration.envs[env_id].env_variables_dct

    def set_env_variable(self, env_id: str, var_name: str, var_value: str, cause: QObject=None):
        """
        Sets a new value for the given environment variable
        :param env_id:
        :param var_name:
        :param var_value:
        :param cause:
        :return:
        """
        self.current_configuration.envs[env_id].env_variables_dct[var_name] = var_value
        # print('[' + env_id + '] Set \'' + var_name + '\' to \'' + var_value + '\'')

        # emit the 'data changed' message
        # noinspection PyUnresolvedReferences
        self.comm_qt.current_config_changed_or_saved.emit(cause)

    def create_slot_set_env_variable(self, env_id, var_name, var_value_editor):
        """
        Creates a slot to set a specific environment variable

        :param env_id:
        :param var_name:
        :param var_value_editor:
        :return:
        """
        def set_env_variable(x):
            self.set_env_variable(env_id, var_name, x, var_value_editor)
        return set_env_variable


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

    def __init__(self, apply_current_tab_hook=None, quit_hook=None, save_config_hook=None,
                 cancel_modifications_hook=None, open_config_file_hook=None, save_config_as_hook=None):
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
        self.mainButtonBox.accepted.connect(save_config_hook or self.lslot_save_config)
        self.actionSave.triggered.connect(save_config_hook or self.lslot_save_config)
        # -- cancel
        self.mainButtonBox.rejected.connect(cancel_modifications_hook or self.lslot_cancel_modifications)
        # -- apply
        apply_current_tab_hook = apply_current_tab_hook or self.lslot_apply_current_env
        def clicked_hook(button: QAbstractButton):
            # button.text()
            if button.foregroundRole() == QDialogButtonBox.ApplyRole:
                current_tab_widget = self.envsTabWidget.currentWidget()
                apply_current_tab_hook(current_tab_widget.objectName()[len(EnvSwitcherView.ENV_TAB_WIDGET_PREFIX):])
        self.mainButtonBox.clicked.connect(clicked_hook)

        # *** connect remaining menu actions to events
        self.actionOpen.triggered.connect(open_config_file_hook or self.lslot_open_config)
        self.actionSave_As.triggered.connect(save_config_as_hook or self.lslot_save_config_as)
        self.actionQuit.triggered.connect(quit_hook or self.lslot_quit)

        # *** the list of value editors that will be used in rslot_current_config_changed_or_saved
        self.line_editors = []

    # noinspection PyUnresolvedReferences
    def set_model(self, state: EnvSwitcherState):
        """
        Associates the view with the given state.

        Binds the QTabWidget http://doc.qt.io/qt-5/qtabwidget.html in this view to the state, by
        * creating one tab for each environment
        * and binding each tab widgets to the model thanks to dedicated signals-slots

        :param state:
        :return:
        """
        # connect the model to the view and save it in self for future references
        state.comm_qt.current_config_changed_or_saved.connect(self.rslot_current_config_changed_or_saved)
        state.comm_qt.current_file_changed.connect(self.rslot_current_file_changed)
        self.state = state

        # refresh the tabs and current file name
        self.rslot_current_file_changed()

        # refresh the buttons status according to 'dirtiness' of the state
        self.rslot_current_config_changed_or_saved()

    def rslot_current_file_changed(self, file: QFileInfo=None):
        """
        Called whenever the configuration file has been changed.
        We have to recreate the tabs view and update the title bar
        :return:
        """
        # refresh the tabs
        self.recreate_tabs_view(self.state)

        # refresh the title bar
        self.setWindowFilePath(self.state.current_config_file)

    class EnvVarEditor(QLineEdit):
        """ A QLineEdit to edit an environment variable value. It remembers the associated env id and var name """
        def __init__(self, parent, env_id, var_name):
            super(EnvSwitcherView.EnvVarEditor, self).__init__(parent)
            self.env_id = env_id
            self.var_name = var_name

    def recreate_tabs_view(self, state: EnvSwitcherState):
        """
        Destroys all tabs in the view and creates them again according to the given state
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

        # clear the list of value editors (used in self.lslot_apply_current_env)
        self.line_editors.clear()

        # For each environment described in the state, create a tab
        for env_id in state.get_env_ids():

            # Create tab widget
            new_env_tab = QWidget()
            new_env_tab.setSizePolicy(self.env_tab_size_policy_from_design)  # reuse size policy from generated code
            new_env_tab.setObjectName(EnvSwitcherView.ENV_TAB_WIDGET_PREFIX + env_id)  # object name > reuse id

            # Apply a Grid layout on the tab
            new_tab_grid_layout = QGridLayout(new_env_tab)
            new_tab_grid_layout.setContentsMargins(11, 11, 11, 11)
            new_tab_grid_layout.setObjectName("envTab_" + env_id + "_GridLayout")

            # There are two ways that we could design the widget
            # (1) a form >> in that case it is not possible to reuse a QTableModel
            # Create a form layout inside the tab
            new_env_tab_form_layout = QFormLayout()
            new_env_tab_form_layout.setObjectName("envTab_" + env_id + "_FormLayout")

            # Fill the form with as many rows as needed
            idx = 0
            for var_name, var_value in state.get_env_variables(env_id).items():
                idx += 1

                # label
                var_label = QLabel(new_env_tab)
                var_label.setObjectName("envTab_" + env_id + "_var_" + str(idx) + "_Label")
                var_label.setText(var_name)
                new_env_tab_form_layout.setWidget(idx, QFormLayout.LabelRole, var_label)

                # line edit
                var_value_editor = EnvSwitcherView.EnvVarEditor(new_env_tab, env_id, var_name)
                var_value_editor.setSizePolicy(self.var_line_edit_size_policy_from_design)
                var_value_editor.setObjectName("envTab_" + env_id + "_var_" + str(idx) + "_LineEdit")
                var_value_editor.setText(var_value)
                # link to model, bidirectional
                # -- editor > model
                # noinspection PyUnresolvedReferences
                var_value_editor.textEdited.connect(state.create_slot_set_env_variable(env_id, var_name,
                                                                                       var_value_editor))
                # -- model > editor
                self.line_editors.append(var_value_editor)
                new_env_tab_form_layout.setWidget(idx, QFormLayout.FieldRole, var_value_editor)

            new_tab_grid_layout.addLayout(new_env_tab_form_layout, 0, 0, 1, 1)

            # (2) other option: a TableView mapped to a TableModel --> too ugly :(  (still available in the git history)

            # Finally add the tab with the appropriate name
            self.envsTabWidget.addTab(new_env_tab, state.get_env_name(env_id))

        print('Done refreshing environment tabs to reflect opened configuration')

    def rslot_current_config_changed_or_saved(self, cause=None):
        """
        Called by the model whenever the current configuration data is changed or saved.
        * refreshes all QLineEdit widgets in the tabs
        * check the 'dirtiness' and update the window title, menu bar and buttons accordingly
        :return:
        """
        # Refresh all the editors' text except the one that triggered the mod (otherwise it will loose focus)
        for var_value_editor in self.line_editors:
            if cause != var_value_editor:
                var_value_editor.setText(
                    self.state.get_env_variables(var_value_editor.env_id)[var_value_editor.var_name])

        # Update several widgets' status according to dirtiness state
        is_dirty = self.state.is_dirty()
        self.setWindowModified(is_dirty)
        self.actionSave.setEnabled(is_dirty)
        self.mainButtonBox.buttons()[0].setEnabled(is_dirty)
        self.mainButtonBox.buttons()[1].setEnabled(is_dirty)

    def lslot_open_config(self):
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

    def lslot_save_config(self):
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

    def lslot_save_config_as(self):
        """
        Called by the view when the user clicks on "save as"
        :return:
        """
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

    def lslot_cancel_modifications(self):
        """
        Called by the view when user clicks on 'Cancel' button.
        :return:
        """
        self.state.cancel_modifications()

    def lslot_quit(self):
        """
        Called by the view when user clicks on 'Quit' button.
        :return:
        """
        self.close()  # this will trigger the closeEvent()

    def closeEvent(self, event: QCloseEvent):
        """
        Called by the view when the user selects File > Quit or closes the application.
        :return:
        """
        if self.maybe_save_modifications_before_continuing():
            # try to save persisted state >> no need anymore, the QSettings() do it for us automatically
            # can_exit = self.internal_state.persist_state_to_disk(
            #                                      self.get_file_path(EnvSwitcherApp.PERSISTED_STATE_FILE))
            print('Terminating...')
            event.accept()
        else:
            event.ignore()

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
                return self.lslot_save_config()
            elif button_reply == QMessageBox.Cancel:
                # cancel the operation
                return False
            else:
                # discard the changes and continue
                self.state.cancel_modifications()
                return True

    def lslot_apply_current_env(self, env_id):
        """
        Called by the view whenever the apply button is pushed.
        :param env_id:
        :return:
        """
        self.state.current_configuration.envs[env_id].apply()


class EnvSwitcherApp(QApplication):
    """
    The main EnvSwitch Application. (the 'Controller' in the MVC pattern)
    * creates (and updates ?) views
    * receives input events from the view
    * query & modifies the internal_state

    It is responsible to handle the current state, map it to persistence layer, and refresh the views
    """

    SETTING_LAST_OPENED_FILE_PATH = 'configuration_file_path'

    def __init__(self, headless: bool, argv, env_id: str=None, config_file_path: str=None):
        """
        Initializes the application
        * either in gui mode (headless = False), in which case the arguments argv MUST be empty
        * or in cli mode (headless = True) in which case the arguments will be used,

        :param headless: a boolean indicating if the app has to be launched with a visible GUI (False) or without (True)
        :param env_id: in headless mode only, this indicates the environment id to apply
        :param config_file_path: in headless mode only, this indicates the alternate config file to use
        :param argv: generic Qt arguments for the underlying Qt application
        """
        super(EnvSwitcherApp, self).__init__(argv)

        # ** Application / Controller (self) **
        # -- some qt-related fields that are useful to all the views created by the application
        self.setOrganizationName('smarie')
        self.setOrganizationDomain('github.com')
        self.setApplicationDisplayName('EnvSwitch')
        # self.setApplicationName() automatically defaults to the executable name so dont modify it
        self.settings = QSettings()

        if headless:
            # config_file_path is either the one provided in cli argument or the last opened one
            config_file_path = config_file_path or self.settings.value(EnvSwitcherApp.SETTING_LAST_OPENED_FILE_PATH,
                                                                       type=str)
            # try to open the file
            try:
                print("Trying to open file: " + config_file_path)
                state = EnvSwitcherState(configuration_file_path=config_file_path)
                print("Opened file successfully: " + config_file_path)
            except Exception as e:
                print("Could not restore last open file : " + str(e))
                sys.exit(1)  # error

            # if the environment required is known, apply it
            if env_id in state.current_configuration.envs.keys():
                state.current_configuration.envs[env_id].apply()
                sys.exit(0)  # success
            else:
                print("Environment id '" + env_id + "' is unknown in this configuration file. Available environments: "
                      + str(list(state.current_configuration.envs.keys())))
                sys.exit(1)  # error
        else:
            # ** View **
            print("Creating Main View")
            self.ui = EnvSwitcherView()
            self.ui.show()  # Show so that the 'open file' dialog below can show

            # ** Model **
            try:
                # restore last known state if possible
                config_file_path = self.settings.value(EnvSwitcherApp.SETTING_LAST_OPENED_FILE_PATH, type=str)
                print("Trying to restore last open file: " + config_file_path)
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
                            print('User cancelled opening file. Terminating')
                            sys.exit(1)
                    except FileNotFoundError:
                        # 'exit' button press will raise a FileNotFoundError
                        print('User cancelled opening file. Terminating')
                        sys.exit(1)
                    try:
                        # try to create a state = try to open the configuration file
                        self.internal_state = EnvSwitcherState(configuration_file_path=config_file_path)
                        # remember the last opened file
                        print("saving last open file path for future launches : '" + config_file_path + "'")
                        self.settings.setValue(EnvSwitcherApp.SETTING_LAST_OPENED_FILE_PATH, config_file_path)
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
        print("saving last open file path for future launches : '" + str(file.filePath()) + "'")
        self.settings.setValue(EnvSwitcherApp.SETTING_LAST_OPENED_FILE_PATH, file.filePath())


def main(headless: bool=False, env_id: str=None, config_file_path: str=None):
    """
    Main entry point both for headless and GUI mode

    :param headless:
    :param env_id:
    :param config_file_path:
    :return:
    """
    print('*** ENVSWITCH <' + get_version() + '> ***')

    # create the application (the frame around everything), passing in the possible commandline arguments
    app = EnvSwitcherApp(headless, sys.argv[1:], env_id=env_id, config_file_path=config_file_path)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
