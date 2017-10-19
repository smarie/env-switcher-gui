import sys

import os
from abc import abstractmethod
from contextlib import ContextDecorator
from functools import partial
from traceback import format_exception
from typing import Dict, List
from warnings import warn

if getattr(sys, 'frozen', False):
    # frozen (cx_Freeze) mode: trick to be sure that Qt loads correctly even when the cli is called form another folder
    cur = os.getcwd()
    os.chdir(os.path.abspath(os.path.dirname(sys.executable)))
    # we can also set the icon path correctly
    _abs_icon_path = os.path.join(os.path.abspath(os.path.dirname(sys.executable)), 'resources', 'envswitch.png')
else:
    # set the icon path for non-frozen mode
    _abs_icon_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'resources', 'envswitch.png')

from PyQt5.QtCore import pyqtSignal, QObject, QFileInfo, QSettings
from PyQt5.QtGui import QCloseEvent, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QAbstractButton, QDialogButtonBox, QWidget, \
    QGridLayout, QFormLayout, QLabel, QLineEdit, QErrorMessage, QMessageBox
if getattr(sys, 'frozen', False):
    # frozen : set cwd back to normal now that Qt has been loaded
    os.chdir(cur)

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


class StateSignals(QObject):
    """
    see http://pyqt.sourceforge.net/Docs/PyQt5/signals_slots.html#PyQt5.QtCore.pyqtSignal : we have to create an
    independent class

    We define three signals here
    * current_config_changed_or_saved that will be triggered whenever the current configuration is modified
    (for example, the user edits the form), or is saved.
    * current_file_changed that will be triggered whenever the current opened file changes (a new file is opened
    for example).
    * settings_changed that will be triggered whenever some settings changes
    """
    current_config_changed_or_saved = pyqtSignal(QObject)  # the arg is the cause
    current_file_changed = pyqtSignal()  # QFileInfo


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
        self.signals = StateSignals()

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
        self.signals.current_file_changed.emit()  # QFileInfo(new_conf_file_path)
        self.signals.current_config_changed_or_saved.emit(None)

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
                self.signals.current_config_changed_or_saved.emit(None)
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
        self.signals.current_config_changed_or_saved.emit(None)

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
        self.signals.current_config_changed_or_saved.emit(cause)

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

    def apply(self, env_id: str, whole_machine: bool):
        """
        Applies the given environment

        :param env_id:
        :param whole_machine: a boolean indicating if environment applications should apply to whole machine
        (True) or to local user (False)
        :return:
        """
        self.current_configuration.apply(env_id, whole_machine=whole_machine)


class PopupOnError(ContextDecorator):
    """A context manager to catch exceptions and disaplying popups"""

    def __init__(self, parent: QWidget):
        self.parent = parent

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        """ If an exception has been raised, display a popup"""
        if type is not None:
            # there was an exception, display a popup
            QMessageBox.critical(self.parent, "Application",
                                 "An unexpected error happened while executing this action: '" + str(value) + "'\n\n"
                                 "Traceback: " + ''.join(format_exception(type, value, traceback)),
                                 QMessageBox.NoButton)


class FileAwareMixin(QWidget):
    """
    A helper class for main windows that handle files.
    It performs most of the logic and catches exceptions in Popups
    """

    def setup_file_aware(self, file_type_short: str, file_extensions: List[str], enable_when_dirty: List[QObject],
                         open_signals: List, save_signals: List, save_as_signals: List, cancel_signals: List,
                         quit_signals: List):
        """
        This function needs to be called once in order to configure the object
        :param enable_when_dirty:
        :return:
        """
        self.file_type_short = file_type_short
        self.file_extensions = file_extensions
        self.enable_when_dirty = enable_when_dirty

        for signal in open_signals:
            signal.connect(self.lslot_open)

        for signal in save_signals:
            signal.connect(self.lslot_save)

        for signal in save_as_signals:
            signal.connect(self.lslot_save_as)

        for signal in cancel_signals:
            signal.connect(self.lslot_cancel_modifications)

        for signal in quit_signals:
            signal.connect(self.lslot_quit)


    def rslot_current_file_changed(self):  # , file: QFileInfo=None
        """
        This right slot should be called whenever the file has been changed.
        We have to recreate the tabs view and update the title bar
        :return:
        """
        with PopupOnError(self):
            # refresh if needed
            self.refresh_view_on_file_change()

            # refresh the title bar
            self.setWindowFilePath(self.get_current_file())

    @abstractmethod
    def get_current_file(self) -> str:
        pass

    @abstractmethod
    def refresh_view_on_file_change(self):
        pass

    def rslot_current_file_contents_changed_or_saved(self, cause=None):
        """
        Should be called whenever the current contents is changed or saved.
        * refreshes all QLineEdit widgets in the tabs
        * check the 'dirtiness' and update the window title, menu bar and buttons accordingly
        :return:
        """
        with PopupOnError(self):
            # refresh if needed
            self.refresh_view_on_file_contents_changed_or_saved(cause)

            # Update several widgets' status according to dirtiness state
            is_dirty = self.is_dirty()
            self.setWindowModified(is_dirty)
            for item in self.enable_when_dirty:
                item.setEnabled(is_dirty)

    @abstractmethod
    def refresh_view_on_file_contents_changed_or_saved(self, cause):
        pass

    @abstractmethod
    def is_dirty(self) -> bool:
        pass

    def lslot_open(self):
        """
        Called by the view when user selects File > Open...
        :return:
        """
        if self.maybe_save_modifications_before_continuing():
            with PopupOnError(self):
                # ask the user to select a configuration file to open
                try:
                    file_path, _ = QFileDialog.getOpenFileName(self, caption='Open a ' + self.file_type_short
                                                               + ' File', filter=self.file_type_short
                                                               + " files (" + ' '.join(self.file_extensions) + ")")

                    # 'cancel' will return without exception but with an empty config_file_path
                    if file_path == '':
                        print('User cancelled opening file.')
                        return
                except FileNotFoundError:
                    # 'exit' button press will raise a FileNotFoundError
                    print('User cancelled opening file.')
                    return

                # call the logic finally
                self.open(file_path)

    @abstractmethod
    def open(self, file_path):
        pass

    def lslot_save(self):
        """
        Called by the view when user selects File > Save, or CTRL+S, or clicks on 'Save' button.
        It tries to save the file to disk.
        In case of failure, it triggers the 'save as' action
        :return:
        """
        try:
            with PopupOnError(self):
                self.save()
                return True

        except Exception as e:
            return self.lslot_save_as()

    @abstractmethod
    def save(self):
        pass

    def lslot_save_as(self):
        """
        Called by the view when the user clicks on "save as".
        :return:
        """
        try:
            # popup 'save as', including the checker "file already exists - want to overwrite ?"
            new_file_path, _ = QFileDialog.getSaveFileName(parent=self,
                                                           caption='Save ' + self.file_type_short + ' File As...',
                                                           filter=self.file_type_short + " files ("
                                                           + ' '.join(self.file_extensions) + ")")
            # 'cancel' will return without exception but with an empty config_file_path
            if new_file_path == '':
                print('User cancelled saving file.')
                return False

            # save
            with PopupOnError(self):
                self.save_as(new_file_path)
                return True

        except FileNotFoundError:
            # 'exit' button press will raise a FileNotFoundError
            print('User cancelled saving file.')
            return False

    @abstractmethod
    def save_as(self, file_path):
        pass

    def lslot_cancel_modifications(self):
        """
        Called by the view when user clicks on 'Cancel' button.
        :return:
        """
        with PopupOnError(self):
            self.cancel_current_modifications()

    @abstractmethod
    def cancel_current_modifications(self):
        pass

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
        if not self.is_dirty():
            return True
        else:
            button_reply = QMessageBox.warning(self, "Application",
                                               "The document has been modified.\nDo you want to save your changes?",
                                               QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            if button_reply == QMessageBox.Save:
                # try to save and cancel if not successful
                # note: do not wrap with popup on error here, already done
                return self.lslot_save()
            elif button_reply == QMessageBox.Cancel:
                # cancel the operation
                return False
            else:
                # discard the changes and continue
                with PopupOnError(self):
                    self.cancel_current_modifications()
                return True


class EnvSwitcherView(QMainWindow, Ui_MainWindow, FileAwareMixin):
    """
    The 'View' in the MVC pattern.

    The static design is generated from qt_designer in qt_design.py. The rest concerns
    * how the view is dynamically created when a new model is loaded (see recreate_tabs_view)
    * the slots related to file menu actions, See also Main window tutorial:
    http://doc.qt.io/qt-5/qtwidgets-mainwindows-application-example.html

    """

    ENV_TAB_WIDGET_PREFIX = "envTab_"
    TARGET_IS_WHOLE_MACHINE = 'target_is_whole_machine'

    # TODO allow user to add & rename tabs see https://stackoverflow.com/questions/44450775/pyqt-gui-with-multiple-tabs

    def __init__(self, apply_environment_hook, set_environment_target_hook, initial_config: Dict):
        """
        Creates the main application's window.
        The controller should provide method hooks for all main events.
        :param apply_environment_hook: a function that will be called when the user clicks on 'apply'. It should have
        one input that is the environment id
        :param set_environment_target_hook: a function that will be called when the user changes the 'environment
        target' setting. It should have one boolean input indicating if the target is the whole machine or not.
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
        # -- file-related: we use this helper class
        self.setup_file_aware(file_type_short='Configuration', file_extensions=['*.yml', '*.yaml'],
                              enable_when_dirty=[self.actionSave, self.mainButtonBox.buttons()[0],
                                                 self.mainButtonBox.buttons()[1]],
                              open_signals=[self.actionOpen.triggered],
                              save_signals=[self.mainButtonBox.accepted, self.actionSave.triggered],
                              save_as_signals=[self.actionSave_As.triggered],
                              cancel_signals=[self.mainButtonBox.rejected],
                              quit_signals=[self.actionQuit.triggered]
                              )

        # -- apply current environment
        self.apply_environment_hook = apply_environment_hook
        def clicked_hook(button: QAbstractButton):
            if button.foregroundRole() == QDialogButtonBox.ApplyRole:
                self.lslot_apply_clicked()
        self.mainButtonBox.clicked.connect(clicked_hook)

        # -- set environment
        # correct initial state
        if self.TARGET_IS_WHOLE_MACHINE in initial_config.keys():
            if initial_config[self.TARGET_IS_WHOLE_MACHINE]:
                self.actionSet_for_local_machine.setChecked(True)
                self.actionSet_for_current_user.setChecked(False)
            else:
                self.actionSet_for_local_machine.setChecked(False)
                self.actionSet_for_current_user.setChecked(True)

        # the 'interlock' between the two
        self.actionSet_for_current_user.triggered.connect(partial(self.actionSet_for_local_machine.setChecked, False))
        self.actionSet_for_local_machine.triggered.connect(partial(self.actionSet_for_current_user.setChecked, False))

        # call the hook
        self.actionSet_for_current_user.triggered.connect(partial(set_environment_target_hook, whole_machine=False))
        self.actionSet_for_local_machine.triggered.connect(partial(set_environment_target_hook, whole_machine=True))

        # *** the list of value editors that will be used in rslot_current_file_contents_changed_or_saved
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
        state.signals.current_config_changed_or_saved.connect(self.rslot_current_file_contents_changed_or_saved)
        state.signals.current_file_changed.connect(self.rslot_current_file_changed)
        self.state = state

        # refresh the tabs and current file name
        self.rslot_current_file_changed()

        # refresh the buttons status according to 'dirtiness' of the state
        self.rslot_current_file_contents_changed_or_saved()

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

    def get_current_file(self):
        """ Overridden from FileAwareMixin """
        return self.state.current_config_file

    def refresh_view_on_file_change(self):
        """ Overridden from FileAwareMixin """
        self.recreate_tabs_view(self.state)

    def refresh_view_on_file_contents_changed_or_saved(self, cause):
        """
        Called whenever the current configuration data is changed or saved.
        * refreshes all QLineEdit widgets in the tabs
        * check the 'dirtiness' and update the window title, menu bar and buttons accordingly
        :return:
        """
        # Refresh all the editors' text except the one that triggered the mod (otherwise it will loose focus)
        for var_value_editor in self.line_editors:
            if cause != var_value_editor:
                var_value_editor.setText(
                    self.state.get_env_variables(var_value_editor.env_id)[var_value_editor.var_name])

    def is_dirty(self):
        """ Overriden from FileAwareMixin """
        return self.state.is_dirty()

    def open(self, file_path):
        """ Overridden from FileAwareMixIn """
        if self.state is None:
            raise Exception('Internal error - This view does not have a bound state !!! ')
        else:
            # this will automatically load the corresponding config
            self.state.current_config_file = file_path

    def save(self):
        """ Overridden from FileAwareMixIn """
        self.state.save_modifications()

    def save_as(self, file_path):
        """ Overridden from FileAwareMixIn """
        self.state.save_as(new_file_path=file_path, overwrite=True)

    def cancel_current_modifications(self):
        """ Overridden from FileAwareMixIn """
        self.state.cancel_modifications()

    def lslot_apply_clicked(self):
        """
        Called by the view whenever the apply button is pushed.
        :param env_id:
        :return:
        """
        with PopupOnError(self):
            current_tab_widget = self.envsTabWidget.currentWidget()
            env_id = current_tab_widget.objectName()[len(EnvSwitcherView.ENV_TAB_WIDGET_PREFIX):]
            self.apply_environment_hook(env_id)


class FileRestoreException(Exception):
    pass


class EnvSwitcherAppHeadless(QApplication):
    """
    A 'headless' version of the envswitcher app. It only contains the state and settings, and provides some API to
    interact with them
    """

    SETTING_LAST_OPENED_FILE_PATH = 'configuration_file_path'
    SETTING_TARGET_IS_WHOLE_MACHINE = EnvSwitcherView.TARGET_IS_WHOLE_MACHINE

    def __init__(self, argv: list=None, config_file_path: str=None):
        """

        :param argv:
        :param config_file_path: the alternate config file to use instead of the last one loaded by the app
        """
        # parent (QApplication) init
        super(EnvSwitcherAppHeadless, self).__init__(argv or [])

        # ** Application / Controller (self) **
        # -- some qt-related fields that are useful to all the views created by the application
        self.setOrganizationName('smarie')
        self.setOrganizationDomain('github.com')
        self.setApplicationDisplayName('EnvSwitch')
        self.setApplicationName('envswitch')  # defaults to the exec name, but we want the same across entry points
        # print('Icon path: ' + _abs_icon_path)
        self.setWindowIcon(QIcon(_abs_icon_path))
        self.settings = QSettings()

        # set to none explicitly so that subclasses may see when init has failed
        self.internal_state = None

        if config_file_path is None:
            # config_file_path = None means 'open the last opened file'
            config_file_path = self.get_last_opened_file()
            try:
                print("Restoring last open file: " + config_file_path)
                self.internal_state = EnvSwitcherState(configuration_file_path=config_file_path)
                print("Opened file successfully: " + config_file_path)

            except Exception as e:  # FileNotFoundError, PermissionError, CouldNotRestoreStateException
                raise FileRestoreException("Could not restore last open file : " + str(e)).with_traceback(
                    e.__traceback__)
        else:
            # load the specified file
            try:
                print("Opening file: " + config_file_path)
                self.internal_state = EnvSwitcherState(configuration_file_path=config_file_path)
                print("Opened file successfully: " + config_file_path)

            except Exception as e:  # FileNotFoundError, PermissionError, CouldNotRestoreStateException
                raise FileRestoreException("Could not open file : " + str(e)).with_traceback(e.__traceback__)

    def get_current_config_file_path(self) -> str:
        """

        :return: the path to the currently loaded file
        """
        return self.internal_state.current_config_file

    def get_current_config(self) -> GlobalEnvsConfig:
        """
        Returns the currently loaded configuration. You can use it to get the list of available environments for
        example, or to apply a given environment.

        :return: the currently loaded configuration
        """
        return self.internal_state.current_configuration

    def get_last_opened_file(self):
        return self.settings.value(EnvSwitcherApp.SETTING_LAST_OPENED_FILE_PATH, type=str) or ''

    def _persist_last_opened_file(self, file_path):
        print("saving last open file path for future launches : '" + file_path + "'")
        self.settings.setValue(EnvSwitcherApp.SETTING_LAST_OPENED_FILE_PATH, file_path)

    def persist_last_opened_file(self):
        """
        Persists the currently opened file in the application's settings so that the next time it will load, it will
        remember it
        :return:
        """
        file_path = self.internal_state.current_config_file
        self._persist_last_opened_file(file_path)

    def set_target_whole_machine(self, whole_machine: bool):
        self.settings.setValue(EnvSwitcherApp.SETTING_TARGET_IS_WHOLE_MACHINE, whole_machine)

    def is_target_whole_machine(self):
        return self.settings.value(EnvSwitcherApp.SETTING_TARGET_IS_WHOLE_MACHINE, type=bool) or False

    def apply_environment(self, env_id):
        self.internal_state.apply(env_id, whole_machine=self.is_target_whole_machine())


class EnvSwitcherApp(EnvSwitcherAppHeadless):
    """
    The main EnvSwitch Application. (the 'Controller' in the MVC pattern)
    * creates (and updates ?) views
    * receives input events from the view
    * query & modifies the internal_state

    It is responsible to handle the current state, map it to persistence layer, and refresh the views.
    """

    def __init__(self, argv, config_file_path: str = None):
        """
        Initializes the application in gui mode

        :param argv: generic Qt arguments for the underlying Qt application
        :param config_file_path: the alternate config file to use instead of the last one loaded by the app
        """

        # ** Application + Model **
        try:
            # Super: init app and load settings, and try to open last known file
            super(EnvSwitcherApp, self).__init__(argv, config_file_path=config_file_path)
        except FileRestoreException:
            # we will handle that below
            pass

        # ** View **
        print("Creating Main View")
        self.ui = EnvSwitcherView(apply_environment_hook=self.apply_environment,
                                  set_environment_target_hook=self.set_target_whole_machine,
                                  initial_config={self.SETTING_TARGET_IS_WHOLE_MACHINE: self.is_target_whole_machine()})
        self.ui.show()  # Do this now, so that the 'open file' dialog below can show

        # --Handle the case where no configuration file could be loaded in the constructor
        if self.internal_state is None:
            # this means that an error happened when opening
            # we have to ask the user to open a configuration file
            print("We need a configuration file, ask the user")
            loaded = False
            # TODO one days when we support the 'new' function (empty document) this will be removed.
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
                    self._persist_last_opened_file(config_file_path)
                    loaded = True
                except TypeError as e:
                    warn(str(e))
                except FileNotFoundError as f:
                    warn(str(f))

        # keep the application informed of events that should be persisted in the app settings (across reboots)
        # noinspection PyUnresolvedReferences
        self.internal_state.signals.current_file_changed.connect(self.persist_last_opened_file)

        # connect the view to the model
        self.ui.set_model(self.internal_state)
        print('Application ready')


def main(config_file_path: str=None):
    """
    Main entry point for GUI mode

    :param config_file_path: optional - to load the gui with a given conf file instead of the last opened one
    :return:
    """
    print('*** ENVSWITCH <' + get_version() + '> ***')

    # create the application (the frame around everything), passing in the possible commandline arguments
    app = EnvSwitcherApp(sys.argv[1:], config_file_path=config_file_path)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
