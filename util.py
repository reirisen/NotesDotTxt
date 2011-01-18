import shutil, os

def GetFileName(srcfile):
    sfile = srcfile.rstrip(os.pathsep)
    (head, tail) = os.path.split(sfile)
    return tail

def GetFileTitle(srcfile):
    (name, ext) = os.path.splitext(GetFileName(srcfile))
    return name

def PathAppend(dst, src):
    return os.path.join(dst, src)

def SafeMoveFile(src, dst):
    success = 0
    if not os.path.exists(dst):
        try:
            shutil.copyfile(src, dst)
            success = 1
        except: success = 0
    if success: os.remove(src)
    return success

def SafeMoveFolder(src, dst):
    success = 0
    if not os.path.exists(dst):
        try:
            shutil.copytree(src, dst)
            success = 1
        except:
            success = 0
    if success: shutil.rmtree( src )
    return success
