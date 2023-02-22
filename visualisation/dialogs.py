import numpy as np
from visualisation.windowsUI import ChangeValueDialogBase, ShapeInputDialogBase
from PyQt5.QtWidgets import QTableWidgetItem


class ShapeInputDialog(ShapeInputDialogBase):
    
    @staticmethod
    def getShape():
        dialog = ShapeInputDialog()
        dialog.exec()
        x = dialog.spinBoxOfShapeX.value()
        y = dialog.spinBoxOfShapeY.value()
        z = dialog.spinBoxOfShapeZ.value()
        shape = (x, y, z)
        order = dialog.comboBoxOfOrder.currentText()
        return shape, order


class ChangeValueDialog(ChangeValueDialogBase):
    
    @staticmethod
    def getChangedArray(array):
        changedArray = array.copy()
        unique, counts = np.unique(array, return_counts=True)
        dialog = ChangeValueDialog()
        dialog.tableWidgetOfUniqueValues.setRowCount(unique.size)
        dialog.tableWidgetOfUniqueValues.setColumnCount(2)
        dialog.tableWidgetOfUniqueValues.setHorizontalHeaderLabels(['Value', 'Counts'])
        for i in range(unique.size):
            dialog.tableWidgetOfUniqueValues.setItem(i, 0, QTableWidgetItem(str(unique[i])))
            dialog.tableWidgetOfUniqueValues.setItem(i, 1, QTableWidgetItem(str(counts[i])))
        
        def itemChanged(item):
            if not item.column():
                newValue = float(item.text())
                index = item.row()
                changedArray[array == unique[index]] = newValue
        
        dialog.tableWidgetOfUniqueValues.itemChanged.connect(itemChanged)
        if dialog.exec():
            return changedArray

