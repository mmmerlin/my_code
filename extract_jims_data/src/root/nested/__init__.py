import pyfits

data = pyfits.open('/mnt/hgfs/VMShared/output/QE_LSST/Jim_results/112-04_QE.fits')['QE_CURVES'].data

wl = data.field('WAVELENGTH')

amp01 = data.field('AMP01')
amp02 = data.field('AMP02')
amp03 = data.field('AMP03')
amp04 = data.field('AMP04')
amp05 = data.field('AMP05')
amp06 = data.field('AMP06')
amp07 = data.field('AMP07')
amp08 = data.field('AMP08')
amp09 = data.field('AMP09')
amp10 = data.field('AMP10')
amp11 = data.field('AMP11')
amp12 = data.field('AMP12')
amp13 = data.field('AMP13')
amp14 = data.field('AMP14')
amp15 = data.field('AMP15')
amp16 = data.field('AMP16')

for i in range(len(wl)):
    print str(wl[i]) + \
    '\t' + str(amp01[i]) + \
    '\t' + str(amp02[i]) + \
    '\t' + str(amp03[i]) + \
    '\t' + str(amp04[i]) + \
    '\t' + str(amp05[i]) + \
    '\t' + str(amp06[i]) + \
    '\t' + str(amp07[i]) + \
    '\t' + str(amp08[i]) + \
    '\t' + str(amp09[i]) + \
    '\t' + str(amp10[i]) + \
    '\t' + str(amp11[i]) + \
    '\t' + str(amp12[i]) + \
    '\t' + str(amp13[i]) + \
    '\t' + str(amp14[i]) + \
    '\t' + str(amp15[i]) + \
    '\t' + str(amp16[i])
    
print ""
    
    
