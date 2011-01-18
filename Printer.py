from wx.html import HtmlEasyPrinting

class Printer(HtmlEasyPrinting):
    def __init__(self):
        HtmlEasyPrinting.__init__(self)

    def GetHtmlText(self,text):
        html_text = text.replace('\n\n','<P>')
        html_text = text.replace('\n', '<BR>')
        return html_text

    def Print(self, text, doc_name):        
        self.PrintText(self.GetHtmlText(text),doc_name)

    def PreviewText(self, text, doc_name):        
        HtmlEasyPrinting.PreviewText(self, self.GetHtmlText(text))