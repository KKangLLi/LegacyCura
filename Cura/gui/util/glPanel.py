__copyright__ = "Copyright (C) 2013 David Braam - Released under terms of the AGPLv3 License"

import wx
import sys
import time
import traceback
import os

from Cura.gui.view3D import view3D

from wx import glcanvas
import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *

class GLPanel(glcanvas.GLCanvas):
	"""
	OpenGL panel is the basic OpenGL glue for rendering OpenGL on a window.
	It uses the view
	"""
	def __init__(self, parent):
		attribList = (glcanvas.WX_GL_RGBA, glcanvas.WX_GL_DOUBLEBUFFER, glcanvas.WX_GL_DEPTH_SIZE, 24, glcanvas.WX_GL_STENCIL_SIZE, 8, 0)
		glcanvas.GLCanvas.__init__(self, parent, style=wx.WANTS_CHARS, attribList = attribList)

		self._context = glcanvas.GLContext(self)
		self._idle_called = False
		self._refresh_queued = False
		self._display_error = True #Display the first error we get during drawing, after that suppress them.
		self._view = None

		wx.EVT_IDLE(self, self._onIdle)
		wx.EVT_PAINT(self, self._onPaint)

	def setView(self, view):
		assert(issubclass(type(view), view3D.View3D))
		self._view = view
		self._view.setPanel(self)

	def queueRefresh(self):
		"""
		For a forced refresh of the panel the queueRefresh function should be called instead of the wxWidgets Refresh().
			As Refresh() puts a refresh event on the queue even if there is one already, which puts a lot of refreshes in the queue when unneeded.
			The queueRefresh function only refreshes if there is no refresh scheduled yet.
		"""
		wx.CallAfter(self._queueRefresh)

	def _onPaint(self, e):
		self._idleCalled = False
		# Retrieve the PaintDC else the paint event will keep firing.
		dc = wx.PaintDC(self)
		try:
			renderStartTime = time.time()

			self.SetCurrent(self._context)
			self._render()
			glFlush()
			self.SwapBuffers()

			renderTime = time.time() - renderStartTime
			if renderTime == 0:
				renderTime = 0.001
		except:
			if self._display_error:
				# When an exception happens, catch it and show a message box. If the exception is not caught the draw function bugs out.
				# Only show this exception once so we do not overload the user with popups.
				errStr = _("An error has occurred during the 3D view drawing.")
				tb = traceback.extract_tb(sys.exc_info()[2])
				errStr += "\n%s: '%s'" % (str(sys.exc_info()[0].__name__), str(sys.exc_info()[1]))
				for n in xrange(len(tb)-1, -1, -1):
					locationInfo = tb[n]
					errStr += "\n @ %s:%s:%d" % (os.path.basename(locationInfo[0]), locationInfo[2], locationInfo[1])
				traceback.print_exc()
				wx.CallAfter(wx.MessageBox, errStr, _("3D window error"), wx.OK | wx.ICON_EXCLAMATION)
				self._display_error = False

	def _render(self):
		size = self.GetSizeTuple()
		if self._view is not None:
			self._view.render()

	def _onIdle(self, e):
		self._idle_called = True
		if self._refresh_queued:
			self._refresh_queued = False
			self.Refresh()

	def _queueRefresh(self):
		if self._idle_called:
			wx.CallAfter(self.Refresh)
		else:
			self._refresh_queued = True
