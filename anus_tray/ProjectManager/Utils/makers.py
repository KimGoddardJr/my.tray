import os
import sys
import errno
import shutil
import socket
from collections import OrderedDict
from time import gmtime, strftime, asctime
import math



class CreationMethods:

    # debug functions
    @staticmethod
    def makedir(folder_path):
        try:
            os.makedirs(folder_path)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
            pass

    @staticmethod
    def CopyTreeFromDict(tree_zip):

        for group in tree_zip:
            # if os.path.exists(dest):
            #     print(dest + " exists already")
            #     pass
            # else:
            src = group[0]
            dest = group[1]
            try:
                shutil.copytree(src, dest)
            except shutil.Error as se:
                print(se)
                print("Something went wrong...")
                raise


class NumberMethods:
    
    @staticmethod
    def IntToBool(int_value):
        if int_value == 1:
            return True
        elif int_value == 0:
            return False
        else:
            pass

    @staticmethod
    def add_one(value):
        value += 1
        return value

    @staticmethod
    def now():
        # Returns preformated time for now.
        return strftime("%H%M%S", gmtime())

    @staticmethod
    def HostAndDateNow():
        date = asctime()
        datesplit = date.split(" ")
        time = datesplit[4]
        timesplit = time.split(":")
        cur_datetime = f"{datesplit[3]}{datesplit[1]}_{timesplit[0]}{timesplit[1]}{timesplit[2]}_{datesplit[-1]}"
        client_now = f"{socket.gethostname()}_{cur_datetime}"

        return client_now

    @staticmethod
    # Show/Hide the delay-time options
    def delaytime(index, delay_layout):
        i = 0
        items = delay_layout.count()
        while i < items:
            item = delay_layout.itemAt(i).widget()
            if item:
                item.setVisible(index == 2)
            i = i + 1


class ExecuteMethods:
    def Py2(self):
        if sys.version_info <= (3, 0):
            return True

    def Py3(self):
        if sys.version_info >= (2, 9):
            return True

    def DictIterCopy(self, dict, copy=False):

        if self.Py2():
            if copy:
                dict_iter_copy = list(dict.iteritems())
            else:
                dict_iter_copy = dict.iteritems()
        elif self.Py3():
            if copy:
                dict_iter_copy = list(dict.items())
            else:
                dict_iter_copy = dict.items()

        return dict_iter_copy