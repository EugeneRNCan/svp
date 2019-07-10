'''
Warning : Before executing this script make sure
--you make a back-up folder of the svp directory just in case,
--you have your python 2.7 directory and Scripts folder path in the value of the Path environment variable,
--you have 2to3 in your python interpreter (you can pip install 2to3 in a cmd prompt)
--and this script is in the svp directory thst you want to upgrade to python 3.7
'''



import os


for root, dirs, files in os.walk(".", topdown=True):
    for name in files:
        if ".py" in name and ".pyc" not in name and ".bak" not in name and "FindAndReplace.py" not in name:

            module = os.path.join(root, name).center(len(os.path.join(root, name)) + 2, "\"").ljust(len(os.path.join(root, name)) + 3)
            os.system('2to3 -w -n ' + module)
