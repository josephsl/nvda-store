# *-* coding: utf8 *-*

import os
import wx
import core
import config
import languageHandler
import ui, gui
from logHandler import log
import addonHandler
import globalVars
CECITEK_MODULE_NAME = 'cecitek'

class StoreDialog(wx.Dialog):
  _instance = None

  def __init__(self,parent, cecitek, storeAddons):
    StoreDialog._instance = self
    # Translators: The title of the Addons Dialog
    super(StoreDialog,self).__init__(parent,title=_("NVDAStore (Cecitek.fr)"))
    StoreDialog._instance.storeAddons = storeAddons
    StoreDialog._instance.cecitek = cecitek
    mainSizer=wx.BoxSizer(wx.VERTICAL)
    settingsSizer=wx.BoxSizer(wx.VERTICAL)
    entriesSizer=wx.BoxSizer(wx.VERTICAL)
    if globalVars.appArgs.disableAddons:
      # Translators: A message in the add-ons manager shown when all add-ons are disabled.
      addonsDisabledLabel=wx.StaticText(self,-1,label=_("All add-ons are currently disabled. To enable add-ons you must restart NVDA."))
      mainSizer.Add(addonsDisabledLabel)
      # Translators: the label for the installed addons list in the addons manager.
    entriesLabel=wx.StaticText(self,-1,label=_("Modules"))
    entriesSizer.Add(entriesLabel)
    self.addonsList=wx.ListCtrl(self,-1,style=wx.LC_REPORT|wx.LC_SINGLE_SEL,size=(550,350))
    # Translators: The label for a column in add-ons list used to identify add-on package name (example: package is OCR).
    self.addonsList.InsertColumn(0,_("Package"),width=150)
    # Translators: The label for a column in add-ons list used to identify add-on's running status (example: status is running).
    self.addonsList.InsertColumn(1,_("Status"),width=50)
    # Translators: The label for a column in add-ons list used to identify add-on's version (example: version is 0.3).
    self.addonsList.InsertColumn(2,_("Version"),width=50)
    # Translators: The label for a column in add-ons list used to identify add-on's author (example: author is NV Access).
    self.addonsList.InsertColumn(3,_("Author"),width=300)
    self.addonsList.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.onListItemSelected)
    entriesSizer.Add(self.addonsList,proportion=8)
    settingsSizer.Add(entriesSizer)
    entryButtonsSizer=wx.BoxSizer(wx.HORIZONTAL)
    # Translators: The label for a button in Add-ons Manager dialog to show information about the selected add-on.
    self.aboutButton=wx.Button(self,label=_("&About add-on..."))
    self.aboutButton.Disable()
    self.aboutButton.Bind(wx.EVT_BUTTON,self.onAbout)
    entryButtonsSizer.Add(self.aboutButton)
    # Translators: The label for a button in Add-ons Manager dialog to show the help for the selected add-on.
    self.helpButton=wx.Button(self,label=_("Add-on &help"))
    self.helpButton.Disable()
    self.helpButton.Bind(wx.EVT_BUTTON,self.onHelp)
    entryButtonsSizer.Add(self.helpButton)
    # Translators: The label for a button in Add-ons Manager dialog to enable or disable the selected add-on.
    self.enableDisableButton=wx.Button(self,label=_("&Disable add-on"))
    self.enableDisableButton.Disable()
    self.enableDisableButton.Bind(wx.EVT_BUTTON,self.onEnableDisable)
    entryButtonsSizer.Add(self.enableDisableButton)
    # Translators: The label for a button in Add-ons Manager dialog to install an add-on.
    self.addButton=wx.Button(self,label=_("&Installer"))
    self.addButton.Bind(wx.EVT_BUTTON,self.onAddClick)
    entryButtonsSizer.Add(self.addButton)
    # Translators: The label for a button to remove either:
    # Remove the selected add-on in Add-ons Manager dialog.
    # Remove a speech dictionary entry.
    self.removeButton=wx.Button(self,label=_("&Remove"))
    self.removeButton.Disable()
    self.removeButton.Bind(wx.EVT_BUTTON,self.onRemoveClick)
    entryButtonsSizer.Add(self.removeButton)
    # Translators: The label of a button in Add-ons Manager to open the Add-ons website and get more add-ons.
    self.getAddonsButton=wx.Button(self,label=_("Store"))
    self.getAddonsButton.Bind(wx.EVT_BUTTON,self.onGetAddonsClick)
    entryButtonsSizer.Add(self.getAddonsButton)
    settingsSizer.Add(entryButtonsSizer)
    mainSizer.Add(settingsSizer,border=20,flag=wx.LEFT|wx.RIGHT|wx.TOP)
    # Translators: The label of a button to close the Addons dialog.
    closeButton = wx.Button(self, label=_("&Close"), id=wx.ID_CLOSE)
    closeButton.Bind(wx.EVT_BUTTON, lambda evt: self.Close())
    mainSizer.Add(closeButton,border=20,flag=wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.CENTER|wx.ALIGN_RIGHT)
    self.Bind(wx.EVT_CLOSE, self.onClose)
    self.EscapeId = wx.ID_CLOSE
    mainSizer.Fit(self)
    self.SetSizer(mainSizer)
    self.selfUpdateCheck = True
    self.refreshAddonsList()
    self.addonsList.SetFocus()
    self.Center(wx.BOTH | wx.CENTER_ON_SCREEN)
    
  def onAddClick(self,evt):
    index=self.addonsList.GetFirstSelected()
    if index == -1:
      return
    self.installAddon(self.storeAddons[index])
    
  def installAddon(self, addon, closeAfter=False, silent=False):
    if silent == False:
      ui.message(u"Téléchargement du module %s en cours " %(addon.name))
    data = self.cecitek.getAddonFile(addon.id, addon.versionId)
    
    if data is None:
      if silent == False:
        ui.message(u"Le téléchargement est impossible actuellement.")
      return False
    tmp = os.path.join(config.getUserDefaultConfigPath(), "storeDownloadedAddon.nvda-addon")
    log.info(u"Saving to %s" %(tmp))
    f = file(tmp, "wb")
    f.write(data)
    f.close()
    path = tmp
    if path is None:
      if silent == False:
        ui.message(u"Téléchargement de %s impossible" %(addon.name))
      return False
    if silent == False:
      ui.message(u"Installation en cours...")
    try:
      bundle=addonHandler.AddonBundle(path)
    except:
      log.error("Error opening addon bundle from %s"%path,exc_info=True)
      # Translators: The message displayed when an error occurs when opening an add-on package for adding. 
      if silent == False:
        gui.messageBox(_("Failed to open add-on package file at %s - missing file or invalid file format")%path,
		       # Translators: The title of a dialog presented when an error occurs.
		       _("Error"),
		       wx.OK | wx.ICON_ERROR)
        return False
    bundleName=bundle.manifest['name']
    prevAddon=None
    for addon in addonHandler.getAvailableAddons():
      if not addon.isPendingRemove and bundleName==addon.manifest['name']:
	prevAddon=addon
        break
    if prevAddon:
      prevAddon.requestRemove()
    if silent == False:
      progressDialog = gui.IndeterminateProgressDialog(gui.mainFrame,
			                               # Translators: The title of the dialog presented while an Addon is being installed.
			                               _("Installing Add-on"),
			                               # Translators: The message displayed while an addon is being installed.
			                               _("Please wait while the add-on is being installed."))
    try:
      gui.ExecAndPump(addonHandler.installAddonBundle,bundle)
    except:
      log.error("Error installing  addon bundle from %s"%addonPath,exc_info=True)
      self.refreshAddonsList()
      if silent == False:
        progressDialog.done()
        del progressDialog
      # Translators: The message displayed when an error occurs when installing an add-on package.
      if silent == False:
        gui.messageBox(_("Failed to install add-on from %s")%(addon.name),
		       # Translators: The title of a dialog presented when an error occurs.
		       _("Error"),
		       wx.OK | wx.ICON_ERROR)
      return False
    self.refreshAddonsList(activeIndex=-1)
    if silent == False:
      progressDialog.done()
      del progressDialog
      ui.message(u"Installation terminée.")
    if closeAfter:
      # #4460: If we do this immediately, wx seems to drop the WM_QUIT sent if the user chooses to restart.
      # This seems to have something to do with the wx.ProgressDialog.
      # The CallLater seems to work around this.
      wx.CallLater(1, self.Close)
    return True
  
      
  def onRemoveClick(self,evt):
    index=self.addonsList.GetFirstSelected()
    if index<0: return
    # Translators: Presented when attempting to remove the selected add-on.
    if gui.messageBox(_("Are you sure you wish to remove the selected add-on from NVDA?"),
		      # Translators: Title for message asking if the user really wishes to remove the selected Addon.
		      _("Remove Add-on"), wx.YES_NO|wx.ICON_WARNING) != wx.YES: return
    addon=self.getLocalAddon(self.storeAddons[index])
    addon.requestRemove()
    self.refreshAddonsList(activeIndex=index)
    self.addonsList.SetFocus()
    
  def getAddonState(self, addon):
    localAddon = self.getLocalAddon(addon)
    if localAddon:
      if localAddon.manifest['version'] < addon.latestVersion:
        self.addButton.SetLabel(u"Mettre à jour")
        return u"Mise à jour"
      else:
        self.addButton.SetLabel(u"Ré&installer")
        return u"Installé"
    else:
      self.addButton.Enable()
      self.addButton.SetLabel(u"&installer")
      return u"Pas installé"

  def selfUpdate(self):
    for addon in self.storeAddons:
      if addon.name.upper() == CECITEK_MODULE_NAME.upper():
        localAddon = self.getLocalAddon(addon)
        if localAddon and localAddon.manifest[u'version'] < addon.latestVersion:
          # We should self-update the Cecitek module itself.
          if gui.messageBox(_(u"Une nouvelle version du module Cecitek est disponible. Souhaitez-vous l'installer maintenant? Cela entraînera un redémarrage de NVDA."),
		            _(u"Mise à jour"),
                            wx.YES_NO|wx.ICON_WARNING) == wx.YES:
            ui.message(u"Mise à jour en cours...")
            ret = self.installAddon(addon, True, True)
            if ret: return
            self.selfUpdateCheck = False

  def refreshAddonsList(self,activeIndex=0):
    self.addonsList.DeleteAllItems()
    self.curAddons=[]
    # for addon in addonHandler.getAvailableAddons():
    # self.addonsList.Append((addon.manifest['summary'], self.getAddonStatus(addon), addon.manifest['version'], addon.manifest['author']))
    # self.curAddons.append(addon)
    if self.selfUpdateCheck is True:
      wx.CallLater(1, self.selfUpdate)
      self.selfUpdateCheck = False
    for addon in self.storeAddons:
      self.addonsList.Append((addon.name, self.getAddonState(addon), addon.latestVersion, addon.author))
    # select the given active addon or the first addon if not given
    curAddonsLen=len(self.curAddons)
    if curAddonsLen>0:
      if activeIndex==-1:
	activeIndex=curAddonsLen-1
      elif activeIndex<0 or activeIndex>=curAddonsLen:
	activeIndex=0
      self.addonsList.Select(activeIndex,on=1)
      self.addonsList.SetItemState(activeIndex,wx.LIST_STATE_FOCUSED,wx.LIST_STATE_FOCUSED)
    else:
      self.aboutButton.Disable()
      self.helpButton.Disable()
      self.removeButton.Disable()

  def getLocalAddon(self, storeAddon):
    for a in addonHandler.getAvailableAddons():
      if a.manifest['name'].upper() == storeAddon.name.upper():
        return a
    return None
  
  def _shouldDisable(self, addon):
    return not (addon.isPendingDisable or (addon.isDisabled and not addon.isPendingEnable))
    
  def onListItemSelected(self, evt):
    index=evt.GetIndex()
    storeAddon=self.storeAddons[index] if index>=0 else None
    addon = self.getLocalAddon(storeAddon)
    # #3090: Change toggle button label to indicate action to be taken if clicked.
    if addon is not None:
      # Translators: The label for a button in Add-ons Manager dialog to enable or disable the selected add-on.
      self.enableDisableButton.SetLabel(_("&Enable add-on") if not self._shouldDisable(addon) else _("&Disable add-on"))
      self.aboutButton.Enable(addon is not None and not addon.isPendingRemove)
      self.helpButton.Enable(bool(addon is not None and not addon.isPendingRemove and addon.getDocFilePath()))
      self.enableDisableButton.Enable(addon is not None and not addon.isPendingRemove)
      self.removeButton.Enable(addon is not None and not addon.isPendingRemove)
      
  def onClose(self,evt):
    self.Destroy()
    needsRestart = False
    for addon in addonHandler.getAvailableAddons():
      if (addon.isPendingInstall or addon.isPendingRemove
	  or addon.isDisabled and addon.isPendingEnable
	  or addon.isRunning and addon.isPendingDisable):
	needsRestart = True
	break
    if needsRestart:
      # Translators: A message asking the user if they wish to restart NVDA as addons have been added, enabled/disabled or removed. 
      # if gui.messageBox(_("Changes were made to add-ons. You must restart NVDA for these changes to take effect. Would you like to restart now?"),
      # Translators: Title for message asking if the user wishes to restart NVDA as addons have been added or removed. 
      # _("Restart NVDA"),
      # wx.YES|wx.NO|wx.ICON_WARNING)==wx.YES:
      core.restart()

  def onAbout(self,evt):
    index=self.addonsList.GetFirstSelected()
    if index<0: return
    manifest = self.getLocalAddon(self.storeAddons[index]).manifest
    # Translators: message shown in the Addon Information dialog. 
    message=_("""{summary} ({name})
Version: {version}
Author: {author}
Description: {description}
""").format(**manifest)
    url=manifest.get('url')
    if url: 
      # Translators: the url part of the About Add-on information
      message+=_("URL: {url}").format(url=url)
      # Translators: title for the Addon Information dialog
      title=_("Add-on Information")
      gui.messageBox(message, title, wx.OK)
      
  def onHelp(self, evt):
    index = self.addonsList.GetFirstSelected()
    if index < 0:
      return
    path = self.curAddons[index].getDocFilePath()
    os.startfile(path)
  
  def onEnableDisable(self, evt):
    index=self.addonsList.GetFirstSelected()
    if index<0: return
    addon=self.curAddons[index]
    shouldDisable = self._shouldDisable(addon)
    # Counterintuitive, but makes sense when context is taken into account.
    addon.enable(not shouldDisable)
    self.enableDisableButton.SetLabel(_("&Enable add-on") if shouldDisable else _("&Disable add-on"))
    self.refreshAddonsList(activeIndex=index)
    
  def onGetAddonsClick(self,evt):
    ADDONS_URL = "https://www.cecitek.fr/nvda"
    os.startfile(ADDONS_URL)
    