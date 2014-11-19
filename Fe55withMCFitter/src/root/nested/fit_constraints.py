class ExamplePrior(object):
    def __init__(self, log10Flux_range, log10T_range):
        self.log10Flux_range=log10Flux_range
        self.log10T_range=log10T_range

    def get_lnprob_scalar(self, pars):
        lnp=0.0
        logT=pars[4]
        if (logT < self.log10Flux_range[0]
                or logT > self.log10Flux_range[1]):
            lnp += -9.99e40
            #raise GMixRangeError("T is out of bounds")

        logFlux=pars[5]
        if (logFlux < self.log10Flux_range[0]
                or logFlux > self.log10Flux_range[1]):
            lnp += -9.99e40
            #raise GMixRangeError("flux is out of bounds")
        return lnp
    
    def fill_fdiff(self, pars, fdiff):
        from ngmix import GMixRangeError

        fdiff[0:4]=0.0
        logT=pars[4]
        if (logT < self.log10Flux_range[0]
                or logT > self.log10Flux_range[1]):
            fdiff[4] = -9.99e40
            #raise GMixRangeError("T is out of bounds")

        logFlux=pars[5]
        if (logFlux < self.log10Flux_range[0]
                or logFlux > self.log10Flux_range[1]):
            fdiff[5] = -9.99e40
            #raise GMixRangeError("flux is out of bounds")

        return 4
    
    
    
