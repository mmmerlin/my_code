import numpy as np

import ROOT
from ROOT import TCanvas, TF1, TH1F


import root_functions
from root_functions import LanGausFit, LandauFit

if __name__ == '__main__':
    
    filename = "/home/user01/Desktop/example_files/landau.txt"
    data = np.loadtxt(filename, dtype = float)
       
    histmin = 0
    histmax = 1500
    nbins = 100

    c1 = TCanvas( 'canvas', 'canvas', 500, 200, 700, 500 ) #create canvas
    landau_hist = TH1F('dE/dx', 'dE/dx',nbins,histmin,histmax)
    for value in data:
        landau_hist.Fill(value)
    landau_hist.Draw()
    landau_hist.GetXaxis().SetTitle('Pulse height (a.u.)')
    landau_hist.GetYaxis().SetTitle('Frequency')
    
    
    langaus_func, dummy = LanGausFit(landau_hist, 200,1000)# returns a TF1
    langaus_func.SetNpx(1000)
    langaus_func.Draw("same")
#    
    landau_func = LandauFit(landau_hist, 200,1000, True) #bool supresses the drawing during the fit
    landau_func.SetNpx(1000)
    landau_func.SetLineStyle(5)
    landau_func.SetLineColor(4)
    landau_func.SetLineWidth(5)
    landau_func.Draw("same")
    
    
    c1.SaveAs('/home/user01/Desktop/example_files/test_landau.pdf')
    del c1
    del landau_hist
    
    
    print '\n***End code***'







