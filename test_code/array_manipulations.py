import numpy as np

a = np.array([[8,15,40],[22,7,14],[17,10,24]])
print("a: Travel time matrix\n", a)

b = np.where(a<=30,1,0)
print("\nb: 30 minute travel time flags\n", b)

e = np.array([100,200,300])
print("\ne: employment\n", e)

c = b * e
print("\nc: 30 minute employment\n", c)

d = np.sum(c,0)
print("\nd: 30 minute employment rowsums\n", d)

z = np.array([1,2,3])
print("\nz: Zone numbers\n", z)

emp = np.array([z,d])
print("\nemp: Employment by zone\n", emp)

emp2 = emp.T
print("\nemp2: Employment by zone (transposed)\n", emp2)

np.savetxt('test.csv', emp2, delimiter=',', fmt='%i', header="taz,Tot_Emp", comments="")
