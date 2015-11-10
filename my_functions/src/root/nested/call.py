import os
####options are '--displayTrimmed', '--displayUnTrimmed', '--doGainCorrection'

script = 'python DMImageAssembly.py'

args = '/mnt/hgfs/VMShared/data/temp/davis_raw.fits --displayUnTrimmed'


os.system(script + ' ' + args)
print 'done'