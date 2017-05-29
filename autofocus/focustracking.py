"""
Tracking algorithm to keep the tip in focus during a move
Use the template matching method to focus
"""

from focus_template_series import *
from template_matching import *
from get_img import *
import cv2


__all__ = ['focus_track']


def focus_track(devtype, microscope, arm, template, step, axis, alpha, um_px, estim=(0., 0., 0.), cap=None):
    """
    Focus after a move of the arm
    """

    pos = microscope.position(2)

    # Update frame just in case
    frame = getImg(devtype, microscope, cv2cap=cap, update=1)

    # Get initial location of the tip
    _, _, initloc = templatematching(frame, template[len(template)/2])

    # Move the arm
    arm.relative_move(step, axis)
    cv2.waitKey(1000)
    frame = getImg(devtype, microscope, cv2cap=cap, update=1)
    cv2.imshow('Camera', frame)
    cv2.waitKey(1)

    # Move the platform to center the tip
    for i in range(2):
        microscope.relative_move(alpha[i]*estim[i]*step, i)
        cv2.waitKey(1000)

    # Update the frame.
    frame = getImg(devtype, microscope, cv2cap=cap, update=1)
    cv2.imshow('Camera', frame)
    cv2.waitKey(1)

    # Move the microscope
    frame = getImg(devtype, microscope, pos + estim[2] * step, cv2cap=cap)
    cv2.imshow('Camera', frame)
    cv2.waitKey(5)

    # Focus around the estimated focus height
    _, estim_temp, loc, frame = focus(devtype, microscope, template, cap)

    # Move the platform for compensation
    for i in range(2):
        microscope.relative_move(alpha[i]*(loc[i] - initloc[i])*um_px, i)

    cv2.waitKey(1000)

    #Update frame
    frame = getImg(devtype, microscope, cv2cap=cap, update=1)
    cv2.imshow('Camera', frame)
    cv2.waitKey(1)

    # Update the estimated move to do for a move of 1 um of the arm
    estim[2] += float(estim_temp)/float(step)
    for i in range(2):
        estim[i] += (loc[i]-initloc[i])*um_px/float(step)

    return estim, frame
