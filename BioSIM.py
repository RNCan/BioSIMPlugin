# -*- coding: utf-8 -*-
"""
/***************************************************************************
 BioSIMplugin
                                 A QGIS plugin
 animation/ image jour 
                              -------------------
        begin                : 2017-09-13
        git sha              : $Format:%H$
        copyright            : (C) 2017 by ahmed amine
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
#from __future__ import division
from csv import reader, writer
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog, QDialog,QFont,QImage,QPainter,QMessageBox
from PyQt4.QtXml import QDomDocument
from qgis.gui import *

# Initialize Qt resources from file resources.py
import resources

# Import the code for the dialog
from BioSIM_dialog import BioSIMpluginDialog
from BioSIM_dialog_image import BioSIMpluginDialogimage
import os.path,time
from qgis.core import *
from PyQt4.QtCore import *
from datetime import date

#from csv_layer import CsvLayer
folderPath = os.path.dirname(__file__)+'/QGIS-PROJ/'
projectPath = folderPath+'Dispersal.qgs'
ameriquenord=folderPath+'ameriquenord.shp'
QCmaps=folderPath+'County.shp'
projanimation= QFileInfo(folderPath+'Dispersal.qgs')
proj=QgsProject.instance() 

class Operationlongue(QtCore.QThread):
    info = QtCore.pyqtSignal(int)
    fini = QtCore.pyqtSignal()
    debut = QtCore.pyqtSignal()
    #========================================================================
    def __init__(self, parent ,n):
        super(Operationlongue, self).__init__(parent)
        self.n=n	
    #========================================================================
    def run(self):
      self.debut.emit()
      for i in range(0,self.n):
        self.info.emit(i)		
      self.fini.emit()	


class BioSIMplugin:
    """QGIS Plugin Implementation."""
    def __init__(self,iface):
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
        self.menu = self.tr(u'&BioSIM Plugin ')        
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'BioSIMplugin')
        self.toolbar.setObjectName(u'BioSIMplugin')
        self.dlg = BioSIMpluginDialog()
        self.dlg1 = BioSIMpluginDialogimage()
        self.dlg.box_csv.clear()
        self.dlg.csv_button.clicked.connect(self.select_csv_file)
        self.dlg1.box_csv.clear()
        self.dlg1.csv_button.clicked.connect(self.select_csv_file1)
        self.dlg.clear_button.clicked.connect(self.cleartif)
        self.dlg.tif_button.clicked.connect(self.select_tif_file)
        self.dlg.box_output.clear()
        self.dlg.output_button.clicked.connect(self.select_output_file)
        self.dlg1.box_output.clear()
        self.dlg1.output_button.clicked.connect(self.select_output_file1)
        self.dlg.ok_button.clicked.connect(self.lancement)
        self.dlg1.run_button.clicked.connect(self.executeimage)
        self.operationlongue = None
        self.displaydate()        
        self.timer = QtCore.QTimer(self.iface)
        self.timer.setInterval( 60000*60*10 )
        self.timer.timeout.connect(self.displaydate)
        self.timer.start()
		
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

        icon_path = ':/plugins/BioSIMplugin/Animation.png'
        self.add_action(
            icon_path,
            text=self.tr(u'BioSIM Animation'),
            callback=self.run,
            parent=self.iface.mainWindow())
		
        icon_path = ':/plugins/BioSIMplugin/DailyDispersal.png'
        self.add_action(
            icon_path,
            text=self.tr(u'BioSIM Image Jour'),
            callback=self.runimage,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&BioSIM Plugin '),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
    
	## set automatique date in image jour ##
    def get_date_csv(self,path):
      import time
      import csv      
      year=int(time.strftime("%Y"))
      month = 13
      month1=0
      day = 32
      day1=0
      reader = csv.reader(open(path, 'rb'))
      header = reader.next()
      for col in range (0, len(header)):
	    if header[col]=="Year":
		  break
      for header in reader:
        if int(header[col]) != year:
           year=int(header[col])
        if int(header[col+1])< month:		   
           month=int(header[col+1])
        if int(header[col+1])> month1:		   
           month1=int(header[col+1])
        if (int(header[col+1])== month ) and (int(header[col+2])< day) :		   
            day=int(header[col+2])        
        if (int(header[col+1])== month1 ) and (int(header[col+2])> day1) and (int(header[col+3])> 14):		   
            day1=int(header[col+2])          
            
      return (year,month,month1,day,day1)	   

	## test csv file format ## 
    def test_file(self,path,name):
        import csv
        id=False
        reader = csv.reader(open(path, 'rb'))
        header = reader.next()  
        for col in range(0,len(header)):   
         if header[col]==name:  
          id=True
          break
        return id  
	
	## test if data existe ##
    def ifdataexiste(self,csv):
       file=open(str(csv), 'rb')
       data = list(reader(file, delimiter=","))
       return len(data)
	
	## select csv file for animation windows ##
    def select_csv_file(self): 
        settings = QSettings("Company name", "Application name")
        lastpath = settings.value("LASTPATH", ".")
        path= QFileDialog.getOpenFileName(self.dlg, "Open cvs file",lastpath,"CSV files (*.csv)")
        if path:  
          if self.test_file(path,'Minute'):
            self.dlg.ok_button.setEnabled(True)
            settings.setValue("LASTPATH", os.path.dirname(path))
            self.dlg.box_csv.setText(path)
            if  not self.dlg.box_output.toPlainText():
              self.dlg.box_output.setText(os.path.dirname(path)+'/Image')
          else:
           msgBox = QMessageBox()
           msgBox.setText(" unsupported column format!!. minute column not exist")
           msgBox.exec_()

	## get date today######	   	   
    def displaydate(self):
      import time
      self.dlg1.spin_an.setValue(int(time.strftime("%Y")))
      self.dlg1.spin_m.setValue(int(time.strftime("%m")))
      self.dlg1.spin_m1.setValue(int(time.strftime("%m")))
      self.dlg1.spin_j.setValue(int(time.strftime("%d"))-1)
      self.dlg1.spin_j1.setValue(int(time.strftime("%d")))
      self.dlg.spin_an.setValue(int(time.strftime("%Y")))
      self.dlg.spin_m.setValue(int(time.strftime("%m")))
      self.dlg.spin_j.setValue(int(time.strftime("%d")))
    
	## select csv file for image windows ##
    def select_csv_file1(self): 
        settings = QSettings("Company name", "Application name")
        lastpath = settings.value("LASTPATH", ".")
        path= QFileDialog.getOpenFileName(self.dlg1, "Open cvs file",lastpath,"CSV files (*.csv)") 
        if path:
          if not( self.test_file(path,'Minute')):
            settings.setValue("LASTPATH", os.path.dirname(path))
            self.dlg1.box_csv.setText(path)
            date=self.get_date_csv(path)
            self.dlg1.spin_an.setValue(int(date[0]))
            self.dlg1.spin_m.setValue(int(date[1]))
            self.dlg1.spin_j.setValue(int(date[3]))
            self.dlg1.spin_m1.setValue(int(date[2]))
            self.dlg1.spin_j1.setValue(int(date[4]))
            if  not self.dlg1.box_output.toPlainText():
              self.dlg1.box_output.setText(os.path.dirname(path)+'/Image')
          else:
           msgBox = QMessageBox()
           msgBox.setText(" unsupported column format!!.")
           msgBox.exec_()
 	
	## select radar image file ##
    def select_tif_file(self):
      settings = QSettings("Company name", "Application name")
      last_path = settings.value("LAST_PATH", ".")
      filetif = QFileDialog.getOpenFileNames(self.dlg,'Open file',last_path,"TIF files (*.tif)")        
      if filetif :
       settings.setValue("LAST_PATH", os.path.dirname(filetif[0]))
       for i in range(0,len(filetif)):
        self.dlg.box_tif.append(filetif[i])
        data = str (filetif[0])
        for i in range(0,len(data)-len('.tif')):
         if data[i]== '\\':
	       j=i 
        data = data[j+1:len(data)-len('.tif')]  
        if len(data)>12 and self.dlg.spin_an.isEnabled():
          self.dlg.spin_an.setValue(int(data[0:4]))
          self.dlg.spin_m.setValue(int(data[4:6]))
          self.dlg.spin_j.setValue(int(data[6:8]))
          self.dlg.spin_an.setEnabled(False)
          self.dlg.spin_m.setEnabled(False)
          self.dlg.spin_j.setEnabled(False)
        elif  not self.dlg.spin_an.isEnabled():
          if (self.dlg.spin_m.value()== int(data[4:6]) and self.dlg.spin_j.value() > int(data[6:8])) or (self.dlg.spin_m.value() > int(data[4:6])):
            self.dlg.spin_an.setValue(int(data[0:4]))
            self.dlg.spin_m.setValue(int(data[4:6]))
            self.dlg.spin_j.setValue(int(data[6:8]))  
	
	## clear filds radar image ##
    def cleartif(self):
      self.dlg.box_tif.clear()	
      self.dlg.spin_an.setEnabled(True)
      self.dlg.spin_m.setEnabled(True)
      self.dlg.spin_j.setEnabled(True)
	
    '''
    def addday(self,d,m):
      if int(m)==6 and  int(d)==30:
        d='01'
        m='07'
      elif int(d)==31 and int(m)==7:
        d='01'
        m='08'
      else:
       d=str(int(d)+1)
      m=self.addzero(m)
      d=self.addzero(d)	   
      return m+d  
    ''' 
 	
	## select output directory for animation windows ##
    def select_output_file(self): 
     outputDir = QFileDialog(None, "Select output Directory")
     outputDir.setFileMode(QFileDialog.Directory)
     outputDir.setAcceptMode(QFileDialog.AcceptOpen)
     outputDir.setOption(QFileDialog.ShowDirsOnly, True)
     outputDir.show()
     if outputDir.exec_() == QDialog.Accepted:
        outDir = outputDir.selectedFiles()[0]
        self.dlg.box_output.setText(outDir)	
	
	## select output directory for image windows ##
    def select_output_file1(self): 
     outputDir = QFileDialog(None, "Select output Directory")
     outputDir.setFileMode(QFileDialog.Directory)
     outputDir.setAcceptMode(QFileDialog.AcceptOpen)
     outputDir.setOption(QFileDialog.ShowDirsOnly, True)
     outputDir.show()
     if outputDir.exec_() == QDialog.Accepted:
        outDir = outputDir.selectedFiles()[0]
        self.dlg1.box_output.setText(outDir)
	
	## load csv file in QGIS ###
    def linkcsv(self,Csvf):      
      canvas = iface.mapCanvas()
      selectedcrs="EPSG:4326"
      target_crs = QgsCoordinateReferenceSystem()
      target_crs.createFromUserInput(selectedcrs)
      canvas.setDestinationCrs(target_crs)
      uricsv = "file:///"+Csvf+"?delimiter=%s&xField=%s&yField=%s" % (",","Longitude","Latitude") 
      layer = QgsVectorLayer(uricsv,'test', "delimitedtext") 
      layer.setCrs(QgsCoordinateReferenceSystem(crs_wkt)) 
      if not layer.isValid():
         uricsv ="file:///"+Csvf+"?delimiter=%s&xField=%s&yField=%s" % (",","lon","lat")
         layer = QgsVectorLayer(uricsv,'t', "delimitedtext")
         layer.setCrs(QgsCoordinateReferenceSystem(crs_wkt)) 
      if not layer.isValid():
         print 'is not good'	 
      return uricsv		
	
	## creat tmp file csv ##
    def open_csv(self):
        Csvin=self.dlg.box_csv.toPlainText()
        year=str(self.dlg.spin_an.value())		
        months=str(self.dlg.spin_m.value())
        day=str(self.dlg.spin_j.value())
        path=self.dlg.box_output.toPlainText()
        imagePath=path+'/'+year+'-'+self.addzero(months)+'-'+self.addzero(day)+'/'
        if int(months)==6 and  int(day)==30:
         fday='01'
         fmonths='07'
        elif int(months)==7 and int(day)==31 :
          fday='01'
          fmonths='08'
        else:
          fday=str(int(day)+1)
          fmonths=months
        self.subcsvjour(Csvin,day,months,fday,fmonths,True)       
        directory =os.path.dirname(imagePath)  
        if  not os.path.exists(directory):
          os.makedirs(directory)
	
	## create tmp file csv with date radar file ##
    def open_project(self,i):
        tmp=  self.dlg.box_tif.toPlainText() 
        tif_ = []
        tif_=tmp.split ('\n')
        data=self.getdata(tif_[i])
        months=data[4:6]
        day=data[6:8]
        hour=data[8:10]
        minute=data[10:12]
        Csvin=folderPath+'data.csv'
        self.subcsvjour(Csvin,day,months,minute,hour,False)
   
    ##  open csv file in qgis without radar image ##  
    def open_project_csv(self,i): 
       path=self.dlg.box_output.toPlainText()		
       Csvin=folderPath+'data.csv'  
       year=str(self.dlg.spin_an.value())
       months=str(self.dlg.spin_m.value())
       day=self.dlg.spin_j.value()
       Path=path+'/'+year+'-'+self.addzero(months)+'-'+self.addzero(day)
       geth=self.gethour(Csvin,day,months)
       if geth:
        minute=int(geth[2:4])+(i*10)#'00'
        hour=int(geth[0:2])+minute/60
        day+=hour/24
        hour%=24
        minute%=60
        if int(months)==6 and  int(day)==31:
         day='01'
         months='07'
        elif int(months)==7 and int(day)==32 :
         day='01'
         months='08'
        day=self.addzero(day)
        months=self.addzero(months)
        hour=self.addzero(hour)
        minute=self.addzero(minute)
        self.subcsvjour(Csvin,day,months,minute,hour,False)        
        data=year+months+day+hour+minute
        self.addcsv(data)
        self.pngout(data,Path)	
        self.dlg.progressBar.setValue(int((i+1)*1.47))
	
	## create image for animation ##
    def lancement(self):
       self.open_csv()
       months=str(self.dlg.spin_m.value())
       day=self.dlg.spin_j.value()
       if self.ifdataexiste(folderPath+'data.csv')!=1:#self.gethour(folderPath+'data.csv',day,months):
         tmp=  self.dlg.box_tif.toPlainText()
         tif_ = []
         tif_=tmp.split ('\n')
         if self.operationlongue==None or not self.operationlongue.isRunning(): 
           if len(self.dlg.box_tif.toPlainText())!=0:	 
             self.operationlongue = Operationlongue(self.iface,len(tif_))
             self.operationlongue.info.connect(self.open_project)
             self.operationlongue.info.connect(self.progression)
             self.operationlongue.fini.connect(self.stop)
             self.operationlongue.fini.connect(self.cleartif)
             self.operationlongue.start()
           else:            
             self.operationlongue = Operationlongue(self.iface,68)
             self.operationlongue.info.connect(self.open_project_csv)
             self.operationlongue.fini.connect(self.stop)
             self.operationlongue.fini.connect(self.cleartif)
             self.operationlongue.start()   
         else :
          self.operationlongue.terminate()	
       else :
        msgBox = QMessageBox()
        msgBox.setText("The selected date does not appear in the file CSV!!.")
        msgBox.exec_()
        self.cleartif()
		    
	## add tif file in qgis and get png image in output ##	
    def progression(self,i):
        path=self.dlg.box_output.toPlainText()
        year=str(self.dlg.spin_an.value())		
        months=str(self.dlg.spin_m.value())
        day=str(self.dlg.spin_j.value())
        Path=path+'/'+year+'-'+self.addzero(months)+'-'+self.addzero(day)		
        tmp=  self.dlg.box_tif.toPlainText() 
        tif_ = []
        tif_=tmp.split ('\n')
        data=self.getdata(tif_[i])
        self.dlg.progressBar.setValue(int((i+1)*(100/(len(tif_)*1.0))))
        if self.ifdataexiste(folderPath+'data1.csv')!=1:
         self.settif(tif_[i])
         self.pngout(data,Path)         
         if i%2:
           QCoreApplication.processEvents()		
	
	## get hour from csv file ##
    def gethour(self,csv,day,m):
      file=open(str(csv), 'rb')
      data = list(reader(file, delimiter=","))
      rownum = 0
      index_=-999
      test=False
      for row in data:
       if rownum==0:
        header =row
        rownum=1
        for col in range(0,len(row)):   
         if header[col]=='Day':  
          index_=col 
          break	
       else :		  
         if int(row[index_])==int(day) and int(row[index_-1])== int(m):
           if int(row[index_+11])== 3 or int(row[index_+11])==4:
              if 16<= int(row[index_+1])<=20:
		       test=self.addzero(row[index_+1])+self.addzero(row[index_+2])
		       break
      file.close()  
      return test	
	
	## stop operation ##
    def stop(self):
        path=self.dlg.box_output.toPlainText()
        year=str(self.dlg.spin_an.value())
        months=str(self.dlg.spin_m.value())
        day=self.dlg.spin_j.value()
        extra='/'+year+'-'+self.addzero(months)+'-'+self.addzero(day)
        if self.dlg.checkGIF.isChecked():
         self.dlg.progressBar.setValue(98)
         self.makeAnimatedGif(path,extra)
        self.dlg.progressBar.setValue(0)
        self.iface.newProject()
        os.remove(folderPath+'/1.qgs')
        #os.remove(folderPath+'/1.qgs~')
        os.remove(folderPath+'/data.csv')
        os.remove(folderPath+'/data1.csv')
	
	## add csv file in qgis ## 
    def addcsv(self,data):
        Year=data[0:4]
        months=data[4:6]
        day=data[6:8]
        hour=data[8:10]
        minute=data[10:12]
        self.iface.newProject()
        layern = QgsVectorLayer(ameriquenord, "maps", "ogr")
        layern.loadNamedStyle(folderPath+'Style/layer.qml')                     
        layern.triggerRepaint()  	  
        QgsMapLayerRegistry.instance().addMapLayer(layern)        
        imagePath =folderPath+'/1.qgs' 
        uricsv=folderPath+'/data1.csv'
        layercsv=self.import_csv(uricsv,hour+':'+minute)		
        style=folderPath+'Style/newcsv.qml'
        if self.dlg.symbole_Box.currentText()=='small':
          style=folderPath+'Style/csv1.qml' 		  
        layercsv.loadNamedStyle(style)  		                  
        layercsv.triggerRepaint()
        layercsv.setSubsetString('("Year"='+Year+' AND "Month"='+months+' AND "Day"='+day+' AND "Hour"='+str(hour)+' AND "Minute"='+str(minute)+')')		
        QgsMapLayerRegistry.instance().addMapLayer(layercsv)
        QgsProject.instance().write(QFileInfo(imagePath))

	## set tif file in layer gqis ##	
    def settif(self,tif):
        self.iface.newProject()
        layern = QgsVectorLayer(ameriquenord, "maps", "ogr")
        layern.loadNamedStyle(folderPath+'Style/layer.qml')                     
        layern.triggerRepaint()  	  
        QgsMapLayerRegistry.instance().addMapLayer(layern)  
        png_name=self.getdata(tif)
        Year=png_name[0:4]
        months=png_name[4:6]
        day=png_name[6:8]
        hour=png_name[8:10]
        minute=png_name[10:12]
        imagePath =folderPath+'/1.qgs'
        layer=QgsRasterLayer(tif, hour+':'+minute)
        QgsMapLayerRegistry.instance().addMapLayer(layer)       
        uricsv=folderPath+'/data1.csv'
        layercsv=self.import_csv(uricsv,hour+':'+minute)
       # layercsv = QgsVectorLayer(uricsv,hour+':'+minute, "delimitedtext") 
        style=folderPath+'Style/newcsv.qml'

        if self.dlg.symbole_Box.currentText()=='small':
          style=folderPath+'Style/csv1.qml' 		
        layercsv.loadNamedStyle(style)                    
        layercsv.triggerRepaint()
        layercsv.setSubsetString('("Year"='+Year+' AND "Month"='+months+' AND "Day"='+day+' AND "Hour"='+str(hour)+' AND "Minute"='+str(minute)+')')		
        QgsMapLayerRegistry.instance().addMapLayer(layercsv)		
        QgsProject.instance().write(QFileInfo(imagePath))	
        del layercsv
	
	## get png image from a composer template qgis ##
    def pngout(self,data,paths):
        png_name=data
        Year=png_name[0:4]
        months=png_name[4:6]
        day=png_name[6:8]
        hour=png_name[8:10]
        minute=png_name[10:12]
        imagePath =folderPath+'/1.qgs'
        canvas = self.iface.mapCanvas()
        QgsProject.instance().read(QFileInfo(imagePath))
        bridge = QgsLayerTreeMapCanvasBridge(QgsProject.instance().layerTreeRoot(), canvas)
        imagePath =paths+'/'+png_name+'.png' 
        bridge.setCanvasLayers()
        composition = QgsComposition(canvas.mapSettings())
        composerAsDocument = QDomDocument()
        composerAsDocument.setContent(QFile(folderPath+'animation.qpt'))
        composition.loadFromTemplate(composerAsDocument, {})
        title = QgsComposerLabel(composition)
        title.setText(str(Year+'/'+months+'/'+day+' '+hour+':'+minute+'(GMT -4)'))
        title.setFont(QFont("Cambria",15, QFont.Bold))
        title.setItemPosition(228,5.2)
        title.adjustSizeToText()  
        composition.addItem(title)
        Legend = QgsComposerPicture(composition)
        Legend.setPictureFile(folderPath+'/Style/Legend1.png')
        Legend.setSceneRect(QRectF(0,0,40,40)) 
        composition.addItem(Legend)		
        dpmm = 300 / 25.4
        width = int(dpmm * composition.paperWidth())
        height = int(dpmm * composition.paperHeight())
        image = QImage(QSize(width, height), QImage.Format_ARGB32)
        image.setDotsPerMeterX(dpmm * 1000)
        image.setDotsPerMeterY(dpmm * 1000)
        image.fill(0)
        imagePainter = QPainter(image)
        composition.renderPage( imagePainter, 0 )
        imagePainter.end()
        image.save(imagePath, "png")
     
	## sub divide the csv file ## 
    def subcsvjour(self,csv,dd,md,df,mf,minute): 
     data = list(reader(open(str(csv), 'rb'), delimiter=","))
     if minute:
	    csvf=open(folderPath+'/data.csv', 'wb')
     else:
        csvf=open(folderPath+'/data1.csv', 'wb')
     out = writer(csvf, delimiter=',' , lineterminator='\n')
     rownum = 0
     index_=-999
     for row in data:
      if rownum==0:
       header =row
       rownum=1
       out.writerow(header)
       for col in range(0,len(row)):   
        if header[col]=='Day':  
         index_=col 
         break 
      else:
       if minute:
          if (int(row[index_-1])== int(md) and int(row[index_])== int(dd)) or (int(row[index_-1])== int(mf) and int(row[index_])== int(df)) :
            out.writerow(row)
       else:  
         if (int(row[index_-1])== int(md) and int(row[index_])== int(dd) and int(row[index_+1])== int(mf) and int(row[index_+2])== int(df)) :
           out.writerow(row) 
     csvf.close()	
	
	## set tif files source in tab ##
    def get_tif(self):
      tmp=  self.dlg.box_tif.toPlainText()
      tif_ = []
      tif_=tmp.split ('\n')
      return tif_
	
    ## get date and hour from tif file ##	
    def getdata(self,indata):
      data = str(indata)
      for i in range(0,len(data)-len('.tif')):
       if data[i]== '\\':
	     j=i 
      data = data[j+1:len(data)-len('.tif')]  
      if len(data)>12:
       return data [0:12]  	  
    
	## add projection epsg:4326 to file csv in qgis ##
    def import_csv(self, csv_path,title):
        import csv
        # Save the path to the file soe we can update it in response to edits
        csv_file = open(csv_path, 'rb')
        reader = csv.reader(csv_file)
        header = reader.next() 
        id=-999
        for col in range(0,len(header)):   
         if header[col]=='Longitude':  
          id=0 
          break 		
        # Get sample
        sample = reader.next()
        field_sample = dict(zip(header, sample))
        field_name_types = {}
        # create dict of fieldname:type
        for key in field_sample.keys():
            if field_sample[key].isdigit():
                field_type = 'integer'
            else:
                try:
                    float(field_sample[key])
                    field_type = 'real'
                except ValueError:
                    field_type = 'string'
            field_name_types[key] = field_type
        # Build up the URI needed to create memory layer
        uri =  "Point?crs=epsg:4326"
        for fld in header:
            uri += '&field={}:{}'.format(fld, field_name_types[fld])
        lyr = QgsVectorLayer(uri,title, 'memory')	
        csv_file.seek(0)
        # Skip the header
        reader.next()
        lyr.startEditing()
        for row in reader:
            flds = dict(zip(header, row))
            feature = QgsFeature()
            if id==0:
              geometry = QgsGeometry.fromPoint(QgsPoint(float(flds['Longitude']), float(flds['Latitude'])))
            else:
			 geometry = QgsGeometry.fromPoint(QgsPoint(float(flds['lon']), float(flds['lat'])))
            feature.setGeometry(geometry)
            feature.setAttributes(row)
            lyr.addFeature(feature, True)
        lyr.commitChanges()
        csv_file.close()
        return lyr
	
	## perpare image from csv file in image jour ##
    def csv_image(self):
     # Csvin =self.dlg1.box_csv.toPlainText()
      paths=self.dlg1.box_output.toPlainText()
      QgsProject.instance().clear()	  
      directory =os.path.dirname(paths+'/')  
      if  not os.path.exists(directory):
        os.makedirs(directory)
      layers=[]
      for x in range(0,2):
       layers.append('')
      layers[0] = QgsVectorLayer(ameriquenord, "maps", "ogr")
      layers[0].loadNamedStyle(folderPath+'Style/layer.qml')                     
      layers[0].triggerRepaint()
      QgsMapLayerRegistry.instance().addMapLayer(layers[0])
      layers[1] = QgsVectorLayer(QCmaps, "quebec", "ogr")
      layers[1].loadNamedStyle(folderPath+'Style/layer.qml')                     
      layers[1].triggerRepaint() 
      QgsMapLayerRegistry.instance().addMapLayer(layers[1])	
    
   	## add layers to qgis for image jour ##
    def qgis_image(self,paths,Csvin,year,Dmonth,Fmonth,Dday,Fday,H,index):   
      fd=0
      if int(Dmonth)!= int(Fmonth):
        if Dmonth=='6':
		   fd='30'
        else: 
		   fd='31'		
      if str(int(Dday)+index)>fd and int(Dmonth)!= int(Fmonth):
          dm=fm=Fmonth
          dj=int(Dday)+index-int(fd)
          fj=dj+1
      elif str(int(Dday)+index)==fd and int(Dmonth)!= int(Fmonth):
         dm=Dmonth
         fm=Fmonth
         dj=int(Dday)+index
         fj=1
      else :		 
         dm=Dmonth
         fm=Dmonth
         dj=int(Dday)+index
         fj=dj+1
      if len(dm)==1:
		months='0'+dm
      else:
	    months=dm
      if len(str(dj))==1:
	    j='0'+str(dj)
      else:
		j=str(dj)
      imagePath = paths+'/'+year+months+j+'.png' 
     # self.subcsvjour(Csvin,str(dj),dm,str(fj),fm,True)
      layers=self.import_csv(Csvin,dm+'/'+str(dj))#folderPath+'/data.csv')	  
      layers.loadNamedStyle(folderPath+'Style/csv.qml')                    
      layers.triggerRepaint()
      QgsMapLayerRegistry.instance().addMapLayer(layers)       
      layers.setSubsetString('("Year"='+year+' AND "Month"='+dm+' AND "Day"='+str(dj)+' AND "Hour">'+H+')  OR  ("Year"='+year+' AND "Month"='+fm+' AND "Day"='+str(fj)+' AND "Hour"<'+H+')' ) 
      QgsProject.instance().write(projanimation)
#####################image ######################### 
      canvas = self.iface.mapCanvas()
      QgsProject.instance().read(projanimation)
      bridge = QgsLayerTreeMapCanvasBridge(QgsProject.instance().layerTreeRoot(), canvas)
      bridge.setCanvasLayers()
      composition = QgsComposition(canvas.mapSettings())
      composerAsDocument = QDomDocument()
      composerAsDocument.setContent(QFile(folderPath+'image-jour.qpt'))
      composition.loadFromTemplate(composerAsDocument, {})
      title = QgsComposerLabel(composition)
      title.setText(str(year+'/'+months+'/'+j))
      title.setFont(QFont("Cambria",15, QFont.Bold))
      title.setItemPosition(248,5.2)
      title.adjustSizeToText()  
      composition.addItem(title)
      Legend = QgsComposerPicture(composition)
      Legend.setPictureFile(folderPath+'/Style/Legend.png')
      Legend.setSceneRect(QRectF(0,0,50,50)) 
      composition.addItem(Legend)	   
      dpmm = 300 / 25.4
      width = int(dpmm * composition.paperWidth())
      height = int(dpmm * composition.paperHeight())
      image = QImage(QSize(width, height), QImage.Format_ARGB32)
      image.setDotsPerMeterX(dpmm * 1000)
      image.setDotsPerMeterY(dpmm * 1000)
      image.fill(0)
      imagePainter = QPainter(image)
      composition.renderPage( imagePainter, 0 )
      imagePainter.end()
      image.save(imagePath, "png")   
      QgsMapLayerRegistry.instance().removeMapLayer(layers.id())		  
      del layers
	
	## clear qgis and delet a poject ##
    def fin_pross(self):
      self.dlg1.progressBar.setValue(100)
      time.sleep(0.05)
      QgsProject.instance().clear()
      self.dlg1.progressBar.setValue(0)
      os.remove(folderPath+'/Dispersal.qgs')
    
	## execute create image ##
    def runimg (self,i):
      csv =self.dlg1.box_csv.toPlainText() 
      path=self.dlg1.box_output.toPlainText()
      year=str(self.dlg1.spin_an.value())
      Dmonth= str(self.dlg1.spin_m.value())
      Fmonth= str(self.dlg1.spin_m1.value())
      Dday= str(self.dlg1.spin_j.value())
      Fday= str(self.dlg1.spin_j1.value())
      H= "16"#str(self.dlg1.spin_h.value())
      self.qgis_image(path,csv,year,Dmonth,Fmonth,Dday,Fday,H,i) 
      delta=date(int(year),int(Fmonth),int(Fday))-date(int(year),int(Dmonth),int(Dday)) 
      idx=int(100/(((delta.days)+1)*1.0))
      self.dlg1.progressBar.setValue((i+1)*idx)
      if i%2:
        QCoreApplication.processEvents()
  
    ##  execute create image ##
    def executeimage(self):
         year=str(self.dlg1.spin_an.value())
         Dmonth= str(self.dlg1.spin_m.value())
         Fmonth= str(self.dlg1.spin_m1.value())
         Dday= str(self.dlg1.spin_j.value())
         Fday= str(self.dlg1.spin_j1.value())
         delta=date(int(year),int(Fmonth),int(Fday))-date(int(year),int(Dmonth),int(Dday)) 
         if self.operationlongue==None or not self.operationlongue.isRunning(): 	 
             self.operationlongue = Operationlongue(self.iface,(delta.days)+1)
             self.operationlongue.debut.connect(self.csv_image)
             self.operationlongue.info.connect(self.runimg)            
             self.operationlongue.fini.connect(self.fin_pross)
             self.operationlongue.start()
         else :
          self.operationlongue.terminate()
	  		  
    def addzero(self,a):
	  a=str(a)
	  if len(a)==1:
	     a='0'+a
	  return a
	
    ##	run animation windows ##
    def run(self):
        """Run method that performs all the real work"""	
        self.dlg.show()
        result = self.dlg.exec_()      
        if result:
            pass
	
	## run image windows ##
    def runimage(self):
        """Run method that performs all the real work"""	
        self.dlg1.show()
        result = self.dlg1.exec_()
        if result:          
           pass
	
	## make GIf animation from png	##	
    def makeAnimatedGif(self,path,extra):
      from images2gif1 import writeGif
      from PIL import Image, ImageSequence
      os.chdir(path+extra)
      imgFiles = sorted((fn for fn in os.listdir('.') if fn.endswith('.png')))
      images = [Image.open(fn).convert('RGB') for fn in imgFiles]
      name=imgFiles[0][0:8]
      filename = path+'/'+name[0:4]+'-'+name[4:6]+'-'+name[6:8]+".gif"
      writeGif(filename, images, duration=0.2)	
      os.chdir("c:/")


###fin###