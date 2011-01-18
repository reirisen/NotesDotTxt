from distutils.core import setup
import py2exe, sys, os

sys.argv.append('py2exe')

setup(
	name='NotesDotTxt',
    version='1.0',
    description='Notes dot TXT',
    author='Pogisys',
	copyright='Copyright (c) 2009-11',
	windows = [{'script': "NotesDotTxt.pyw", "icon_resources": [(1, "images/MyIcon.ico")]}],
	options = {'py2exe': {'bundle_files': 1}},
	data_files=[("images", 
		["images/MyIcon.ico", 
		"images/img_delete.png", 
		"images/img_modify.png", 
		"images/img_mynotes.png", 
		"images/img_newnote.png", 
		"images/img_newtopic.png", 
		"images/img_note.png", 
		"images/img_rename.png", 
		"images/img_save.png", 
		"images/img_topic.png",
		"images/img_date.png",
		"images/img_print.png"]),
		("tools", ["tools/myfishlite.dll"])],
	zipfile = None,
)