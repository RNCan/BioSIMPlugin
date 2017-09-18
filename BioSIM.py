# -*- coding: utf-8 -*-
"""
/***************************************************************************
 BioSIMplugin
                                 A QGIS plugin
 csv to image 
                              -------------------
        begin                : 2017-09-13
        git sha              : $Format:%H$
        copyright            : (C) 2017 by ahmed
        email                : aa.moutaoufik@gmail.com
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


from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog, QDialog,QFont
from qgis.gui import QgsMessageBar,QgsMapCanvas, QgsLayerTreeMapCanvasBridge
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from BioSIM_dialog import BioSIMpluginDialog
from BioSIM_dialog_image import BioSIMpluginDialogimage
import os.path
from qgis.core import *
from PyQt4.QtCore import *

folderPath = os.path.dirname(__file__)+'/QGIS-PROJ/'
projectPath = folderPath+'Dispersal.qgs'
#templatePath = folderPath+'animation.qpt'  
ameriquenord=folderPath+'ameriquenord.shp'
QCmaps=folderPath+'County.shp'
myproj= QFileInfo(projectPath)
proj=QgsProject.instance() 

class BioSIMplugin:
    """QGIS Plugin Implementation."""
    def __init__(self, iface):

	   # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'BioSIMplugin_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&csvtoimage ')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'BioSIMplugin')
        self.toolbar.setObjectName(u'BioSIMplugin')
        self.dlg = BioSIMpluginDialog()
        self.dlg1 = BioSIMpluginDialogimage()
        self.dlg.box_csv.clear()
        self.dlg.csv_button.clicked.connect(self.select_csv_file)
        self.dlg.box_tif.clear()
        self.dlg.tif_button.clicked.connect(self.select_tif_file)
        self.dlg.box_output.clear()
        self.dlg.output_button.clicked.connect(self.select_output_file)
        self.dlg.ok_button.clicked.connect(self.execute)
        
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
        return QCoreApplication.translate('BioSIMplugin', message)


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

        # Create the dialog (after translation) and keep reference
        

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/BioSIMplugin/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'BioSIM animation'),
            callback=self.run,
            parent=self.iface.mainWindow())
			
        icon_path = ':/plugins/BioSIMplugin/image-icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'BioSIM Image jour'),
            callback=self.runimage,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&csvtoimage '),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def select_csv_file(self):
       filename = QFileDialog.getOpenFileName(self.dlg, "Select csv file ",None, 'file csv *.csv')
       self.dlg.box_csv.setText(filename)
       if  not self.dlg.box_output.toPlainText():
           self.dlg.box_output.setText(os.path.dirname(filename)+'/Image')
		   
    def select_tif_file(self):
      filetif = QFileDialog.getOpenFileNames(self.dlg, 'Open file',None,"TIF files (*.tif)") 
      if filetif :
       self.dlg.box_tif.setText(filetif[0])
       for i in range(1,len(filetif)):
        self.dlg.box_tif.append(filetif[i])
       data = str (filetif[0])
       for i in range(0,len(data)-len('.tif')):
        if data[i]== '\\':
	       j=i 
       data = data[j+1:len(data)-len('.tif')]  
       if len(data)>8:
         self.dlg.spin_an.setValue(int(data[0:4]))
         self.dlg.spin_m.setValue(int(data[4:6]))
         self.dlg.spin_j.setValue(int(data[6:8]))
		 
    def select_output_file(self): 
     outputDir = QFileDialog(None, "Select output Directory")
     outputDir.setFileMode(QFileDialog.Directory)
     outputDir.setAcceptMode(QFileDialog.AcceptOpen)
     outputDir.setOption(QFileDialog.ShowDirsOnly, True)
     outputDir.show()
     if outputDir.exec_() == QDialog.Accepted:
        outDir = outputDir.selectedFiles()[0]
        self.dlg.box_output.setText(outDir)

    def gethour(self,indata):
      data = str(indata)
      for i in range(0,len(data)-len('.tif')):
       if data[i]== '\\':
	     j=i 
      data = data[j+1:len(data)-len('.tif')]  
      if len(data)>12:
       return data [8:12]	 
	   
    def getCompItemFromTitle(self,composition, type, title):
        for i in composition.items():
          if i.type() == type and i.scene() and i.displayName() == title:
            compItem = i
        return compItem  
		
    def getCompItemNames(self,composition, type):
       for i in composition.items():
         if i.type() == type and i.scene():
           compItemNames=i.displayName()
           break
       return compItemNames       
	  
    def qgis_(self,Csvin, Radarin,year,month,day,paths):
      QgsProject.instance().read(myproj)
      QgsProject.instance().clear()
      #print "preparation des images"	  
      directory =os.path.dirname(paths)  
      if  not os.path.exists(directory):
        os.makedirs(directory)
##########################
      layers=[]
      for x in range(0,4):
       layers.append('')
#################  add csv file  ############################  
      layers[2] = QgsVectorLayer(ameriquenord, "maps", "ogr")
      layers[2].loadNamedStyle(folderPath+'Style/layer.qml')                     
      layers[2].triggerRepaint() 
      layers[3] = QgsVectorLayer(QCmaps, "quebec", "ogr")
      layers[3].loadNamedStyle(folderPath+'Style/layer.qml')                     
      layers[3].triggerRepaint() 
      uricsv = "file:///"+Csvin+"?delimiter=%s&xField=%s&yField=%s" % (",","Longitude","Latitude") 
      layers[0] = QgsVectorLayer(uricsv,'hour', "delimitedtext") 
      if not layers[0].isValid():
         uricsv ="file:///"+Csvin+"?delimiter=%s&xField=%s&yField=%s" % (",","lon","lat")
         layers[0] = QgsVectorLayer(uricsv,'hour', "delimitedtext")
      if not layers[0].isValid():
         print 'is not good'
      QgsMapLayerRegistry.instance().addMapLayer(layers[2])
      QgsMapLayerRegistry.instance().addMapLayer(layers[3])
      progress=100/(len(Radarin)* 1.0)
      i=0
############## boucle principale  ########################
      for index_ in range(0,len(Radarin)):           
        png_name=self.gethour(Radarin[index_])
        hour=png_name[0:2]
        minute=png_name[2:4]
        if len(month)==1:
		   months='0'+month
        else:
		   months=month
        imagePath = paths+'/'+year+months+day+png_name+'.png'
  
##########################################################	
        layers[0] = QgsVectorLayer(uricsv,hour+':'+minute, "delimitedtext")                                             
        layers[0].loadNamedStyle(folderPath+'Style/newcsv.qml')                    
        layers[0].triggerRepaint()                                                                                       	   
##################  add tif file  #######################     
        layers[1]=QgsRasterLayer(Radarin[index_], hour+':'+minute)
        layers[0].setSubsetString('("Year"='+year+' AND "Month"='+month+' AND "Day"='+day+' AND "Hour"='+hour+' AND "Minute"='+minute+')')	
        QgsMapLayerRegistry.instance().addMapLayer(layers[1])
        QgsMapLayerRegistry.instance().addMapLayer(layers[0])
#####################################################
        i = i+progress
        self.dlg.progressBar.setValue(int(i))
        print layers[0].isValid()
       #QgsProject.instance().write(myproj)
#####################image ######################### 
        maps = self.getCompItemNames(self.iface.activeComposers()[0],QgsComposerItem.ComposerMap)
        for c in self.iface.activeComposers():
          if c.composerWindow().windowTitle() == 'ahmed':
           comp = c.composition()
        canvas = self.iface.mapCanvas()
        canvas.setRenderFlag(False)
        map_item = self.getCompItemFromTitle(comp,QgsComposerItem.ComposerMap,maps)
        comp.refreshItems()
        title = QgsComposerLabel(comp)
        title.setText(str(year+'/'+months+'/'+day+' '+hour+':'+minute+'(GMT -4)'))
        title.setFont(QFont("Cambria",15, QFont.Bold))
        title.setItemPosition(228,5.2)
        title.adjustSizeToText()  
        comp.addItem(title)  
        image = comp.printPageAsRaster(0)
        image.save(imagePath, "png")
        print 'test'
        comp.removeItem(title)
        QgsMapLayerRegistry.instance().removeMapLayer(layers[1].id())
        QgsMapLayerRegistry.instance().removeMapLayer(layers[0].id())
      print "fin"
      self.dlg.progressBar.setValue(100)
      #QgsProject.instance().clear()
      self.dlg.progressBar.setValue(0)
      self.dlg.box_csv.clear()
      self.dlg.box_tif.clear()
      QgsProject.instance().write(myproj)
     # QgsApplication.exitQgis() 	  		
    def execute (self):
      csv =self.dlg.box_csv.toPlainText() 
      tmp = self.dlg.box_tif.toPlainText()
      path=self.dlg.box_output.toPlainText()
      year=str(self.dlg.spin_an.value())
      month= str(self.dlg.spin_m.value())
      day=str(self.dlg.spin_j.value())
      tif_ = []
      tif_=tmp.split ('\n') 
      self.qgis_(csv,tif_,year,month,day,path)
	  		
    def run(self):
        """Run method that performs all the real work"""
	
		# show the dialog
        self.dlg.show()

        # Run the dialog event loop
        result = self.dlg.exec_()

        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
			
    def runimage(self):
        """Run method that performs all the real work"""
	
		# show the dialog
        self.dlg1.show()

        # Run the dialog event loop
        result = self.dlg1.exec_()

        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
