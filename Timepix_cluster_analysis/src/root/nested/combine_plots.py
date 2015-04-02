from ROOT import TCanvas, TH1F, TFile, TLegend
import ROOT
from ROOT import *


gROOT.SetBatch(1) #don't show drawing on the screen along the way
gStyle.SetOptStat(11111111111111111)


if __name__ == '__main__':

    outpath = '/mnt/hgfs/VMShared/output/new_sensor_profiling/'
    path = '/mnt/hgfs/VMShared/output/new_sensor_profiling/'
    ID_list = []
    ID_list.append('A1_run1')
    ID_list.append('A2_run1')
    
    key_list = []
    key_list.append('cluster_size')
    key_list.append('pixels_per_frame')
    key_list.append('ions_per_frame')
    
    object_list = {}
    
    
    for ID in ID_list:
        rootfile = TFile.Open(path + ID + '.root', "READ")
    
        for i, key in enumerate(key_list):
            temp = rootfile.Get(key)
            if repr(temp) != '<ROOT.TObject object at 0x(nil)>':
                object_list[ID + key] = temp
            else:
                print "Error opening %s from %s"%(key, ID)
            
            
            
    c1 = TCanvas( 'canvas', 'canvas', 1200, 800)
    legend_text = []
    legend = TLegend(0.59,0.70,0.89,0.87) #position the legend at top left
    
    for i, ID in enumerate(ID_list):
        object_list[ID + 'cluster_size'].SetLineColor(i+1)
        object_list[ID + 'cluster_size'].Draw("same")
        legend_text.append(ID + 'cluster_size')
        legend.AddEntry(object_list[ID + 'cluster_size'], ID)

    legend.Draw('same')
        
#     legend_text.append('grad = ' + str(round(a,4)) + ' #pm ' + str(round(a_error,4)))
#     legend_text.append('intercept = ' + str(round(y_int,2)) + ' #pm ' + str(round(y_int_error,2)))
#     legend_text.append('R^{2} = ' + str(round(R2,3)))
#     textbox = TPaveText(0.5,0.25,0.85,0.5,"NDC")
#     for line in legend_text: textbox.AddText(line)
#     textbox.SetFillColor(0)
#     textbox.SetTextSize(1.4* textbox.GetTextSize())
#     textbox.Draw("same")

    
    c1.SaveAs(outpath + 'aa_combined_hist_test' + '.png')    
    
    
    