import os

script = 'python DMImageAssembly.py'


# args = '/mnt/hgfs/VMShared/useful/ITL_400.fits --displayTrimmed --doGainCorrection'
args = '/mnt/hgfs/VMShared/useful/ITL_1100.fits --displayTrimmed --doGainCorrection'
# args = '/mnt/hgfs/VMShared/useful/ITL_400.fits --displayUnTrimmed'
# args = '/mnt/hgfs/VMShared/useful/ITL_1100.fits --displayTrimmed'

# args = '/mnt/hgfs/VMShared/useful/new_e2v_1100.fits --displayTrimmed --doGainCorrection'
# args = '/mnt/hgfs/VMShared/useful/new_e2v_1100.fits'
# args = '/mnt/hgfs/VMShared/useful/new_e2v_400.fits --displayTrimmed --doGainCorrection'
# args = '/mnt/hgfs/VMShared/useful/new_e2v_400.fits --displayUnTrimmed'
# args = '/mnt/hgfs/VMShared/useful/new_e2v_400.fits --displayTrimmed'


# args = '/mnt/hgfs/VMShared/useful/113-03_dark_example.fits --displayTrimmed'
# args = '/mnt/hgfs/VMShared/useful/114-04_ITL_fe55.fits --displayTrimmed'



args = '/mnt/hgfs/VMShared/data/useful/g08_gal.fits --displayUnTrimmed'


os.system(script + ' ' + args)
print 'done'