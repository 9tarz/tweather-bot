import numpy as np

A = 17.271
B = 237.7 # degC

def dewpoint_approximation(T,RH):
  Td = (B * gamma(T,RH)) / (A - gamma(T,RH))
  return Td

def gamma(T,RH):
  g = (A * T / (B + T)) + np.log(RH/100.0)
  return g
 