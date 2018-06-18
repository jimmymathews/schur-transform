#!/usr/bin/python3

# x = np.array([ [[4,2],[3,2.1],[4,2.2]] , [[10,7.6],[10.2,7.6],[10.2,7]] , [[5,4],[5.5,4.5],[5.6,4.3]], [[4,4],[5,4.5],[5.1,4.1]]])
# x = np.array([ [[4,2],[3,2.1],[4,2.2]] , [[4,2],[3,2.1],[4,2.2]] , [[4,2],[3,2.1],[4,2.2]], [[4,2],[3,2.1],[4,2.2]]])
# x = np.array([ [[4,2],[4.01,2.1],[3.9,2.2]] , [[3.99,2.1],[3.7,2.1],[4.0,2.2]] , [[4.4,1.9],[4.3,1.8],[4.3,1.8]]])

import numpy as np
from schur_transform import schur_transform

x = np.array([ [[4,2],[4.01,2.1],[3.9,2.2]] , [[3.99,2.1],[3.7,2.1],[4.0,2.2]] , [[4.4,1.9],[4.3,1.8],[4.3,1.8]], [[4.6,2.0],[4.1,1.8],[4.3,1.7]],[[3.6,2.1],[4.5,2],[5,1]],[[3.0,2.2],[7,2.2],[5.6,1.2]]])
[components, amplitudes, characters] = schur_transform(x)
print("Amplitudes:  "+str(amplitudes))
print("Characters:  "+str(characters))
print("Norm of total covariance tensor:  "+str(np.linalg.norm(amplitudes)))
