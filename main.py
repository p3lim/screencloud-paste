import os
import ScreenCloud

from time import time
from requests import requests

from PythonQt.QtCore import QSettings, QFile, QStandardPaths
from PythonQt.QtGui import QFileDialog
from PythonQt.QtUiTools import QUiLoader

class PasteUploader():
	def __init__(self):
		self.uil = QUiLoader()
		self.loadSettings()

	def upload(self, screenshot, name):
		path = self.save(screenshot, name)

		if not path:
			ScreenCloud.setError('Failed to save screenshot')
			return False

		with open(path, 'rb') as file:
			files = {'c': ('c', file, 'image/' + ScreenCloud.getScreenshotFormat())}

			try:
				res = requests.post(self.remote_url, files=files)
				res.raise_for_status()

				if self.copy_link:
					ScreenCloud.setUrl(res.text)
			except requests.exceptions.HTTPError as e:
				ScreenCloud.setError('\n' + str(e))
				return False

		return True

	def save(self, screenshot, name, path=None):
		path = QStandardPaths.writableLocation(QStandardPaths.TempLocation)
		path = os.path.join(path, name)

		try:
			screenshot.save(QFile(path), ScreenCloud.getScreenshotFormat())
		except Exception as e:
			raise

		return path

	def getFilename(self):
		return ScreenCloud.formatFilename(str(time()))

	def showSettingsUI(self, parentWidget):
		self.parentWidget = parentWidget

		self.settingsDialog = self.uil.load(QFile(workingDir + '/settings.ui'), parentWidget)
		self.settingsDialog.connect('accepted()', self.saveSettings)

		self.loadSettings()

		self.settingsDialog.group_url.input_url.text = self.remote_url
		self.settingsDialog.group_url.check_copylink.checked = self.copy_link

		self.settingsDialog.open()

	def loadSettings(self):
		settings = QSettings()
		settings.beginGroup('uploaders')
		settings.beginGroup('paste')

		self.remote_url = settings.value('url', '')
		self.copy_link = settings.value('copy-link', 'True') == 'True'

		settings.endGroup()
		settings.endGroup()

	def saveSettings(self):
		settings = QSettings()
		settings.beginGroup('uploaders')
		settings.beginGroup('paste')

		settings.setValue('url', self.settingsDialog.group_url.input_url.text)
		settings.setValue('copy-link', str(self.settingsDialog.group_url.check_copylink.checked))

		settings.endGroup()
		settings.endGroup()

	def isConfigured(self):
		self.loadSettings()
		return len(self.remote_url) > 0
