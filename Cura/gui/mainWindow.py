__copyright__ = "Copyright (C) 2013 David Braam - Released under terms of the AGPLv3 License"

import wx
import sys

from Cura.gui.util import dropTarget
from Cura.gui.util import glPanel
from Cura.util import profile
from Cura.util import version

from Cura.gui.view3D import printerView3D
from Cura.scene import printer3DScene

class mainWindow(wx.Frame):
	def __init__(self):
		super(mainWindow, self).__init__(None, title='Cura - ' + version.getVersion())

		wx.EVT_CLOSE(self, self.OnClose)

		# allow dropping any file, restrict later
		self.SetDropTarget(dropTarget.FileDropTarget(self.OnDropFiles))

		# TODO: wxWidgets 2.9.4 has a bug when NSView does not register for dragged types when wx drop target is set. It was fixed in 2.9.5
		if sys.platform.startswith('darwin'):
			try:
				import objc
				nswindow = objc.objc_object(c_void_p=self.MacGetTopLevelWindowRef())
				view = nswindow.contentView()
				view.registerForDraggedTypes_([u'NSFilenamesPboardType'])
			except:
				pass

		#Main 3D panel
		self._gl_panel = glPanel.GLPanel(self)

		#Setup a view and scene for testing.
		self._scene = printer3DScene.Printer3DScene()
		self._view = printerView3D.PrinterView3D()
		self._view.setScene(self._scene)
		self._gl_panel.setView(self._view)

		# Main window sizer
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(sizer)
		sizer.Add(self._gl_panel, 1, flag=wx.EXPAND)
		sizer.Layout()
		self.sizer = sizer

		# Set default window size & position
		self.SetSize((wx.Display().GetClientArea().GetWidth()/2,wx.Display().GetClientArea().GetHeight()/2))
		self.Centre()

		# Restore the window position, size & state from the preferences file
		try:
			if profile.getPreference('window_maximized') == 'True':
				# Maximize as next event, this solves a layouting problem on windows, where the first size given to the sizer is wrong.
				wx.CallAfter(self.Maximize, True)
			else:
				posx = int(profile.getPreference('window_pos_x'))
				posy = int(profile.getPreference('window_pos_y'))
				width = int(profile.getPreference('window_width'))
				height = int(profile.getPreference('window_height'))
				if posx > 0 or posy > 0:
					self.SetPosition((posx,posy))
				if width > 0 and height > 0:
					self.SetSize((width,height))
		except:
			# Maximize as next event, this solves a layouting problem on windows, where the first size given to the sizer is wrong.
			wx.CallAfter(self.Maximize, True)

		#Check if the window is somewhere on a display, else put it at the center.
		if wx.Display.GetFromPoint(self.GetPosition()) < 0:
			self.Centre()
		if wx.Display.GetFromPoint((self.GetPositionTuple()[0] + self.GetSizeTuple()[1], self.GetPositionTuple()[1] + self.GetSizeTuple()[1])) < 0:
			self.Centre()
		if wx.Display.GetFromPoint(self.GetPosition()) < 0:
			self.SetSize((800,600))
			self.Centre()

	def OnDropFiles(self, files):
		#TODO: Files droped on window, load them.
		pass

	def OnClose(self, e):
		profile.saveProfile(profile.getDefaultProfilePath(), True)

		# Save the window position, size & state from the preferences file
		profile.putPreference('window_maximized', self.IsMaximized())
		if not self.IsMaximized() and not self.IsIconized():
			(posx, posy) = self.GetPosition()
			profile.putPreference('window_pos_x', posx)
			profile.putPreference('window_pos_y', posy)
			(width, height) = self.GetSize()
			profile.putPreference('window_width', width)
			profile.putPreference('window_height', height)

			# Save normal sash position.  If in normal mode (!simple mode), get last position of sash before saving it...
			isSimple = profile.getPreference('startMode') == 'Simple'
			if not isSimple:
				self.normalSashPos = self.splitter.GetSashPosition()
			profile.putPreference('window_normal_sash', self.normalSashPos)

		print "Closing down"
		self.Destroy()
