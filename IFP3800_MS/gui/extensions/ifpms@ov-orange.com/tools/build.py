# A very simple setup script to create 2 executables.
#
# hello.py is a simple "hello, world" type program, which alse allows
# to explore the environment in which the script runs.
#
# test_wx.py is a simple wxPython program, it will be converted into a
# console-less program.
#
# If you don't have wxPython installed, you should comment out the
#   windows = ["test_wx.py"]
# line below.
#
#
# Run the build process by entering 'setup.py py2exe' or
# 'python setup.py py2exe' in a console prompt.
#
# If everything works well, you should find a subdirectory named 'dist'
# containing some files, among them hello.exe and test_wx.exe.


from distutils.core import setup
import py2exe
import matplotlib
import sys, os

# Special hack necessary to import the "pylib" directory. See bug:
# http://bugs.activestate.com/show_bug.cgi?id=74925
old_sys_path = sys.path[:]
pylib_path = os.path.join(os.getcwd(), "..", "pylib")
sys.path.append(pylib_path)
import collector
import channel
#sys.path = old_sys_path

setup(
    # The first three parameters are not required, if at least a
    # 'version' is given, then a versioninfo resource is built from
    # them and added to the executables.
    version = "0.5.0",
    description = "py2exe sample script",
    name = "py2exe samples",
    data_files=matplotlib.get_py2exe_datafiles(),
    options={'py2exe': {
        'includes': ['matplotlib.backends.backend_wxagg','matplotlib.backends.backend_tkagg','collector', 'channel'],
        'excludes': ['_gtkagg'],
        "compressed": 1,"optimize": 2,"ascii": 1,"bundle_files": 1,
     }},
    # targets to build
    windows = ["net_sample_plot.py","raw_sample_preprocess.py"],
    console = ["net_sample_dump.py","raw_sample_fft.py"],
    )
