# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'data_change_form.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(300, 360)
        self.ttab_tab_rbtn = QtWidgets.QRadioButton(Dialog)
        self.ttab_tab_rbtn.setGeometry(QtCore.QRect(165, 40, 105, 20))
        self.ttab_tab_rbtn.setObjectName("ttab_tab_rbtn")
        self.tab_rbtns = QtWidgets.QButtonGroup(Dialog)
        self.tab_rbtns.setObjectName("tab_rbtns")
        self.tab_rbtns.addButton(self.ttab_tab_rbtn)
        self.dead_tab_rbtn = QtWidgets.QRadioButton(Dialog)
        self.dead_tab_rbtn.setGeometry(QtCore.QRect(165, 10, 105, 20))
        self.dead_tab_rbtn.setObjectName("dead_tab_rbtn")
        self.tab_rbtns.addButton(self.dead_tab_rbtn)
        self.add_type_rbtn = QtWidgets.QRadioButton(Dialog)
        self.add_type_rbtn.setGeometry(QtCore.QRect(30, 10, 105, 20))
        self.add_type_rbtn.setObjectName("add_type_rbtn")
        self.type_rbtns = QtWidgets.QButtonGroup(Dialog)
        self.type_rbtns.setObjectName("type_rbtns")
        self.type_rbtns.addButton(self.add_type_rbtn)
        self.chg_type_rbtn = QtWidgets.QRadioButton(Dialog)
        self.chg_type_rbtn.setGeometry(QtCore.QRect(30, 40, 105, 20))
        self.chg_type_rbtn.setObjectName("chg_type_rbtn")
        self.type_rbtns.addButton(self.chg_type_rbtn)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.ttab_tab_rbtn.setText(_translate("Dialog", "Time Table"))
        self.dead_tab_rbtn.setText(_translate("Dialog", "Deadline"))
        self.add_type_rbtn.setText(_translate("Dialog", "Add"))
        self.chg_type_rbtn.setText(_translate("Dialog", "Change"))
