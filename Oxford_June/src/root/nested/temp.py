from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib.animation as animation
import matplotlib.image as mpimg
import gc
gc.collect()


# plt.ion()

ims = []

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
X, Y, Z = axes3d.get_test_data(0.1)
# ax.plot_wireframe(X, Y, Z, rstride=5, cstride=5)
ax.scatter(X, Y, Z)
 
for angle in range(0, 360):
    print angle
    ax.view_init(30, angle)
    image = fig.savefig('/mnt/hgfs/VMShared/temp/animation/' + str(angle) + '.png')


# 
# fig = plt.figure()
# 
#     
# for filename in os.listdir('/mnt/hgfs/VMShared/temp/animation/'):
#     image = mpimg.imread('/mnt/hgfs/VMShared/temp/animation/' + filename)
#     ims.append(image)
#     
#     
# ani = animation.ArtistAnimation(fig, ims, interval=50, blit=True, repeat_delay=1000)
#      
     
# plt.show()

    
print 'done'