import wx, os

class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self, frame, iconfile, title):
        wx.TaskBarIcon.__init__(self)

        self.frame = frame
        self.SetIcon(wx.Icon(iconfile, wx.BITMAP_TYPE_ICO), title)
        self.Bind(wx.EVT_MENU, self.OnTaskBarActivate, id=1)
        self.Bind(wx.EVT_MENU, self.OnTaskBarDeactivate, id=2)
        self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=3)
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarActivate)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        menu.Append(1, 'Restore')
        menu.Append(2, 'Minimize')        
        menu.AppendSeparator()
        menu.Append(3, 'Exit')
        return menu

    def OnTaskBarClose(self, event):
        self.frame.Terminate()

    def OnTaskBarActivate(self, event):
        if not self.frame.IsShown():
            self.frame.Show()
            self.frame.Restore()

    def OnTaskBarDeactivate(self, event):
        if self.frame.IsShown():
            self.frame.Hide()
