import pyfits
import sys
import matplotlib.pyplot as plt
import numpy
from numpy import sqrt, linspace, zeros
from mpl_toolkits.mplot3d import axes3d
import matplotlib.animation as animation

from ROOT import *
from array import array
# gROOT.SetBatch(1) #don't show drawing on the screen along the way


filename = '/mnt/hgfs/VMShared/temp/opencluster.fits'
output_path = '/mnt/hgfs/VMShared/temp/animation/'
name = 'phi'

def main():
    global filename, output_path, name
    
#     MyPalette = numpy.ndarray(1000, dtype = numpy.int32)
#     r = array('d',[0., 0.0, 1.0, 1.0, 1.0])
#     g = array('d',[0., 0.0, 0.0, 1.0, 1.0])
#     b = array('d',[0., 1.0, 0.0, 0.0, 1.0])
#     stop = array('d',[0., .25, .50, .75, 1.0])
#     FI = TColor.CreateGradientColorTable(5, stop, r, g, b, 100)
# #     for (int i=0;i<100;i++) MyPalette[i] = FI+i;
#     for i in xrange(100):
#         MyPalette[i] = FI+i
#     gStyle.SetPalette(1000, MyPalette);
# #     gROOT.GetColor(26)
    
    
    x, h = pyfits.getdata(filename, header=True)
    box=h['box']
    x /= 3.085e16
    box /= 3.085e16

    c = TCanvas( 'SC_ex', 'SC_ex', 1200, 1200) #create canvas
    gPad.SetFillColor(1)

    rng=[0.0, box]
    rng[0] = 0.01
    rng[1] = 23.99
    
    ntot = x.shape[0]
    for i in xrange(ntot):
        w, = numpy.where((x[i,:,0]>rng[0]) & (x[i,:,0]<rng[1])
                  & (x[i,:,1]>rng[0]) & (x[i,:,1]<rng[1])
                  & (x[i,:,2]>rng[0]) & (x[i,:,2]<rng[1]))
                  
        xlist = array('d', x[i,w,0])
        ylist = array('d', x[i,w,1])
        zlist = array('d', x[i,w,2])
        
#         xlist = array('d', x[i,:,0])
#         ylist = array('d', x[i,:,1])
#         zlist = array('d', x[i,:,2])
        
        #box corners for hacking axis ranges
        xlist += array('d',[rng[0],rng[0],rng[0],rng[0],rng[1],rng[1],rng[1],rng[1]])
        ylist += array('d',[rng[0],rng[0],rng[1],rng[1],rng[1],rng[1],rng[0],rng[0]])
        zlist += array('d',[rng[0],rng[1],rng[0],rng[1],rng[0],rng[1],rng[0],rng[1]])
        
        npts = len(xlist)
        print "npts = " + str(npts)
        plot = TGraph2D(npts, xlist, ylist, zlist)
        plot.SetTitle("")
        plot.SetMarkerColor(0)
        plot.SetMarkerStyle(8)
        plot.SetMarkerSize(1)
        
        tagged_points = [1,2,3,4]
        graph_list = []
        for pointnum in tagged_points:
            x_point,y_point, z_point =  array('d'),array('d'),array('d')
            x_point.append(xlist[pointnum])
            y_point.append(ylist[pointnum])
            z_point.append(zlist[pointnum])
            graph = TGraph2D(1, x_point, y_point, z_point)
            graph.SetTitle("")
#             this_color = gROOT.GetColor(26);
            graph.SetMarkerColor(2)
            graph.SetMarkerStyle(8)
            graph.SetMarkerSize(1)
            graph_list.append(graph)
            
        
        plot.GetXaxis().SetAxisColor(0)
        plot.GetYaxis().SetAxisColor(0)
        plot.GetZaxis().SetAxisColor(1)
        
#         plot.GetXaxis().SetLimits(rng[0],rng[1]) 
#         plot.GetYaxis().SetLimits(rng[0],rng[1]) 
#         plot.GetZaxis().SetLimits(rng[0],rng[1])
        
        
        c.SetGrid(False)
        
        plot.Draw("P,fb,bb*")
        for graph in graph_list:
            graph.GetXaxis().SetRangeUser(rng[0],rng[1])
            graph.GetYaxis().SetRangeUser(rng[0],rng[1])
            graph.GetZaxis().SetRangeUser(rng[0],rng[1])
            graph.Draw("APsame,fb,bb")
            
#         plot.GetXaxis().SetRange(rng[0],rng[1])
#         plot.GetYaxis().SetRange(rng[0],rng[1])
#         plot.GetZaxis().SetRange(rng[0],rng[1])
        

        
        c.RedrawAxis()
        
        
#         c.SetTheta(i)
        c.SetPhi(i)
        
 
        


        out_name = output_path + '%s-%06d' % (name, i)
        gifname = output_path + name
        print '%d/%d %s' % (i+1,ntot,filename)
        c.SaveAs(out_name + '.png')
#         c.SaveAs(gifname + '.gif+10')
#         if i>10: exit()
            

#     ani = animation.ArtistAnimation(fig, plots, interval = 50, blit = True, repeat_delay = 1000)
#     plt.show()
#     ani.save('test1000.mp4', writer='ffmpeg')
    
    
main()
