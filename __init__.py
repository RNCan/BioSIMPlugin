# -*- coding: utf-8 -*-
"""
/***************************************************************************
 BioSIMplugin
                                 A QGIS plugin
 csv to image 
                             -------------------
        begin                : 2017-09-13
        copyright            : (C) 2017 by ahmed
        email                : aa.moutaoufik@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load BioSIMplugin class from file BioSIMplugin.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .BioSIM import BioSIMplugin
    return BioSIMplugin(iface)
