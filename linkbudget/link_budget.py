from flow.node import Node, Ptype
import random
import math

c = 299792458.0 # speed of light in m/s
k = 1.38064852*1e-23 # Boltzmann constant
wavelength = lambda f: c/f


Ptype.CWSIG = '#FFD500' # define port type for cw signal


class CWSig:
	'''
	Datatype for port type CWSIG (continous wave signal)
	'''
	def __init__(self, freqMHz, powDBm):
		self.freqMHz = freqMHz
		self.powDBm = powDBm
	
	def __repr__(self):
		return 'CWSig(freqMHz={}, powDBm={})'.format(self.freqMHz, self.powDBm)
	
	def __str__(self):
		return '<{} MHz, {} dBm>'.format(self.freqMHz, self.powDBm)


class CWSignal(Node):
	'''
	Node for creating a cw signal
	'''
	def __init__(self):
		Node.__init__(self, 'CW signal')
		self.addInput('freqMHz', 1000.)
		self.addInput('powDBm', 0.)
		self.addOutput('cwSignal', Ptype.CWSIG)
	
	def process(self, freqMHz, powDBm):
		self.output['cwSignal'].push(CWSig(freqMHz, powDBm))


class CWSignalFreq(Node):
	'''
	Extracts the frequency from a cw signal
	'''
	def __init__(self):
		Node.__init__(self, 'CW signal frequency')
		self.addInput('cwSignal', ptype=Ptype.CWSIG)
		self.addOutput('freqMHz', Ptype.FLOAT)
	
	def process(self, cwSignal):
		self.output['freqMHz'].push(cwSignal.freqMHz)


class CWSignalPow(Node):
	'''
	Extracts the power from a cw signal
	'''
	def __init__(self):
		Node.__init__(self, 'CW signal power')
		self.addInput('cwSignal', ptype=Ptype.CWSIG)
		self.addOutput('powDBm', Ptype.FLOAT)
	
	def process(self, cwSignal):
		self.output['powDBm'].push(cwSignal.powDBm)


class Wavelength(Node):
	'''
	Wavelength for a given frequency
	'''
	def __init__(self):
		Node.__init__(self, 'Wavelength')
		self.addInput('freqMHz', 1000.)
		self.addOutput('wavelengthM', Ptype.FLOAT)
	
	def process(self, freqMHz):
		self.output['wavelengthM'].push(wavelength(freqMHz*1e6))


class WattToDBm(Node):
	'''
	Linear power in Watt to Milliwatt-decibel
	'''
	def __init__(self):
		Node.__init__(self, 'Watt to dBm')
		self.addInput('watt', 0.001)
		self.addOutput('dBm', Ptype.FLOAT)
	
	def process(self, watt):
		self.output['dBm'].push(10*math.log10(1e3*watt))


class DBmToWatt(Node):
	'''
	Milliwatt-Decibel to linear power in Watt
	'''
	def __init__(self):
		Node.__init__(self, 'dBm to Watt')
		self.addInput('dBm', 0.)
		self.addOutput('watt', Ptype.FLOAT)
	
	def process(self, dBm):
		self.output['watt'].push(1e-3*math.pow(10, dBm/10.))


class ERPToEIRP(Node):
	'''
	Effective radiated power to effective isotropic radiated power
	'''
	def __init__(self):
		Node.__init__(self, 'ERP to EIRP')
		self.addInput('erpDBm', 0.)
		self.addOutput('eirpDBm', Ptype.FLOAT)
	
	def process(self, erpDBm):
		self.output['eirpDBm'].push(erpDBm+2.15)


class EIRPToERP(Node):
	'''
	Effective isotropic radiated power to effective radiated power
	'''
	def __init__(self):
		Node.__init__(self, 'EIRP to ERP')
		self.addInput('eirpDBm', 0.)
		self.addOutput('erpDBm', Ptype.FLOAT)
	
	def process(self, eirpDBm):
		self.output['erpDBm'].push(eirpDBm-2.15)


class Amplifier(Node):
	'''
	Amplifies a signal
	'''
	def __init__(self):
		Node.__init__(self, 'Amplifier')
		self.addInput('cwSignal', ptype=Ptype.CWSIG)
		self.addInput('ampDB', 10.)
		self.addOutput('cwSignal', Ptype.CWSIG)
	
	def process(self, cwSignal, ampDB):
		cwSignal.powDBm += ampDB
		self.output['cwSignal'].push(cwSignal)


class Attenuator(Node):
	'''
	Attenuates a signal
	'''
	def __init__(self):
		Node.__init__(self, 'Attenuator')
		self.addInput('cwSignal', ptype=Ptype.CWSIG)
		self.addInput('attnDB', 10.)
		self.addOutput('cwSignal', Ptype.CWSIG)
	
	def process(self, cwSignal, attnDB):
		cwSignal.powDBm -= attnDB
		self.output['cwSignal'].push(cwSignal)


class FreespaceLoss(Node):
	'''
	Attenuates a signal with frequency over a distance in free space
	'''
	def __init__(self):
		Node.__init__(self, 'Freespace loss')
		self.addInput('cwSignal', ptype=Ptype.CWSIG)
		self.addInput('distanceM', 1.)
		self.addOutput('cwSignal', Ptype.CWSIG)
	
	def process(self, cwSignal, distanceM):
		fsplLin = (4*math.pi*distanceM/wavelength(cwSignal.freqMHz*1e6))**2
		fsplDB = 10*math.log10(fsplLin) # linear attenuation to dB
		cwSignal.powDBm -= fsplDB # attenuate signal
		self.output['cwSignal'].push(cwSignal)


class FreespaceDist(Node):
	'''
	Freespace distance for a given attenuation at a frequency
	'''
	def __init__(self):
		Node.__init__(self, 'Freespace distance')
		self.addInput('lossDB', 0.)
		self.addInput('freqMHz', 1000.)
		self.addOutput('distanceM', Ptype.FLOAT)
	
	def process(self, lossDB, freqMHz):
		lossLin = math.pow(10, abs(lossDB)/10.)
		dist = wavelength(freqMHz*1e6)*math.sqrt(lossLin)/(4*math.pi)
		self.output['distanceM'].push(dist)


class RLToML(Node):
	'''
	Return loss to mismatch loss converter
	'''
	def __init__(self):
		Node.__init__(self, 'Mismatch loss')
		self.addInput('returnLossDB', 10.)
		self.addOutput('mismatchLossDB', Ptype.FLOAT)
	
	def process(self, returnLossDB):
		refl = 10**(-abs(returnLossDB)/20.)
		ml = -10*math.log10(1-refl**2)
		self.output['mismatchLossDB'].push(ml)


class FarfieldBNetzA(Node):
	'''
	Far field distance for a given frequency 
	based on the definition of the Bundesnetzagentur
	'''
	def __init__(self):
		Node.__init__(self, 'Farfield BNetzA')
		self.addInput('freqMHz', 1000.)
		self.addOutput('farfieldM', Ptype.FLOAT)
	
	def process(self, freqMHz):
		self.output['farfieldM'].push(4*wavelength(freqMHz*1e6))


class FarfieldAperture(Node):
	'''
	Far field distance for a given frequency and aperture
	'''
	def __init__(self):
		Node.__init__(self, 'Farfield region')
		self.addInput('freqMHz', 1000.)
		self.addInput('apertureM', 0.2)
		self.ffOut = self.addOutput('farfieldM', Ptype.FLOAT)
		self.antOut = self.addOutput('longAnt', Ptype.BOOL)
	
	def process(self, freqMHz, apertureM):
		l = wavelength(freqMHz*1e6)
		if apertureM > l:
			# long antenna
			self.ffOut.push(2*apertureM**2/l)
			self.antOut.push(True)
		else:
			# short antenna
			self.ffOut.push(2*l)
			self.antOut.push(False)


class NearfieldRegion(Node):
	'''
	Reactive nearfield region for a given frequency and aperture
	'''
	def __init__(self):
		Node.__init__(self, 'Nearfield region')
		self.addInput('freqMHz', 1000.)
		self.addInput('apertureM', 0.2)
		self.nfOut = self.addOutput('nearfieldM', Ptype.FLOAT)
	
	def process(self, freqMHz, apertureM):
		l = wavelength(freqMHz*1e6)
		self.nfOut.push(0.62*math.sqrt(apertureM**3/l))


class Noisefloor(Node):
	'''
	Noisefloor in dBm
	'''
	def __init__(self):
		Node.__init__(self, 'Noisefloor')
		self.addInput('tempCelsius', 16.85)
		self.addInput('bwMHz', 20.)
		self.dBmOut = self.addOutput('noiseDBm', Ptype.FLOAT)
	
	def process(self, tempCelsius, bwMHz):
		tempKelvin = tempCelsius+273.15
		bwHz = bwMHz*1e6
		powWatt = k*tempKelvin*bwHz
		self.dBmOut.push(10*math.log10(1e3*powWatt))