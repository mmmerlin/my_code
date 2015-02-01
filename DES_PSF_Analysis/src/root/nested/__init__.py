from os import listdir, system
from os.path import isfile
from string import zfill

if __name__ == '__main__':

    path = '/mnt/hgfs/VMShared/Data/des_new_darks/'
    files = [filename for filename in listdir(path) if isfile(path + filename)]
    overscan_script = '/mnt/hgfs/VMShared/Code/git/my_functions/overscanDECam.py'
    
    for filename in files:
        for i in range(1,32):
            outfile = path + 'split/' + filename + '_ext_N' + zfill(i,2) + '.fits' 
            if isfile(outfile):
                print "Skipped existing file: %s"%outfile
            else:
                argstring = ' -i ' + path + filename + ' -o ' + outfile + ' -e N' + str(i)
                system('python ' + overscan_script + argstring)
            
            outfile = path + 'split/' + filename + '_ext_S' + zfill(i,2) + '.fits' 
            if isfile(outfile):
                print "Skipped existing file: %s"%outfile
            else:
                argstring = ' -i ' + path + filename + ' -o ' + outfile + ' -e S' + str(i)
                system('python ' + overscan_script + argstring)
            
        
