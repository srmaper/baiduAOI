# -*- coding: utf-8 -*-
"""
/***************************************************************************
 bdaoi
                                 A QGIS plugin
 bdaoi
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-03-17
        git sha              : $Format:%H$
        copyright            : (C) 2023 by srmaper
        email                : 1139949042
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .bdaoi_dialog import bdaoiDialog
import os.path

from qgis.utils import iface
import qgis
from qgis.core import *
import requests
import hashlib
import urllib
import json
import math

pi = 3.1415926535897932384626

def yr(lnglat, b):
    if b != '':
        c = b[0] + b[1] * abs(lnglat[0])
        d = abs(lnglat[1] / b[9])
        d = b[2] + b[3] * d + b[4] * d * d + b[5] * d * d * d + b[6] * d * d * d * d + b[7] * d * d * d * d * d + b[
            8] * d * d * d * d * d * d
        if 0 > lnglat[0]:
            bd = -1 * c
        else:
            bd = c
        lnglat[0] = bd
        if 0 > lnglat[0]:
            bd2 = -1 * d
        else:
            bd2 = d
        lnglat[1] = bd2
        return lnglat
    return

def Mecator2BD09(lng, lat):
    lnglat = [0, 0]
    Au = [[1.410526172116255E-8, 8.98305509648872E-6, -1.9939833816331, 200.9824383106796, -187.2403703815547,
           91.6087516669843, -23.38765649603339, 2.57121317296198, -0.03801003308653, 1.73379812E7],
          [- 7.435856389565537E-9, 8.983055097726239E-6, -0.78625201886289, 96.32687599759846, -1.85204757529826,
           -59.36935905485877, 47.40033549296737, -16.50741931063887, 2.28786674699375, 1.026014486E7],
          [- 3.030883460898826E-8, 8.98305509983578E-6, 0.30071316287616, 59.74293618442277, 7.357984074871,
           -25.38371002664745, 13.45380521110908, -3.29883767235584, 0.32710905363475, 6856817.37],
          [- 1.981981304930552E-8, 8.983055099779535E-6, 0.03278182852591, 40.31678527705744, 0.65659298677277,
           -4.44255534477492, 0.85341911805263, 0.12923347998204, -0.04625736007561, 4482777.06],
          [3.09191371068437E-9, 8.983055096812155E-6, 6.995724062E-5, 23.10934304144901, -2.3663490511E-4,
           -0.6321817810242, -0.00663494467273, 0.03430082397953, -0.00466043876332, 2555164.4],
          [2.890871144776878E-9, 8.983055095805407E-6, -3.068298E-8, 7.47137025468032, -3.53937994E-6,
           -0.02145144861037,
           -1.234426596E-5, 1.0322952773E-4, -3.23890364E-6, 826088.5]]
    Sp = [1.289059486E7, 8362377.87, 5591021, 3481989.83, 1678043.12, 0]
    lnglat[0] = math.fabs(lng)
    lnglat[1] = abs(lat)
    for d in range(0, 6):
        if lnglat[1] >= Sp[d]:
            c = Au[d]
            break
    lnglat = yr(lnglat, c)
    return lnglat

def BD092WGS84(lnglat):

    x_pi = 3.14159265358979324 * 3000.0 / 180.0
    pi = 3.1415926535897932384626  # π
    a = 6378245.0  # 长半轴
    ee = 0.00669342162296594323  # 扁率
    x = lnglat[0] - 0.0065
    y = lnglat[1] - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    lnglat[0] = z * math.cos(theta)
    lnglat[1] = z * math.sin(theta)

    dlat = tranlat1(lnglat[0] - 105.0, lnglat[1] - 35.0)
    dlng = tranlng1(lnglat[0] - 105.0, lnglat[1] - 35.0)
    radlat = lnglat[1] / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lnglat[1] + dlat
    mglng = lnglat[0] + dlng
    return [lnglat[0] * 2 - mglng, lnglat[1] * 2 - mglat]

def tranlat1(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret

def tranlng1(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret

mb = {
    "type": "FeatureCollection",
    "name": "aoi",
    "crs": {
        "type": "name",
        "properties": {
            "name": "urn:ogc:def:crs:EPSG::4326"
        }
    },
    "features": [{
        "type": "Feature",
        "properties": {
            "ID": 0
        },
        "geometry": {
            "type": "",
            "coordinates": [[]]
        }
    }
    ]
}



class bdaoi:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'bdaoi_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&bdaoi')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('bdaoi', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/bdaoi/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'aoi'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&bdaoi'),
                action)
            self.iface.removeToolBarIcon(action)

    def getbdwzi(self, dz, ct, aky, sky):
        datab = mb

        baiduurl = "https://api.map.baidu.com"
        queryStr = "/place/v2/suggestion?query=" + dz + "&region=" + ct + "&city_limit=true&coord_type=1&output=json&ak=" + aky
        encodedStr = urllib.parse.quote(queryStr, safe="/:=&?#+!$,;'@()*[]")
        rawStr = encodedStr + sky
        sign = hashlib.md5(urllib.parse.quote_plus(rawStr).encode("utf8")).hexdigest()
        qqurl = baiduurl + queryStr + '&sn=' + sign

        data = requests.request('GET', qqurl).content.decode('utf-8')
        dataa = json.loads(data)

        if dataa['status'] == 0:
            print('有poi')

            AOI_id = dataa['result'][0]['uid']
            uel_AOI = 'https://map.baidu.com/?newmap=1&qt=ext&uid=' + AOI_id + '&ext_ver=new&ie=utf-8&l=11'
            r_AOI = requests.request('GET', uel_AOI).content.decode('utf-8')
            # print(r_AOI)

            data_AOI = json.loads(r_AOI)
            point_transform = []
            xy = dataa['result'][0]['location']
            nxy = BD092WGS84([float(xy['lng']), float(xy['lat'])])
            dataa['result'][0]['location'] = nxy

            if 'geo' in data_AOI['content']:
                print('有aoi')
                data_AOI['content']['geo']
                geo_AOI = data_AOI['content']['geo']
                geo_AOI = geo_AOI.split('|')

                point = geo_AOI[2].split(",")

                for i in range(int(len(point) / 2)):  # 全部点的坐标，分别是x,y,的形式
                    if i == 0:  # 第一个点的x坐标删除‘1-’

                        point[2 * i] = point[2 * i][2:]
                    if i == int((len(point) / 2) - 1):  # 最后的点的y坐标删除‘;’
                        point[2 * i + 1] = point[2 * i + 1][:-1]

                    point_Mecator2BD09 = Mecator2BD09(float(point[2 * i]), float(point[2 * i + 1]))
                    point_BD092WGS84 = BD092WGS84(point_Mecator2BD09)
                    point_transform.append(point_BD092WGS84)

                datab['features'][0]['geometry']['type'] = "Polygon"
                datab['features'][0]['geometry']['coordinates'][0] = point_transform

            else:
                print('无aoi')
                datab['features'][0]['geometry']['type'] = "Point"
                datab['features'][0]['geometry']['coordinates'] = nxy


            datab['features'][0]['properties'] = dataa['result'][0]
            datab['name'] = datab['features'][0]['properties']['name']
            dataz = json.dumps(datab, ensure_ascii=False)


        else:
            print('未找到')

        return dataz


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = bdaoiDialog()

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            aky = self.dlg.bdak.text()
            sky = self.dlg.bdsk.text()
            dz = self.dlg.mbmc.text()
            ct = self.dlg.szcs.text()
            result = self.getbdwzi(dz, ct, aky, sky)

            pgstyl = QgsFillSymbol.createSimple(
                {'color': '241,248,44,128', 'outline_color': '255,0,35,255', 'outline_width': '1'})
            ptstyl = QgsMarkerSymbol.createSimple(
                {'size': 2.5, 'color': '241,248,44,128', 'outline_color': '255,0,35,255', 'outline_width': '0.5'})
                
            dtdt = json.loads(result)
            dtnm = dtdt['name']
            dz0 = iface.addVectorLayer(result, dtnm, "ogr")
            qgis.utils.iface.setActiveLayer(dz0)
            qgis.utils.iface.zoomToActiveLayer()
            dttp = dtdt['features'][0]['geometry']['type']
            if dttp == 'Polygon':
                dz0.renderer().setSymbol(pgstyl)
            else:
                dz0.renderer().setSymbol(ptstyl)

            pass
