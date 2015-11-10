from __builtin__ import str
import pylab as pl
import numpy as np
from root_functions import CANVAS_HEIGHT, CANVAS_WIDTH
from ROOT import TCanvas, TGraph, TF1


if __name__ == '__main__':

    print "running"
    
    # filename = '/mnt/hgfs/VMShared/Data/QE_LSST/diode_data/test.txt'
    filename = '/mnt/hgfs/VMShared/Data/QE/sensitivity.txt'
    ts, ys = np.loadtxt(filename, skiprows = 1, delimiter = '\t', unpack = True, usecols = (0,1))
    
    # filename = '/mnt/hgfs/VMShared/Data/QE_LSST/diode_data/sensitivity.txt'
    # ts, ys = np.loadtxt(filename, skiprows = 1, delimiter = '\t', unpack = True, usecols = (0,4))
    

    # tlist = []
    # ylist = []
    #
    # for i in range(len(ts)):
    # tlist.append(ts[i])
    # ylist.append(ys[i])
    #
    # c1 = TCanvas( '1', '1', CANVAS_WIDTH,CANVAS_HEIGHT)
    # graph = TGraph(int(len(ts)), np.asarray(tlist, dtype = 'f8'), np.asarray(ylist, dtype = 'f8'))
    # graph.SetMarkerStyle(2)
    # fitfunc = TF1("","[0] + [1] *x +[2] *x ^ 2 +[3] *x ^ 3 +[4] *x ^ 4 +[5] *x ^ 5")# +[6] *x ^ 6 +[7] *x ^ 7 +[8] *x ^ 8 +[9] *x ^ 9 +[10] *x ^ 10 +[11] *x ^ 11 +[12] *x ^ 12 +[13] *x ^ 13 +[14] *x ^ 14 +[15] *x ^ 15 +[16] *x ^ 16 +[17] *x ^ 17 +[18] *x ^ 18 +[19] *x ^ 19 +[20] *x ^ 20 +[21] *x ^ 21 +[22] *x ^ 22 +[23] *x ^ 23 +[24] *x ^ 24 +[25] *x ^ 25 +[26] *x ^ 26 +[27] *x ^ 27 +[28] *x ^ 28 +[29] *x ^ 29 +[30] *x ^ 30 +[31] *x ^ 31 +[32] *x ^ 32 +[33] *x ^ 33 +[34] *x ^ 34 +[35] *x ^ 35 +[36] *x ^ 36 +[37] *x ^ 37 +[38] *x ^ 38 +[39] *x ^ 39 +[40] *x ^ 40 +[41] *x ^ 41 +[42] *x ^ 42 +[43] *x ^ 43 +[44] *x ^ 44 +[45] *x ^ 45 +[46] *x ^ 46 +[47] *x ^ 47 +[48] *x ^ 48 +[49] *x ^ 49")
    # # for i in range(20):
    # # fitfunc.SetParameter(i,(-1.**(i+1)) * float(np.random.randint(-1,1)))
    #
    # graph.Fit(fitfunc,"M")
    # graph.Draw("AP")
    # c1.SaveAs('/mnt/hgfs/VMShared/output/QE_LSST/diode_data/test.pdf')
    
    
    
#     wavelengths = [320,325,330,335,340,345,350,355,360,365,370,375,380,385,390,395,400,405,410,415,420,425,430,435,440,445,450,465,480,495,510,525,540,555,570,585,600,615,630,645,660,675,690,705,720,735,750,765,780,795,810,825,840,855,870,885,900,915,930,945,950,955,960,965,970,975,980,985,990,995,1000,1005,1010,1015,1020,1025,1030,1035,1040,1045,1050,1055,1060,1065,1070,1075,1080]
    wavelengths = [200,205,210,215,220,225,230,235,240,245,250,255,260,265,270,275,280,285,290,295,300,305,310,315,320,325,330,335,340,345,350,355,360,365,370,375,380,385,390,395,400,405,410,415,420,425,430,435,440,445,450,455,460,465,470,475,480,485,490,495,500,505,510,515,520,525,530,535,540,545,550,555,560,565,570,575,580,585,590,595,600,605,610,615,620,625,630,635,640,645,650,655,660,665,670,675,680,685,690,695,700,705,720,725,730,735,740,745,750,755,760,765,770,775,780,785,790,795,800,805,810,815,820,825,830,835,840,845,850,855,860,865,870,875,880,885,890,895,900,905,910,915,920,925,930,935,940,945,950,955,960,965,970,975,980,985,990,995,1000,1005,1010,1015,1020,1025,1030,1035,1040,1045,1050,1055,1060,1065,1070,1075,1080,1085,1090,1095,1100,1105,1110,1115,1120,1125,1130,1135,1140,1145,1150,1155,1160,1165,1170,1175,1180,1185,1190,1195]
    
    from scipy.interpolate import interp1d
    # interp1 = interp1d(ts, ys)
    interp2 = interp1d(ts, ys, kind='cubic')
    
    t_new = np.linspace(min(ts), max(ts), len(ts)*20)
    # pl.plot(ts,ys,'o',wavelengths,interp2(wavelengths),'-')
    pl.plot(ts,ys,'o',t_new,interp2(t_new),'-')

    pl.show()
    
    
    for w in wavelengths:
        print str(w) + '\t' + str(interp2(w))
    
    
    print '\n***End code***'
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
