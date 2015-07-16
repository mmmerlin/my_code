from ROOT import TGraph2D,TCanvas,TH2F
from decamutil import decaminfo
import ROOT
from ROOT import gStyle

import numpy as np
decam = decaminfo()

ns = np.genfromtxt('/mnt/hgfs/VMShared/output/DES_analysis/results.txt', delimiter='\t',dtype = 'str', skiprows=1, usecols = [7], unpack = True)#, dtype, comments, delimiter, converters, skiprows, usecols, unpack, ndmin)
ns_num, sigma, grad = np.genfromtxt('/mnt/hgfs/VMShared/output/DES_analysis/results.txt', delimiter='\t', skiprows=1, usecols = [8,12,14], unpack = True)#, dtype, comments, delimiter, converters, skiprows, usecols, unpack, ndmin)

names = []

for i, name in enumerate(ns):
    names.append(name + str(int(ns_num[i])))
del ns

grad*= 100

c1 = TCanvas( 'canvas', 'canvas', 1200, 1200)

graph = TGraph2D()
# dummy = TH2F('hist','hist',100,-186,186,100,-192,192)
# #dummy.SetPoint(0,-185.9805,-191.6625, 3.8)
# #dummy.SetPoint(1, 185.9955, 191.6775, 4.5)
# #dummy.SetPoint(2, 185.9955, 191.6775, 100)
# #dummy.SetPoint(3, 185.9955, 191.6775, -100)
# for i in range(10):
# 	dummy.Fill(0,0,1)
# #dummy.GetZaxis().SetRangeUser(3.8,4.2)
# 
# dummy.Draw('colz')

xs, ys = [], []
for i in range(len(names)):
    x,y = decam.getPosition(names[i], 1024, 2048)
    print x, y
    xs.append(x)
    ys.append(y)
    graph.SetPoint(i,x,y,sigma[i])
#     graph.SetPoint(i,x,y,grad[i])
  
# graph = TH2F('hist','hist',)
# for i in range(len(names)):
#     x,y = decam.getPosition(names[i], 1024, 2048)
#     print i
#     graph.Fill(x,y,sigma[i])
  
  
# graph.GetZaxis().SetRangeUser(3.878711492, 4.425647785)
# graph.GetZaxis().SetRangeUser(4, 4.2)
# graph.SetMarkerStyle(20)
# graph.SetMarkerSize(2)
# hist = TH2F('hist','hist',7,min(xs),max(xs),12,min(ys),max(ys))


hist = TH2F('hist','hist',12,min(xs),max(xs),7,min(ys),max(ys))
# hist.GetZaxis().SetRangeUser(min(grad), max(grad))
hist.GetZaxis().SetRangeUser(min(sigma), max(sigma))
# hist.GetZaxis().SetRangeUser(3.878711492, 4.425647785)
graph.SetHistogram(hist)

graph.SetTitle('')
gStyle.SetOptStat(0)


graph.Draw('colz')
c1.SaveAs('/mnt/hgfs/VMShared/output/DES_analysis/focal_plane_sigma.png')
# c1.SaveAs('/mnt/hgfs/VMShared/output/DES_analysis/focal_plane_grad.png')

print "finished"
