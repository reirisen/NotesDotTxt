# by: reirisen (c) 2009-11, All Rights Reserved.
# This code is provided 'as-is', without any express or implied
# warranty. In no event will the authors be held liable for any damages
# arising from the use of this software.

import os.path
import wx, os
from ctypes import *
import time
import shutil
from Printer import Printer
from util import *
from TaskBarIcon import *

ID_TOPICSPLIT = 1000
ID_TOPICTREE  = 1001
ID_TOPICTEXT  = 1002

ID_TOPICNEW   = 1003
ID_NOTENEW    = 1004
ID_EXIT       = 1005
ID_EDIT       = 1006
ID_DELETE     = 1007
ID_MODIFY     = 1008
ID_SAVENOTE   = 1009
ID_SEARCHBUTTON = 1010
ID_SEARCH_LIST = 1011
ID_PASSWORDREM = 1012
ID_INSERTDATE = 1013
ID_PRINTNOTE = 1014

DEF_TITLE = 'Notes dot TXT (c) 2009 - 2011'
DEF_TOPICS = "MyNotes"

ITEM_NOTE = 1
ITEM_TOPIC = 2

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(-1, -1))
        
        self.Initialized = 0
        wx.EVT_CLOSE(self, self.OnCloseWindow)
        wx.EVT_SIZE(self, self.OnSizeWindow)
        noteIconFile = "images/MyIcon.ico"
        noteIcon = wx.Icon(noteIconFile, wx.BITMAP_TYPE_ICO)
        self.SetIcon(noteIcon)
        
        self.systray = TaskBarIcon(self, noteIconFile, title)
        self.Bind(wx.EVT_ICONIZE, self.OnMinimizeWindow)
        
        # Initialize Split Window
        self.splitterTopics = wx.SplitterWindow(self, ID_TOPICSPLIT, style=wx.SP_3D)
        self.splitterTopics.SetMinimumPaneSize(20)
        self.tabNotebook = wx.Notebook(self.splitterTopics, -1, style=wx.NB_TOP)
        self.treeTopics = wx.TreeCtrl(self.tabNotebook, ID_TOPICTREE, wx.DefaultPosition, (-1,-1), 
            wx.TR_HAS_BUTTONS | wx.TR_EDIT_LABELS)
        fontTopics = wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Courier New')
        self.treeTopics.SetFont(fontTopics)
        self.tabNotebook.AddPage(self.treeTopics, "Notes")
        
        self.textContent = wx.TextCtrl(self.splitterTopics, ID_TOPICTEXT, '', size=(-1, -1), 
            style=wx.HSCROLL | wx.TE_MULTILINE | wx.TE_PROCESS_ENTER | wx.TE_PROCESS_TAB)
        fontContent = wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Courier New')
        self.textContent.SetFont(fontContent)
        self.textContent.SetEditable(0)
        
        self.splitterTopics.SplitVertically(self.tabNotebook, self.textContent)
        size =  self.GetSize()
        self.splitterTopics.SetSashPosition(size.x/3 + size.x/4 )
        self.Bind(wx.EVT_SPLITTER_DCLICK, self.OnSplitterDoubleClick, id=ID_TOPICSPLIT)
        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.OnSplitterSashChanged, id=ID_TOPICSPLIT)
        
        self.searchPanel = wx.Panel(self.tabNotebook, -1)
        wx.StaticText(self.searchPanel, -1, "Look for:", (5, 5), style=wx.ALIGN_RIGHT)
        nsize = self.GetSize()
        self.searchText = wx.TextCtrl(self.searchPanel, -1, '', (5, 20), size=(nsize.x/3 + nsize.x/4 - 20, -1))
        wx.StaticText(self.searchPanel, -1, "Search Mode:", (5, 45), style=wx.ALIGN_RIGHT)
        self.searchMethod = wx.ComboBox(self.searchPanel, -1, pos=(5, 60), size=(nsize.x/3 + nsize.x/4 - 20, -1), 
            choices=['Current Note','Current Topic', 'All Topics'], style=wx.CB_READONLY)
        self.searchMethod.SetSelection(0)
        wx.Button(self.searchPanel, ID_SEARCHBUTTON, '&Search', (5, 85))
        self.Bind(wx.EVT_BUTTON, self.OnSearchButton, id=ID_SEARCHBUTTON)
        wx.StaticText(self.searchPanel, -1, "Search Results:", (5, 110), style=wx.ALIGN_RIGHT)
        self.searchResults = wx.ListCtrl(self.searchPanel, ID_SEARCH_LIST, (5, 125), 
            size=(nsize.x/3 + nsize.x/4 - 20, nsize.y-180), style=wx.LC_REPORT)
        self.searchResults.InsertColumn(0, 'Note')
        self.searchResults.InsertColumn(1, 'Pos')
        csize = self.searchResults.GetSize()
        self.searchResults.SetColumnWidth(0, 3*(csize.x/4)-10)
        self.searchResults.SetColumnWidth(1, csize.x/4)
        self.searchResults.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSearchItemSelected, id=ID_SEARCH_LIST)
        self.searchResultPaths = {}
        self.tabNotebook.AddPage(self.searchPanel, "Search")
        
        self.toolbarTopic = self.CreateToolBar()
        self.toolbarTopic.AddLabelTool(ID_TOPICNEW, '', wx.Bitmap('images/img_newtopic.png'), 
            longHelp = "Create new Topic")
        self.toolbarTopic.AddLabelTool(ID_NOTENEW, '', wx.Bitmap('images/img_newnote.png'), 
            longHelp = "Create new Note under a Topic")
        self.toolbarTopic.AddSeparator()
        self.toolbarTopic.AddLabelTool(ID_MODIFY, '', wx.Bitmap('images/img_modify.png'),
            longHelp = "Modify the selected note")
        self.toolbarTopic.AddLabelTool(ID_INSERTDATE, '', wx.Bitmap('images/img_date.png'), 
            longHelp = "Insert date and time to note being modified")
        self.toolbarTopic.AddLabelTool(ID_SAVENOTE, '', wx.Bitmap('images/img_save.png'), 
            longHelp = "Save the modified selected note")
        self.toolbarTopic.AddLabelTool(ID_PRINTNOTE, '', wx.Bitmap('images/img_print.png'), 
            longHelp = "Print the selected note")            
        self.toolbarTopic.AddSeparator()
        self.toolbarTopic.AddLabelTool(ID_EDIT, '', wx.Bitmap('images/img_rename.png'), 
            longHelp = "Rename the selected topic/note")
        self.toolbarTopic.AddLabelTool(ID_DELETE, '', wx.Bitmap('images/img_delete.png'), 
            longHelp = "Delete selected topic/note")        
        self.toolbarTopic.SetToolBitmapSize((32, 32))
        self.toolbarTopic.Realize()
        
        self.rootpath = os.getcwd() + "/notes"
        
        self.root = self.treeTopics.AddRoot(DEF_TOPICS, 2)
        self.onEditFlag = 0
        self.onEditItem = self.root
        self.onSelectedNote = self.root
        self.treeTopics.SetPyData(self.root, self.rootpath)
        self.treeTopics.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTopicSelChanged, id=ID_TOPICTREE)
        self.treeTopics.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnTopicRightClick, id=ID_TOPICTREE)        
        self.treeTopics.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnTopicEdit, id=ID_TOPICTREE)
        self.treeTopics.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnBeginDrag)
        self.treeTopics.Bind(wx.EVT_TREE_END_DRAG, self.OnEndDrag)
        
        menuMain = wx.MenuBar()
        menuFile = wx.Menu()
        menuEdit = wx.Menu()
        menuFile.Append(ID_TOPICNEW, '&New Topic', 'Create new Topic')
        wx.EVT_MENU(self, ID_TOPICNEW, self.OnMenuNewTopic )
        menuFile.Append(ID_NOTENEW, 'Ne&w Note', 'Create new Note under a Topic')
        wx.EVT_MENU(self, ID_NOTENEW, self.OnMenuNewNote )
        menuFile.AppendSeparator()
        menuFile.Append(ID_EXIT, 'E&xit', 'Exit application')    
        wx.EVT_MENU(self, ID_EXIT, self.OnCloseWindow )
        menuEdit.Append(ID_MODIFY, '&Modify Note', 'Modify the selected note')
        wx.EVT_MENU(self, ID_MODIFY, self.OnModifyNote )
        menuEdit.Append(ID_SAVENOTE, '&Save Note', 'Save the modified selected note')
        wx.EVT_MENU(self, ID_SAVENOTE, self.OnSaveNote )
        menuEdit.AppendSeparator()
        menuEdit.Append(ID_EDIT, '&Rename Topic/Note', 'Rename the selected topic/note')
        wx.EVT_MENU(self, ID_EDIT, self.OnMenuEditTopicNote )
        menuEdit.Append(ID_DELETE, '&Delete Topic/Note', 'Delete selected topic/note')
        wx.EVT_MENU(self, ID_DELETE, self.OnMenuDeleteTopicNote )
        wx.EVT_MENU(self, ID_INSERTDATE, self.OnInsertDate )
        wx.EVT_MENU(self, ID_PRINTNOTE, self.OnPrintNote )                
        menuTools = wx.Menu()
        menuTools.Append( ID_PASSWORDREM, '&Pass (Enc/Dec)yptor\tCtrl+E', 'Encrypts or Decrypts password')
        wx.EVT_MENU(self, ID_PASSWORDREM, self.OnPassEncDecryptor )
        menuMain.Append(menuFile, '&File')
        menuMain.Append(menuEdit, '&Edit')
        menuMain.Append(menuTools, '&Tools')
        self.SetMenuBar(menuMain)
        
        self.menuPopUp = menuEdit
        
        self.statusbarTopics = self.CreateStatusBar()
        self.statusbarTopics.SetStatusText("Ready")
        screensize = wx.GetDisplaySize()
        self.SetSize(((screensize.x/4)*3, (screensize.y/4)*3))
        self.Center()
        self.Show(True)
        
        self.imageList = wx.ImageList(16, 16)
        self.imageList.Add(wx.Bitmap('images/img_topic.png'))
        self.imageList.Add(wx.Bitmap('images/img_note.png'))
        self.imageList.Add(wx.Bitmap('images/img_mynotes.png'))
        self.treeTopics.SetImageList(self.imageList)
        
        if os.path.exists(self.rootpath) != True:
            os.makedirs(self.rootpath)
        self.LoadTopics(self.rootpath, self.root)
        self.treeTopics.SelectItem(self.root, 1)
        self.treeTopics.Expand(self.root)
        
        self.Initialized = 1
    
    def OnMinimizeWindow(self, event):
        self.systray.OnTaskBarDeactivate(event)
        
    def OnPassEncDecryptor(self, event):
        if os.path.exists('tools/myfishlite.dll') == True:
            rundll32 = os.environ['SystemRoot'] + '/system32/rundll32.exe'
            os.spawnl(os.P_NOWAIT, rundll32, rundll32, 'tools/myfishlite.dll,RunMe')
        
    def OnCloseWindow(self, event):
        self.systray.OnTaskBarDeactivate(event)
        
    def OnSizeWindow(self, event):
        if self.Initialized:
            wsize = self.GetSize()
            self.searchResults.SetSize((-1, wsize.y - 300))
        event.Skip()
        
    def OnSearchItemSelected(self, event):
        note = self.searchResultPaths[event.m_itemIndex]
        npath = self.treeTopics.GetPyData(note)
        self.treeTopics.SelectItem(note, 1)
        subitem = self.searchResults.GetItem(event.m_itemIndex, 1)
        scolrow = subitem.GetText().split("/")
        col = int(scolrow[0])-1
        row = int(scolrow[1])-1
        pos = self.textContent.XYToPosition(col,row)
        self.textContent.ShowPosition(pos)
        self.textContent.SetSelection(pos, pos+10)
        self.textContent.SetStyle(pos, pos+10, self.textContent.GetDefaultStyle())
        
    def SearchTextContent(self, notelabel, strtext, note):
        nLines = self.textContent.GetNumberOfLines()
        for line in range(0, nLines):
            if self.textContent.GetLineLength(line):
                strline = self.textContent.GetLineText(line).lower()
                col = strline.find(strtext)
                if col != -1:
                    nitems = self.searchResults.GetItemCount()
                    self.searchResults.InsertStringItem(nitems, notelabel)
                    self.searchResults.SetStringItem(nitems, 1, str(col+1) + "/" + str(line+1))
                    self.searchResultPaths[nitems] = note
    
    def OnSearchButton(self, event):
        item = event.GetSelection()
        if item == 0:
            self.searchResultPaths.clear()
            self.searchResults.DeleteAllItems()
            note = self.onSelectedNote
            topic = self.treeTopics.GetItemParent(note)
            stopic = ""
            if topic != self.root:
                stopic = self.treeTopics.GetItemText(topic) + "/"
            snote = stopic + self.treeTopics.GetItemText(note)
            npath = self.treeTopics.GetPyData(note)
            if note != None and note != self.root and os.path.isfile(npath):
                text = self.searchText.GetValue().lower()
                stext = text.strip(' ')
                if stext != "":
                    self.SearchTextContent(snote, stext, note)
                    return
    
    def OnSplitterSashChanged(self, event):
        nsize = self.splitterTopics.GetSashPosition()
        self.searchText.SetSize((nsize - 20, -1))
        self.searchMethod.SetSize((nsize - 20, -1))
        self.searchResults.SetSize((nsize - 20, -1))
        csize = self.searchResults.GetSize()
        self.searchResults.SetColumnWidth(0, 3*(csize.x/4))
        self.searchResults.SetColumnWidth(1, csize.x/4)
        
    def Terminate(self):
        if self.onEditFlag:
            self.OnSaveNote(None)
        self.systray.Destroy()
        self.Destroy()
    
    def OnModifyNote(self, event):
        if self.onEditFlag:
            return
        item = self.treeTopics.GetSelection()
        if item != None and item != self.root:
            path = self.treeTopics.GetPyData(item)
            if os.path.isfile(path):
                self.textContent.SetEditable(1)
                self.onEditFlag = 1
                self.onEditItem = item
        else:
            self.ShowMessage("Please select a note to edit.")
            
    def OnSaveNote(self, event):
        if not self.onEditFlag:
            return
        reply = wx.ID_YES
        if event == None:
            msg = wx.MessageDialog(None, "Do you want to save changes to the modified note?", 
                    'Question', wx.YES_NO | wx.CANCEL | wx.NO_DEFAULT | wx.ICON_QUESTION)
            reply = msg.ShowModal()
        if reply == wx.ID_YES:
            path = self.treeTopics.GetPyData(self.onEditItem)
            success = 1
            try:
                success = self.textContent.SaveFile(path)
            except:
                success = 0
            if not success:
                self.ShowMessage("Error saving the file.", 1)
        elif reply == wx.ID_CANCEL:
                self.treeTopics.SelectItem(self.onEditItem, 1)
                return 0
        self.textContent.SetEditable(0)
        self.onEditFlag = 0
        return 1
                
    def OnMenuEditTopicNote(self, event):
        item = self.treeTopics.GetSelection()
        if item != None and item != self.root:
            self.treeTopics.EditLabel(item)
    
    def ShowMessage(self, message, error=0):
        if error:
            dial = wx.MessageDialog(None, message, 'Error', wx.ICON_EXCLAMATION)
            dial.ShowModal()
        else:
            dial = wx.MessageDialog(None, message, 'Info', wx.OK)
            dial.ShowModal()
    
    def OnMenuDeleteTopicNote(self, event):
        if self.onEditFlag:
            cont = self.OnSaveNote(None)
            if not cont: return
        item = self.treeTopics.GetSelection()
        if item == None or item == self.root:
            return
        text = ""
        path = self.treeTopics.GetPyData(item)
        if os.path.isdir(path):
            text = "Are you sure you want to delete the selected topic and its entirety?"
        else:
            text = "Are you sure you want to delete the selected note?"
        msg = wx.MessageDialog(None, text, 'Question', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        reply = msg.ShowModal()
        if reply == wx.ID_YES:
            success = 1
            try:
                if os.path.isdir(path):
                    os.rmdir(path)
                else:
                    os.remove(path)                    
            except:
                success = 0
            if success:
                self.treeTopics.Delete(item)
            else:
                self.ShowMessage("Failed to delete the selected topic/note!", 1)
            
    def OnTopicEdit(self, event):
        item = event.GetItem()
        oldname = self.treeTopics.GetItemText(item)
        wx.CallAfter(self.AfterEditLabel, self,item, oldname)
     
    def AfterEditLabel(pro, self, item, oldname):
        if item == self.root:
            self.treeTopics.SetItemText(item, DEF_TOPICS)
            return
        newname = self.treeTopics.GetItemText(item)
        path = self.treeTopics.GetPyData(item)
        newpath = ""
        (head, tail) = os.path.split(path)
        if os.path.isdir(path):
            newpath = os.path.join(head, newname)
        else:
            newpath = os.path.join(head, newname) + ".txt"
        success = 1
        try:
            os.rename(path, newpath)
        except:
            success = 0
        if success:
            self.treeTopics.SetPyData(item, newpath)
            if os.path.isdir(newpath):
                self.treeTopics.DeleteChildren(item)
                self.LoadTopics(newpath, item)
        else:
            self.treeTopics.SetItemText(item, oldname)
            self.ShowMessage("Failed to rename the selected topic/note!", 1)
        self.treeTopics.SelectItem(item)

    def GenerateName(self, folder, isfile=1):
        newpath = ""
        if isfile:
            newnote = "New Note"
            newpath = folder + "\\" + newnote + ".txt"
            counter = 1
            while os.path.exists(newpath) == True:
                newnote = "New Note" + "(" + str(counter) + ")"
                counter = counter + 1
                newpath = folder + "\\" + newnote + ".txt"
            return (newnote, newpath)
        else:
            newtopic = "New Topic"
            newpath = folder + "\\" + newtopic
            counter = 1
            while os.path.exists(newpath) == True:
                newtopic = "New Topic" + "(" + str(counter) + ")"
                counter = counter + 1
                newpath = folder + "\\" + newtopic
            return (newtopic, newpath)
            
    def OnMenuNewTopic(self, event):
        if self.onEditFlag:
            cont = self.OnSaveNote(None)
            if not cont: return
        item = self.treeTopics.GetSelection()
        if item == None:
            item = self.root
        path = self.treeTopics.GetPyData(item)
        if os.path.isfile(path):
            parent = self.treeTopics.GetItemParent(item)
            item = parent
            path = self.treeTopics.GetPyData(item)
        (topicname, newpath) = self.GenerateName(path, 0)
        newtopic = self.treeTopics.AppendItem(item, topicname, 0)
        os.makedirs(newpath)
        self.treeTopics.SetPyData(newtopic, newpath)
        self.treeTopics.Expand(item)
        self.treeTopics.EditLabel(newtopic)
                    
    def OnMenuNewNote(self, event):
        if self.onEditFlag:
            cont = self.OnSaveNote(None)
            if not cont: return
        topic = self.treeTopics.GetSelection()
        if topic == None:
            topic = self.root
        topicpath =  self.treeTopics.GetPyData(topic)
        if os.path.isfile(topicpath):
            parent = self.treeTopics.GetItemParent(topic)
            topic = parent
            topicpath =  self.treeTopics.GetPyData(topic)
        (notename, newnotepath) = self.GenerateName(topicpath, 1)
        newnote = self.treeTopics.AppendItem(topic, notename, 1)
        newfile = open(newnotepath, 'w')
        newfile.write('[add your notes here]')
        newfile.close()
        self.treeTopics.SetPyData(newnote, newnotepath)
        self.treeTopics.Expand(topic)
        self.textContent.LoadFile(newnotepath)
        self.textContent.SetEditable(1)
        self.onEditFlag = 1
        self.onEditItem = newnote
        self.treeTopics.EditLabel(newnote)
        
    def OnInsertDate(self, event):                
        if not self.onEditFlag: return                
        dstr = time.asctime(time.localtime()) + '\n'
        self.textContent.WriteText(dstr)    
        
    def OnSplitterDoubleClick(self, event):
        self.OnSplitterSashChanged(event)
        
    def OnTopicSelChanged(self, event):
        item = event.GetItem()
        if self.onEditFlag and item == self.onEditItem:
            return
        if self.onEditFlag:
            cont = self.OnSaveNote(None)
            if not cont: return
        if self.onSelectedNote != item:
            path = self.treeTopics.GetPyData(item)
            if path != None and os.path.isfile(path):
                self.textContent.SetEditable(0)
                self.textContent.LoadFile(path)
                self.onSelectedNote = item
                
    def OnTopicRightClick(self, event):        
        #if self.onEditFlag: return        
        self.OnTopicSelChanged( event )
        self.treeTopics.SelectItem(event.GetItem())
        self.PopupMenu( self.menuPopUp, event.GetPoint() )

    def OnPrintNote(self, event):
        item = self.onSelectedNote
        path = self.treeTopics.GetPyData(item)
        if path != None and os.path.isfile(path):
            toprint = Printer()
            content = self.textContent.GetValue()
            (fname, ext) = os.path.splitext(path)
            (head, tail) = os.path.split(fname)
            toprint.PreviewText( '[' + tail + ']\n\n' + content, tail )
        
    def LoadTopics(self, path, root):
        notes = {}
        foundtotal = 0
        files = os.listdir(path)
        for file in files:
            fpath = path + "\\" + file
            if os.path.isdir(fpath):
                topic = self.treeTopics.AppendItem(root, file, 0)
                found = self.LoadTopics(fpath, topic)
                #if found == 0:
                    #self.treeTopics.Delete(topic)
                #else:
                self.treeTopics.SetPyData(topic, fpath)
                foundtotal += found
            else:
                (fname, ext) = os.path.splitext(file)
                if ext == ".txt":
                    notes[fname] = fpath            
        for note, fpath in notes.iteritems():
            topic = self.treeTopics.AppendItem(root, note, 1)
            self.treeTopics.SetPyData(topic, fpath)
        return foundtotal+len(notes)
        
    def GetItemType(self, item):
        path = self.treeTopics.GetPyData(item)
        if path != None:
            if os.path.isfile(path):
                return ITEM_NOTE
            elif os.path.isdir(path):
                return ITEM_TOPIC
        return 0
        
    def IsSameItem(self, item1, item2):
        if item1 == item2:
            return True
        return False
    
    def IsItemInsideItem(self, rootitem, item):
        if self.IsSameItem( self.root, item ):
            return False
        parentitem = self.treeTopics.GetItemParent( item )
        if self.IsSameItem( self.root, parentitem ):
            return False
        if self.IsSameItem( rootitem, parentitem ):
            return True
        else:
            return self.IsItemInsideItem( rootitem, parentitem )
        return False

    def IsItemParent(self, parent, item):
        parentitem = self.treeTopics.GetItemParent( item )
        if self.IsSameItem( parent, parentitem ): return True
        return False

    def MoveTopicToTopic(self, srctopic, desttopic):
        if self.IsSameItem( srctopic, desttopic ): return
        if self.IsItemInsideItem( srctopic, desttopic ): return
        if self.IsItemParent( desttopic, srctopic ): return
        src = self.treeTopics.GetPyData(srctopic)
        dst = self.treeTopics.GetPyData(desttopic)
        movedst = PathAppend(dst, GetFileName(src))
        if os.path.exists( movedst ) and os.path.isdir( movedst ):
            self.ShowMessage("Topic already exists.", 1)
        elif SafeMoveFolder( src, movedst ):
            movedtopic = self.treeTopics.AppendItem(desttopic, GetFileTitle(movedst), 0)
            self.treeTopics.SetPyData(movedtopic, movedst)
            self.treeTopics.Delete(srctopic)
            self.LoadTopics(movedst, movedtopic)
            self.treeTopics.Expand(desttopic)
        else:
            self.ShowMessage("Error moving the topic.", 1)
        return
    
    def MoveNoteToTopic(self, noteitem, topicitem):
        if self.IsSameItem( noteitem, topicitem ): return
        if self.IsItemParent( topicitem, noteitem ): return
        notefile = self.treeTopics.GetPyData(noteitem)
        topicfolder = self.treeTopics.GetPyData(topicitem)
        dstfile = PathAppend(topicfolder, GetFileName(notefile))
        if os.path.exists( dstfile ):
            self.ShowMessage("Note already exist in the topic.", 1)
        elif SafeMoveFile( notefile, dstfile ):
            movednote = self.treeTopics.AppendItem(topicitem, GetFileTitle(dstfile), 1)
            self.treeTopics.SetPyData(movednote, dstfile)
            self.treeTopics.Delete(noteitem)
            self.treeTopics.Expand(topicitem)
        else:
            self.ShowMessage("Error moving the note.", 1)
        return
        
    def OnBeginDrag(self, event):
        if not self.IsSameItem( self.root, event.GetItem() ):
            event.Allow()
            self.dragitem = event.GetItem()
    
    def OnEndDrag(self, event):
        destitem = event.GetItem()
        if not destitem.IsOk(): return
        if self.GetItemType( destitem ) == ITEM_TOPIC:
            if self.GetItemType( self.dragitem ) == ITEM_TOPIC:
                self.MoveTopicToTopic( self.dragitem, destitem )    
            else:
                self.MoveNoteToTopic( self.dragitem, destitem )
            
class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, DEF_TITLE)
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

app = MyApp(0)
app.MainLoop()
