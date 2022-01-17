from flow.node import Node, Ptype

def cableAttn(freqMHz, cableLenM, a, b):
	'''
	Cable attenuation per meter at frequency.
	:param freqMHz: frequency in MHz
	:param cableLenM: cable length in m
	:param a, b: coefficients
	'''
	freqGHz = freqMHz/1000.
	return cableLenM*(a*(freqGHz**0.5) + b*freqGHz)


class CableAttn(Node):
	'''
	Abstract class for cable attenuation per meter at frequency
	'''
	def __init__(self, name):
		Node.__init__(self, name)
		self.addInput('cwSignal', ptype=Ptype.CWSIG)
		self.addInput('cableLenM', 1.)
		self.addOutput('cwSignal', Ptype.CWSIG)
		self.a = 1.
		self.b = 1.
	
	def process(self, cwSignal, cableLenM):
		attnDB = cableAttn(cwSignal.freqMHz, cableLenM, self.a, self.b)
		cwSignal.powDBm -= attnDB
		self.output['cwSignal'].push(cwSignal)


class CustomCable(CableAttn):
	'''
	User can set a and b coefficients
	'''
	def __init__(self):
		CableAttn.__init__(self, 'Custom cable')
		self.addInput('a', 0.1)
		self.addInput('b', 0.01)
	
	def process(self, cwSignal, cableLenM, a, b):
		attnDB = cableAttn(cwSignal.freqMHz, cableLenM, a, b)
		cwSignal.powDBm -= attnDB
		self.output['cwSignal'].push(cwSignal)


class SUCOFORM141(CableAttn):
	def __init__(self):
		CableAttn.__init__(self, 'H+S Sucoform 141')
		self.a = 0.355
		self.b = 0.04


class SUCOFORM86(CableAttn):
	def __init__(self):
		CableAttn.__init__(self, 'H+S Sucoform 86')
		self.a = 0.6283
		self.b = 0.04


class G03232D01(CableAttn):
	def __init__(self):
		CableAttn.__init__(self, 'H+S G 03232 D-01')
		self.a = 0.431
		self.b = 0.135


class EZ118TP(CableAttn):
	def __init__(self):
		CableAttn.__init__(self, 'H+S EZ 118 TP')
		self.a = 0.3804
		self.b = 0.00791


class EZ141TPM17(CableAttn):
	def __init__(self):
		CableAttn.__init__(self, 'H+S EZ 141 TP M17')
		self.a = 0.32544
		self.b = 0.03967


class SX04172B60(CableAttn):
	def __init__(self):
		CableAttn.__init__(self, 'H+S SX 04172 B-60')
		self.a = 0.233
		self.b = 0.0575

class LCF1450J(CableAttn):
	def __init__(self):
		CableAttn.__init__(self, 'LCF14-50J')
		self.a = 0.13
		self.b = 0.0092


class LCF1250J(CableAttn):
	def __init__(self):
		CableAttn.__init__(self, 'LCF12-50J')
		self.a = 0.067
		self.b = 0.00549


class LCF7850JAA0(CableAttn):
	def __init__(self):
		CableAttn.__init__(self, 'LCF78-50JA-A0')
		self.a = 0.035
		self.b = 0.003


class Ecoflex10(CableAttn):
	def __init__(self):
		CableAttn.__init__(self, 'Ecoflex10')
		self.a = 0.123
		self.b = 0.019


class Ecoflex10Plus(CableAttn):
	def __init__(self):
		CableAttn.__init__(self, 'Ecoflex10-Plus')
		self.a = 0.127
		self.b = 0.013


class H155(CableAttn):
	def __init__(self):
		CableAttn.__init__(self, 'H155')
		self.a = 0.285
		self.b = 0.024


class Aircell5(CableAttn):
	def __init__(self):
		CableAttn.__init__(self, 'Aircell5')
		self.a = 0.291
		self.b = 0.02