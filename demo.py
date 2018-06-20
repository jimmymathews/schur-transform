#!/usr/bin/python3

# x = np.array([ [[4,2],[3,2.1],[4,2.2]] , [[10,7.6],[10.2,7.6],[10.2,7]] , [[5,4],[5.5,4.5],[5.6,4.3]], [[4,4],[5,4.5],[5.1,4.1]]])
# x = np.array([ [[4,2],[3,2.1],[4,2.2]] , [[4,2],[3,2.1],[4,2.2]] , [[4,2],[3,2.1],[4,2.2]], [[4,2],[3,2.1],[4,2.2]]])
# x = np.array([ [[4,2],[4.01,2.1],[3.9,2.2]] , [[3.99,2.1],[3.7,2.1],[4.0,2.2]] , [[4.4,1.9],[4.3,1.8],[4.3,1.8]]])

import numpy as np
from schur_transform import schur_transform


x = np.array([ [[4,2],[4.01,2.1],[3.9,2.2]] , [[3.99,2.1],[3.7,2.1],[4.0,2.2]] , [[4.4,1.9],[4.3,1.8],[4.3,1.8]], [[4.6,2.0],[4.1,1.8],[4.3,1.7]],[[3.6,2.1],[4.5,2],[5,1]],[[3.0,2.2],[7,2.2],[5.6,1.2]]])
[components, amplitudes, characters] = schur_transform(x)
print("Amplitudes:  "+str(amplitudes))
print("Characters:  "+str(characters))
#print("Norm of total covariance tensor:  "+str(np.linalg.norm(amplitudes)))



### GUI demo
### keys:
###  p  place a point (on the left pane)
###  r  start/stop rotating (on the right pane; currently not a permanent effect)
###  c  clear the placed points (except 0)
###  1  start/stop placing basis element 1 (on the right pane)
###  2  start/stop placing basis element 2 (on the right pane)
###
### I couldn't quite figure out how to capture mouse events beyond basic motion, hence the key-driven action instead.

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.Point import Point
from pyqtgraph import ScatterPlotItem

class KeyPressWindow(pg.GraphicsWindow):
    sigKeyPress = QtCore.pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def keyPressEvent(self, ev):
        self.scene().keyPressEvent(ev)
        self.sigKeyPress.emit(ev)

class Tracker:
    def __init__(self):
        self.mode = 0
        self.leftPointX = 0
        self.leftPointY = 0
        self.needs_update = False
        self.basis1data=[5,0]
        self.basis2data=[0,5]
        self.reset_data()
        self.needs_clear = True

    def reset_data(self):
        self.x = [0]
        self.y = [0]
        self.tx = [0]
        self.ty = [0]

    def keyPressed(self,evt):
        # print(evt.key())
        if(evt.key()==80):
            self.x.append(self.leftPointX)
            self.y.append(self.leftPointY)
            self.needs_update = True
        if(evt.key()==50):
            if(self.mode !=1):
                self.mode=1
            else:
                self.mode=0
        if(evt.key()==49):
            if(self.mode !=2):
                self.mode = 2
            else:
                self.mode = 0
        if(evt.key()==82):
            if(self.mode !=3):
                self.mode = 3
            else:
                self.mode = 0
        if(evt.key()==67):
            self.reset_data()
            self.needs_clear = True

    def update_schur_profile(self):
        points          = [ [self.x[i],self.y[i]] for i in range(len(self.x))]
        points_deformed = [ [self.tx[i],self.ty[i]] for i in range(len(self.tx))]
        x = np.array([points, points_deformed])
        [self.components, self.amplitudes, characters] = schur_transform(x)

m = Tracker()

app = QtGui.QApplication([])
# win = pg.GraphicsWindow()
win = KeyPressWindow()
win.sigKeyPress.connect(m.keyPressed)
win.setWindowTitle('2-factor Schur transform')

p1 = win.addPlot(row=0, col=1)
p2 = win.addPlot(row=0, col=2)
label = win.addLabel('...',row=1, col=1)

p1.plot(m.x, m.y, symbolPen='w', pen=None)

# This is probably doing nothing
region = pg.LinearRegionItem()
region.setZValue(10)

p1.setAutoVisible(y=True)
p2.plot(m.tx,m.ty, symbolPen='w', pen=None)

p1.setXRange(-10,10)
p1.setYRange(-10,10)
p2.setXRange(-10,10)
p2.setYRange(-10,10)

def update():
    region.setZValue(10)
    minX, maxX = region.getRegion()

region.sigRegionChanged.connect(update)

def updateRegion(window, viewRange):
    rgn = viewRange[0]
    region.setRegion(rgn)

p1.sigRangeChanged.connect(updateRegion)

basis1=ScatterPlotItem([0,m.basis1data[0]],[0,m.basis1data[1]], pen='r')
basis2=ScatterPlotItem([0,m.basis2data[0]],[0,m.basis2data[1]], pen='r')

p2.addItem(basis1, ignoreBounds=True)
p2.addItem(basis2, ignoreBounds=True)

vb = p1.vb
vb2 = p2.vb

import math

def mouseMoved(evt):
    pos = evt[0]  ## using signal proxy turns original arguments into a tuple
    if p1.sceneBoundingRect().contains(pos):
        mousePoint = vb.mapSceneToView(pos)
        mx = mousePoint.x()
        my = mousePoint.y()
        index = int(mousePoint.x())
        m.leftPointX = mousePoint.x()
        m.leftPointY = mousePoint.y()
        if(m.needs_update or m.needs_clear):
            p1.clear() 
            p1.plot(m.x, m.y, symbolPen='w', pen=None)
            m.tx = [0.2*m.basis1data[0]*m.x[i]+0.2*m.basis2data[0]*m.y[i] for i in range(len(m.x))]
            m.ty = [0.2*m.basis1data[1]*m.x[i]+0.2*m.basis2data[1]*m.y[i] for i in range(len(m.y))]
            p2.clear()
            p2.plot(m.tx,m.ty, symbolPen='w', pen=None)
            p2.addItem(basis1, ignoreBounds=True)
            p2.addItem(basis2, ignoreBounds=True)
            m.needs_update = False
            m.needs_clear = False

    if p2.sceneBoundingRect().contains(pos):
        if(m.mode not in [1,2,3]):
            basis1.setData([0, m.basis1data[0]], [0, m.basis1data[1]])
            basis2.setData([0, m.basis2data[0]], [0, m.basis2data[1]])

        mousePoint = vb2.mapSceneToView(pos)
        index = int(mousePoint.x())
        mx = mousePoint.x()
        my = mousePoint.y()
        if(m.mode == 1):
            basis1.setData([mx],[my])
            m.basis1data=[mx,my]
        if(m.mode == 2):
            basis2.setData([0,mx],[0,my])
            m.basis2data=[mx,my]

        m.tx = [0.2*m.basis1data[0]*m.x[i]+0.2*m.basis2data[0]*m.y[i] for i in range(len(m.x))]
        m.ty = [0.2*m.basis1data[1]*m.x[i]+0.2*m.basis2data[1]*m.y[i] for i in range(len(m.y))]
        m.update_schur_profile()

        tx = m.tx
        ty = m.ty

        if(m.mode == 3):
            unit = [my / math.sqrt(mx*mx + my*my), mx / math.sqrt(mx*mx + my*my)]
            b1x = m.basis1data[0]*unit[0] + m.basis1data[1]*unit[1]
            b1y = -m.basis1data[0]*unit[1] + m.basis1data[1]*unit[0]
            b2x = m.basis2data[0]*unit[0] + m.basis2data[1]*unit[1]
            b2y = -m.basis2data[0]*unit[1] + m.basis2data[1]*unit[0]

            basis1.setData([0, b1x], [0, b1y])
            basis2.setData([0, b2x], [0, b2y])

            tx = [ m.x[i]*unit[0] + m.y[i]*unit[1] for i in range(len(m.x))]
            ty = [-m.x[i]*unit[1] + m.y[i]*unit[0] for i in range(len(m.y))]
            pushed = [m.tx, m.ty]
            m.tx = tx
            m.ty = ty
            m.update_schur_profile()
            m.tx = pushed[0]
            m.ty = pushed[1]

        sym = m.components[1]
        ext = m.components[0]
        label.setText("<br><span style='font-size: 20pt; color: green'>M(symmetric)= <br> [%0.001f,%0.001f] <br> [%0.1f,%0.1f] <br><br><span style='color: red'>M(anti-symmetric)= <br> [%0.001f, %0.001f]<br>[%0.001f,%0.001f]</span>" % (sym[0,0],sym[0,1],sym[1,0],sym[1,1],ext[0,0],ext[0,1],ext[1,0],ext[1,1]))

        # Probably this is refreshing too often
        p2.clear()
        p2.plot(tx,ty, symbolPen='w', pen=None)
        p2.addItem(basis1, ignoreBounds=True)
        p2.addItem(basis2, ignoreBounds=True)


proxy = pg.SignalProxy(p1.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)
#p1.scene().sigMouseMoved.connect(mouseMoved)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


