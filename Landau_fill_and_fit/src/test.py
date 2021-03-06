from ROOT import TCanvas, TH1F, gROOT
import numpy as np

if __name__ == '__main__':
    gROOT.SetBatch(1) #don't draw along the way
    
    filename = '/home/user01/Desktop/example_files/landau.txt'
    data = np.loadtxt(filename, dtype = float)
       
    histmin = -100
    histmax = 1500
    nbins = 160
        
    c1 = TCanvas( 'canvas', 'canvas', 1200, 800) #create canvas
    landau_hist = TH1F('dE/dx', 'dE/dx',nbins,histmin,histmax)
    for value in data:
        landau_hist.Fill(value)
    landau_hist.Draw()
    landau_hist.GetXaxis().SetTitle('Pulse height (a.u.)')
    landau_hist.GetYaxis().SetTitle('Frequency')
    
    landau_hist.Fit('landau', '', '', 200, 1400)
    
    c1.SaveAs('/home/user01/Desktop/example_outputs/landau.pdf')
    c1.SaveAs('/home/user01/Desktop/example_outputs/landau_hist.png')
    
    print '\n***ROOT example complete***'







