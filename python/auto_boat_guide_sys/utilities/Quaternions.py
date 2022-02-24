"""
.. module:: Quaterions.py
    :platform: MacOS, Unix, Windows,
    :synopsis: Quaternions for rotating vectors, and doing attitude estimation. 
    This is based off the excellent book: "Quaternions and Rotation Sequnces: 
    A Primer with Applications to Orbits Aerospace, and Virtual Reality," by 
    Jack B. Kuipers
    Quaternions are treated as 4x1 np.array([[]])'s
.. moduleauthor:: Pavlo Vlastos <pvlastos@ucsc.edu>
"""
import numpy as np


def setQuaternionEulerAngles(psi, theta, phi):
    """
    :param psi: Yaw angle in radians from -pi to pi
    :param theta: Pitch angle in radians
    :param phi: Roll angle in radians
    :return: A quaternion
    """
    cPsi2 = np.cos(psi/2.0)
    cTheta2 = np.cos(theta/2.0)
    cPhi2 = np.cos(phi/2.0)

    sPsi2 = np.sin(psi/2.0)
    sTheta2 = np.sin(theta/2.0)
    sPhi2 = np.sin(phi/2.0)

    q = np.zeros((4, 1))

    q0 = (cPsi2*cTheta2*cPhi2 + sPsi2*sTheta2*sPhi2)
    q1 = (cPsi2*cTheta2*sPhi2 - sPsi2*sTheta2*cPhi2)
    q2 = (cPsi2*sTheta2*cPhi2 + sPsi2*cTheta2*sPhi2)
    q3 = (sPsi2*cTheta2*cPhi2 - cPsi2*sTheta2*sPhi2)

    q[0, 0] = q0
    q[1, 0] = q1
    q[2, 0] = q2
    q[3, 0] = q3

    return q


def getQuaternionComplexConjugate(q):
    """
    :param q: A quaternion
    :return: The complex congjugate of the input quaternion
    """
    qConj = np.zeros((4, 1))

    qConj[0, 0] = q[0, 0]
    qConj[1, 0] = -q[1, 0]
    qConj[2, 0] = -q[2, 0]
    qConj[3, 0] = -q[3, 0]

    return qConj


def multiplyQuaternions(q, p):
    """
    :param q: A quaternion
    :param p: A quaternion
    :return: A quaternion
    """

    p0 = p[0, 0]
    p1 = p[1, 0]
    p2 = p[2, 0]
    p3 = p[3, 0]

    pMat = np.array([[p0, -p1, -p2, -p3],
                     [p1, p0, p3, -p2],
                     [p2, -p3, p0, p1],
                     [p3, p2, -p1, p0]])

    r = np.matmul(pMat, q)

    return r


def rotateVectorWithQuaternion(v, psi=0.0, theta=0.0, phi=0.0):
    """
    :param v: A vector in R^3 as a 3x1 np.array([[]])
    :param psi: Yaw angle in radians from -pi to pi
    :param theta: Pitch angle in radians
    :param phi: Roll angle in radians
    :return: The rotated vector in R^3 as a 3x1 np.array([[]])
    """

    q = setQuaternionEulerAngles(psi, theta, phi)

    vPure = np.zeros((4, 1))

    vPure[1:4, 0] = v[:, 0]

    qConj = getQuaternionComplexConjugate(q)

    p = multiplyQuaternions(qConj, vPure)

    vNew = multiplyQuaternions(p, q)

    return vNew[1:4]


def quaternionToEulerAngles(q):
    """
    See page 167.
    :param q: A quaternion
    :return: Euler angles: phi, theta, psi
    """

    phi = np.arctan2((2.0 * q[2][0] * q[3][0] + 2.0 * q[0][0] * q[1][0]),
                     (2.0 * q[0][0] * q[0][0] + 2.0 * q[3][0] * q[3][0] - 1.0))

    theta = np.arcsin(-(2.0 * q[1][0] * q[3][0] - 2.0 * q[0][0] * q[2][0]))

    psi = np.arctan2((2.0*q[1][0]*q[2][0] + 2.0*q[0][0]*q[3][0]),
                     (2.0*q[0][0]*q[0][0] - 1.0 + 2.0*q[1][0]*q[1][0]))

    return phi, theta, psi

def quaternionToDCM(q):
    """
    See page 168.
    :param q: A quaternion
    :return: R a rotation matrix direction cosine matrix (DCM)
    """

    # q_a = np.copy(q)
    # q[0][0] = q_a[0][0] 
    # q[1][0] = q_a[3][0] #x -> z
    # q[2][0] = q_a[2][0] #y -> y
    # q[3][0] = q_a[1][0] #z -> x

    R = np.zeros((3,3))
    R[0][0] = 2.0 * q[0][0] * q[0][0] - 1.0 + 2.0 * q[1][0] * q[1][0];
    R[0][1] = 2.0 * q[1][0] * q[2][0] + 2.0 * q[0][0] * q[3][0];
    R[0][2] = 2.0 * q[1][0] * q[3][0] - 2.0 * q[0][0] * q[2][0];

    R[1][0] = 2.0 * q[1][0] * q[2][0] - 2.0 * q[0][0] * q[3][0];
    R[1][1] = 2.0 * q[0][0] * q[0][0] - 1.0 + 2.0 * q[2][0] * q[2][0];
    R[1][2] = 2.0 * q[2][0] * q[3][0] + 2.0 * q[0][0] * q[1][0];

    R[2][0] = 2.0 * q[1][0] * q[3][0] + 2.0 * q[0][0] * q[2][0];
    R[2][1] = 2.0 * q[2][0] * q[3][0] - 2.0 * q[0][0] * q[1][0];
    R[2][2] = 2.0 * q[0][0] * q[0][0] - 1.0 + 2.0 * q[3][0] * q[3][0];

    return R