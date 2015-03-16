#from matplotlib.pylab import *
import numpy
#import dtcwt
## SI len(face) ==0 on incremente un i si i ==10 alors envoie message erreur sinon on reinitialse i a 0
def ppgFunction(r, g, b, face, frame):
    r[0] = r[1]
    g[0] = g[1]
    b[0] = b[1]
    
    for (x, y, w, h) in face:
        i = x+w/2
        j = y+h/6
        r[1] = frame[j][i][2]
        g[1] = frame[j][i][1]
        b[1] = frame[j][i][0]
            
    print "R : ", r
    print "G : ", g
    print "B : ", b
        
    x1 = [r[1]-g[1], r[0]-g[0]]
    x2 = [r[1]+g[1]-2*b[1], r[0]+g[0]-2*b[0]]

    print "X1 : ", x1
    print "X2 : ", x2
        
    mean_x1 = numpy.mean(x1)
    mean_x2 = numpy.mean(x2)
    v0 = x1[0] - mean_x1
    v1 = x1[1] - mean_x1
    x1 = [v0, v1]
    v0 = x2[0] - mean_x2
    v1 = x2[1] - mean_x2
    x2 = [v0, v1]
        
    print "X1(mean) : ", x1
    print "X2(mean) : ", x2
        
    std_x1 = numpy.std(x1)
    std_x2 = numpy.std(x2)
    v0 = (std_x1/std_x2)*x2[0]
    v1 = (std_x1/std_x2)*x2[1]
    x2 = [v0, v1]
        
    print "X2(std) : ", x2

    v0 = x1[0]-x2[0]
    v1 = x1[1]-x2[1]
    hb = [v0, v1]

    print "HB : ", hb

    std_hb = numpy.std(hb)
    v0 = hb[0]/std_hb
    v1 = hb[1]/std_hb
    hb = [v0, v1]

    print "HB : ", hb

    #figure()
    #plot(hb)
    #title("Input")

    nblevels = 3
    dtcwt_transform = dtcwt.Transform1d()
    hb_dtcwt = dtcwt_transform.forward(hb, nblevels)

    #print "HB(dtcwt) - lowpass(length) : ", len(hb_dtcwt.lowpass)
    print "HB(dtcwt) - lowpass[0] : ", hb_dtcwt.lowpass[0]
    print "HB(dtcwt) - lowpass[1] : ", hb_dtcwt.lowpass[1]
    #print "HB(dtcwt) - highpass(length) : ", len(hb_dtcwt.highpasses)
    print "HB(dtcwt) - highpass[0] : ", hb_dtcwt.highpasses[0]
    #print "HB(dtcwt) - highpass[0]-real : ", hb_dtcwt.highpasses[0][0][0].real
    #print "HB(dtcwt) - highpass[0]-imag : ", hb_dtcwt.highpasses[0][0][0].imag
    print "HB(dtcwt) - highpass[1] : ", hb_dtcwt.highpasses[1]
    #print "HB(dtcwt) - highpass[1]-real : ", hb_dtcwt.highpasses[1][0][0].real
    #print "HB(dtcwt) - highpass[1]-imag : ", hb_dtcwt.highpasses[1][0][0].imag
    print "HB(dtcwt) - highpass[2] : ", hb_dtcwt.highpasses[2]
    #print "HB(dtcwt) - highpass[2]-real : ", hb_dtcwt.highpasses[2][0][0].real
    #print "HB(dtcwt) - highpass[2]-imag : ", hb_dtcwt.highpasses[2][0][0].imag
    
    mean_highpass = numpy.mean(hb_dtcwt.highpasses)
    std_highpass = numpy.std(hb_dtcwt.highpasses)
    t = 1.4*(mean_highpass-0.1*std_highpass)

    print "t = ", t

    v0_r = hb_dtcwt.highpasses[0][0][0].real*hb_dtcwt.highpasses[0][0][0].real
    v0_i = hb_dtcwt.highpasses[0][0][0].imag*hb_dtcwt.highpasses[0][0][0].imag
    v1_r = hb_dtcwt.highpasses[1][0][0].real*hb_dtcwt.highpasses[1][0][0].real
    v1_i = hb_dtcwt.highpasses[1][0][0].imag*hb_dtcwt.highpasses[1][0][0].imag
    v2_r = hb_dtcwt.highpasses[2][0][0].real*hb_dtcwt.highpasses[2][0][0].real
    v2_i = hb_dtcwt.highpasses[2][0][0].imag*hb_dtcwt.highpasses[2][0][0].imag
    x_0 = numpy.sqrt(v0_r+v0_i)
    x_1 = numpy.sqrt(v1_r+v1_i)
    x_2 = numpy.sqrt(v2_r+v2_i)

    print "x_0 = ", x_0
    print "x_1 = ", x_1
    print "x_2 = ", x_2

    #   /!\sgn -> numpy.sign(?)
    if x_0 > t.real:
        v0 = numpy.sign(x_0)*(x_0-t)
    else:
        v0 = 0

    if x_1 > t.real:
        v1 = numpy.sign(x_1)*(x_1-t)
    else:
        v1 = 0

    if x_2 > t.real:
        v2 = numpy.sign(x_2)*(x_2-t)
    else:
        v2 = 0

    hb_dtcwt.highpasses[0][0][0] = v0
    hb_dtcwt.highpasses[1][0][0] = v1
    hb_dtcwt.highpasses[2][0][0] = v2

    print "HB(dtcwt) - lowpass[0] : ", hb_dtcwt.lowpass[0]
    print "HB(dtcwt) - lowpass[1] : ", hb_dtcwt.lowpass[1]
    print "HB(dtcwt) - highpass[0] : ", hb_dtcwt.highpasses[0]
    print "HB(dtcwt) - highpass[1] : ", hb_dtcwt.highpasses[1]
    print "HB(dtcwt) - highpass[2] : ", hb_dtcwt.highpasses[2]

    inv_dtcwt = dtcwt_transform.inverse(hb_dtcwt)

    print "inv_dtcwt : ", inv_dtcwt

    print " ------------------------------------"