# coding: utf-8

import csv
import ctypes
import datetime
import getpass
import json
import logging
import os
import platform
import re
import subprocess
import sys
import time
from string import Template
from threading import Thread, Event

import uno
import unohelper
from com.sun.star.util import Time, Date, DateTime
from com.sun.star.beans import PropertyValue, NamedValue
from com.sun.star.datatransfer import XTransferable, DataFlavor
from org.universolibre.EasyDev import XTools
from org.universolibre.EasyDev import XArrays
from easydev import comun
from easydev.comun import LODefault

from easydev.setting import (
    BUTTONS_YES_NO,
    CLIPBOARD_FORMAT_TEXT,
    LOCATION_USER,
    NAME_EXT,
    NODE,
    NODE_CONFIG,
    OS,
    PY2,
    PYTHON,
    QUERYBOX,
    VERSION,
    WIN,
    YES,
)


if PY2:
    str = unicode

log = logging.getLogger(NAME_EXT)
stop_thread = {}


def call_macro(factory, macro, doc, args):
    #~ https://wiki.openoffice.org/wiki/Documentation/DevGuide/Scripting/Scripting_Framework_URI_Specification
    if not macro.Library:
        macro.Library = 'Standard'
    if not macro.Language:
        macro.Language = PYTHON
    if macro.Language == 'Basic':
        if not macro.Location:
            macro.Location = 'application'
    else:
        if not macro.Location:
            macro.Location = LOCATION_USER
    if macro.Language == PYTHON:
        main = 'vnd.sun.star.script:{}.py${}?language=Python&location={}'.format(
            macro.Library, macro.Name, macro.Location)
    elif macro.Language == 'Basic':
        main = 'vnd.sun.star.script:{}.{}.{}?language=Basic&location={}'.format(
            macro.Library, macro.Module, macro.Name, macro.Location)
    elif macro.Language == 'BeanShell':
        main = 'vnd.sun.star.script:{}.{}.bsh?language=BeanShell&location={}'.format(
            macro.Library, macro.Name, macro.Location)
    elif macro.Language == 'Java':
        main = 'vnd.sun.star.script:{}.{}?language=Java&location={}'.format(
            macro.Library, macro.Name, macro.Location)
    elif macro.Language == 'JavaScript':
        main = 'vnd.sun.star.script:{}.{}.js?language=JavaScript&location={}'.format(
            macro.Library, macro.Name, macro.Location)
    #~ log.info(main)
    if macro.Location=='document':
        script = doc.getScriptProvider().getScript(main)
    else:
        script = factory.createScriptProvider('').getScript(main)
    return script.invoke(args, None, None)[0]


class TextTransferable(unohelper.Base, XTransferable):
    """Keep clipboard data and provide them."""

    def __init__(self, text):
        df = DataFlavor()
        df.MimeType = CLIPBOARD_FORMAT_TEXT
        df.HumanPresentableName = "encoded text utf-16"
        self.flavors = [df]
        self.data = [text]

    def getTransferData(self, flavor):
        if not flavor:
            return
        for i, f in enumerate(self.flavors):
            if flavor.MimeType == f.MimeType:
                return self.data[i]
        return

    def getTransferDataFlavors(self):
        return tuple(self.flavors)

    def isDataFlavorSupported(self, flavor):
        if not flavor:
            return False
        mtype = flavor.MimeType
        for f in self.flavors:
            if mtype == f.MimeType:
                return True
        return False


class TimerThread(Thread):

    def __init__(self, event, wait, factory, macro, doc, args):
        Thread.__init__(self)
        self.stopped = event
        self.wait = wait
        self.factory = factory
        self.macro = macro
        self.doc = doc
        self.args = args

    def run(self):
        log.info('Timer started... {}'.format(self.macro.Name))
        while not self.stopped.wait(self.wait):
            call_macro(self.factory, self.macro, self.doc, self.args)
        log.info('Timer stopped... {}'.format(self.macro.Name))


class Tools(XTools, LODefault):
    VERSION = VERSION
    OS = OS
    LANGUAGE = ''
    APP_NAME = ''
    APP_VERSION = ''
    value = None

    def __init__(self, ctx, sm, desktop, toolkit):
        LODefault.__init__(self, ctx, sm, desktop, toolkit)
        self._init_vars()

    def _init_vars(self):
        self.LANGUAGE = self._get_language()
        self.APP_NAME = self._get_app_name()
        self.APP_VERSION = self._get_app_version()
        return

    def _get_language(self):
        key = 'ooLocale'
        node = 'org.openoffice.Setup/L10N/'
        data = self._get_config(key, node)
        if data:
            data = data.split('-')[0]
        return data

    def _get_app_name(self):
        key = 'ooName'
        node = 'org.openoffice.Setup/Product'
        data = self._get_config(key, node)
        if data:
            data = data.split('-')[0]
        return data

    def _get_app_version(self):
        key = 'ooSetupVersion'
        node = 'org.openoffice.Setup/Product'
        data = self._get_config(key, node)
        if data:
            data = data.split('-')[0]
        return data

    def _get_config(self, key, node_name):
        name = 'com.sun.star.configuration.ConfigurationProvider'
        cp = self._create_instance(name)
        node = PropertyValue()
        node.Name = 'nodepath'
        node.Value = node_name
        try:
            ca = cp.createInstanceWithArguments(
                'com.sun.star.configuration.ConfigurationAccess', (node,))
            if ca and (ca.hasByName(key)):
                data = ca.getPropertyValue(key)
            return data
        except Exception as e:
            log.debug(e)
            return ''

    def getSizeScreen(self):
        if OS == WIN:
            user32 = ctypes.windll.user32
            res = '{}x{}'.format(
                user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
        else:
            args = 'xrandr | grep "\*" | cut -d" " -f4'
            res = subprocess.check_output(args, shell=True).decode()
        return res.strip()

    def getInfoPC(self):
        """
            https://docs.python.org/3.3/library/platform.html
            Get info PC:
            name user,
            name pc,
            system/OS name,
            machine type,
            Returns the (real) processor name
            string identifying platform with as much useful information as possible,
        """
        info = (
            getpass.getuser(),
            platform.node(),
            platform.system(),
            platform.machine(),
            platform.processor(),
            platform.platform(),
        )
        return info

    def question(self, title, message):
        """ Create message box
            type_msg: infobox, warningbox, errorbox, querybox, messbox
        """
        parent = self.toolkit.getDesktopWindow()
        mb = self.toolkit.createMessageBox(
            parent, QUERYBOX, BUTTONS_YES_NO, title, message)
        return YES == mb.execute()

    def render(self, template, data):
        data = comun.to_dict(data)
        s = Template(template)
        return s.safe_substitute(**data)

    def format(self, template, data):
        """
            https://pyformat.info/
        """
        if isinstance(data, tuple):
            if isinstance(data[0], tuple):
                data = comun.to_dict(data, True)
                result = template.format(**data)
            else:
                data = [comun.to_date(v) for v in data]
                result = template.format(*data)
        else:
            result = template.format(comun.to_date(data))
        return result

    def getPath(self, name='Work'):
        """
            Return de path name in config
            http://api.libreoffice.org/docs/idl/ref/interfacecom_1_1sun_1_1star_1_1util_1_1XPathSettings.html
        """
        if not name:
            name = 'Work'
        path = self._create_instance('com.sun.star.util.PathSettings')
        return comun.path_to_os(getattr(path, name))

    def getPathInfo(self, path):
        return comun.get_path_info(path)

    def pathJoin(self, paths):
        return os.path.normpath(os.path.join(*paths))

    def getFolder(self, init_folder=''):
        if init_folder:
            init_folder = comun.path_to_url(init_folder)
        else:
            init_folder = comun.path_to_url(self.getPath())
        folder = self._create_instance('com.sun.star.ui.dialogs.FolderPicker')
        folder.setDisplayDirectory(init_folder)
        if folder.execute():
            return comun.path_to_os(folder.getDirectory())
        else:
            return ''

    def getSelectedFiles(self, init_folder, multiple, filters):
        """
            init_folder: folder default open
            multiple: True for multiple selected
            filters: Example
            (
                ('XML', '*.xml'),
                ('TXT', '*.txt'),
            )
        """
        if init_folder:
            init_folder = comun.path_to_url(init_folder)
        else:
            init_folder = comun.path_to_url(self.getPath())

        folder = self._create_instance('com.sun.star.ui.dialogs.FilePicker')
        folder.setDisplayDirectory(init_folder)
        folder.setMultiSelectionMode(multiple)
        if filters:
            folder.setCurrentFilter(filters[0][0])
            for f in filters:
                folder.appendFilter(f[0], f[1])

        if folder.execute():
            files = folder.getSelectedFiles()
            if multiple:
                return tuple([comun.path_to_os(f) for f in files])
            else:
                return comun.path_to_os(files[0])
        else:
            return ""

    def getFiles(self, path, ext):
        paths = []
        for folder, _, files in os.walk(path):
            pattern = re.compile('\.{}'.format(ext), re.IGNORECASE)
            paths += [os.path.join(folder, f) for f in files if pattern.search(f)]
        return tuple(paths)

    def fileOpen(self, path, mode='r', array=False):
        data = ''
        if not mode:
            mode = 'r'
        path = comun.path_to_os(path)
        with open(path, mode) as f:
            if array:
                data = tuple(f.read().splitlines())
            else:
                data = f.read()
        return data

    def fileSave(self, path, mode='w', data=None):
        if not mode:
            mode = 'w'
        if not data:
            return
        path = comun.path_to_os(path)
        with open(path, mode) as f:
            f.write(data)
        return

    def execute(self, args, wait):
        if wait:
            res = subprocess.check_output(' '.join(args), shell=True).decode()
            return res
        else:
            subprocess.Popen(args)
        return

    def getConfig(self, key):
        name = 'com.sun.star.configuration.ConfigurationProvider'
        cp = self._create_instance(name)
        node = PropertyValue()
        node.Name = 'nodepath'
        node.Value = NODE
        try:
            ca = cp.createInstanceWithArguments(
                'com.sun.star.configuration.ConfigurationAccess', (node,))
            if ca and (ca.hasByName(NODE_CONFIG)):
                data = ca.getPropertyValue(NODE_CONFIG)
                if not data:
                    return data
                data = json.loads(data)
                if key:
                    value = data.get(key, '')
                    if isinstance(value, list):
                        return tuple(value)
                    else:
                        return value
                else:
                    return data
            return
        except Exception as e:
            log.debug(e)
            return ''

    def setConfig(self, key, value):
        name = 'com.sun.star.configuration.ConfigurationProvider'
        cp = self._create_instance(name)
        node = PropertyValue()
        node.Name = 'nodepath'
        node.Value = NODE
        #~ print (NODE)
        try:
            config_writer = cp.createInstanceWithArguments(
                'com.sun.star.configuration.ConfigurationUpdateAccess', (node,))
            data = self.getConfig('')
            if not data:
                data = {}
            data[key] = value
            new_values = json.dumps(data)
            config_writer.setPropertyValue(NODE_CONFIG, new_values)
            config_writer.commitChanges()
            return True
        except Exception as e:
            log.error(e, exc_info=True)
            return False

    def getClipboard(self):
        df = None
        text = ''
        sc = self._create_instance(
            'com.sun.star.datatransfer.clipboard.SystemClipboard')
        transferable = sc.getContents()
        data = transferable.getTransferDataFlavors()
        for df in data:
            if df.MimeType == CLIPBOARD_FORMAT_TEXT:
                break
        if df:
            text = transferable.getTransferData(df)
        return text

    def setClipboard(self, text):
        ts = TextTransferable(text)
        sc = self._create_instance(
            'com.sun.star.datatransfer.clipboard.SystemClipboard')
        sc.setContents(ts, None)
        return

    def copy(self, doc):
        comun.copy(doc)
        return

    def paste(self, doc):
        return comun.paste(doc)

    def getEpoch(self):
        now = datetime.datetime.now()
        return int(time.mktime(now.timetuple()))

    def callMacro(self, macro, args):
        doc = self.desktop.getCurrentComponent()
        factory = self._create_instance(
            'com.sun.star.script.provider.MasterScriptProviderFactory', False)
        if macro.Thread:
            thread = Thread(target=call_macro, args=(factory, macro, doc, args))
            thread.start()
            return
        else:
            return call_macro(factory, macro, doc, args)

    def timer(self, name, wait, macro, args):
        global stop_thread
        doc = self.desktop.getCurrentComponent()
        factory = self._create_instance(
            'com.sun.star.script.provider.MasterScriptProviderFactory', False)
        stop_thread[name] = Event()
        thread = TimerThread(stop_thread[name], wait, factory, macro, doc, args)
        thread.start()
        return

    def stopTimer(self, name):
        global stop_thread
        stop_thread[name].set()
        del stop_thread[name]
        return

    def exportCSV(self, path, data, options):
        """
            See https://docs.python.org/3.3/library/csv.html#csv.writer
        """
        path = comun.path_to_os(path)
        if options:
            config = comun.to_dict(options)
        try:
            with open(path, 'w') as f:
                if options:
                    if not 'lineterminator' in config:
                        config['lineterminator'] = '\n'
                    writer = csv.writer(f, **config)
                else:
                    writer = csv.writer(f, lineterminator='\n')
                writer.writerows(data)
            return True
        except:
            log.debug('CSV', exc_info=True)
            return False

    def importCSV(self, path, options):
        """
            See https://docs.python.org/3.3/library/csv.html#csv.reader
        """
        path = comun.path_to_os(path)
        if options:
            config = comun.to_dict(options)
        try:
            with open(path) as f:
                if options:
                    data = tuple(csv.reader(f, **config))
                else:
                    data = tuple(csv.reader(f))
            array = tuple(tuple(r) for r in data)
            return array
        except:
            log.debug('CSV', exc_info=True)
            return ()

    def zip(self, source, target):
        if comun.isdir(source):
            comun.zip_dir(source, target)
        else:
            comun.zip_file(source, target)
        return

    def unzip(self, source, target, name):
        comun.unzip(source, target, name)
        return


class Arrays(XArrays):

    def __init__(self):
        pass

    def array(self, array, method, value):
        """
            Methods of list to Basic
        """
        res = None
        l = list(array)
        if method == 'insert':
            res = getattr(l, method)(*data)
        elif method == 'pop':
            res = getattr(l, method)(data)
            res = (tuple(l), res)
        elif method == 'remove_all':
            l = [i for i in array if i != data]
        elif method in ('reverse', 'sort'):
            res = getattr(l, method)()
        elif method == 'unique':
            l = list(set(l))
        elif method in ('len', 'max', 'min'):
            res = eval('{}({})'.format(method, l))
        elif method == 'slice':
            l = eval('{}{}'.format(l, data))
        elif method == 'exists':
            res = data in l
        else:
            res = getattr(l, method)(data)
        if res is None:
            return tuple(l)
        else:
            return res

    def append(self, array, value):
        l = list(array)
        l.append(value)
        return tuple(l)

    def delete(self, array, pos):
        l = list(array)
        del l[pos]
        return tuple(l)

    def slice(self, array, value):
        if value.startswith('[') and value.endswith(']'):
            t = eval('{}{}'.format(array, value))
        return t

    def extend(self, array1, array2):
        l = list(array1)
        l.extend(list(array2))
        return tuple(l)

    def multi(self, array, value):
        return array * value

    def unique(self, array):
        l = list(array)
        l = list(set(l))
        return tuple(l)

    def reverse(self, array):
        l = list(array)
        l.reverse()
        return tuple(l)

    def sorted(self, array, column):
        if isinstance(array[0], tuple):
            t = sorted(array, key=lambda x: x[column])
        else:
            t = sorted(array)
        return tuple(t)

    def insert(self, array, pos, value):
        l = list(array)
        l.insert(pos, value)
        return tuple(l)

    def pop(self, array, pos):
        l = list(array)
        r = l.pop(pos)
        return (tuple(l), r)

    def remove(self, array, value, all):
        l = list(array)
        if not all:
            l.remove(value)
        else:
            l = [i for i in array if i != value]
        return tuple(l)

    def len(self, array):
        return len(array)

    def min(self, array):
        return min(array)

    def max(self, array):
        return max(array)

    def average(self, array):
        s = self.sum(array)
        return s / float(len(array))

    def sum(self, array):
        return sum(int(i) for i in array if isinstance(i, (int, float)))

    def exists(self, array, value):
        return value in array

    def equal(self, array1, array2):
        return array1 == array2

    def count(self, array, value):
        l = list(array)
        r = l.count(value)
        return r

    def index(self, array, value):
        r = [i for i, v in enumerate(array) if v==value]
        if len(r) == 1:
            return r[0]
        else:
            return tuple(r)

    def intersection(self, array1, array2):
        s1 = set(array1)
        s2 = set(array2)
        s = s1.intersection(s2)
        return tuple(s)

    def union(self, array1, array2):
        s1 = set(array1)
        s2 = set(array2)
        s = s1.union(s2)
        return tuple(s)

    def symmetricDifference(self, array1, array2):
        s1 = set(array1)
        s2 = set(array2)
        s = s1.symmetric_difference(s2)
        return tuple(s)

    def difference(self, array1, array2):
        s1 = set(array1)
        s2 = set(array2)
        s = s1.difference(s2)
        return tuple(s)

    def getColumn(self, array, column):
        a = [row[column] for row in array]
        return tuple(a)

