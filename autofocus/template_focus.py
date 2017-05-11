"""
Autofocusing on the tip using template matching
First user must put the tip on focus to get the template
Template matching is not scale nor rotation invariant
"""

__all__ = ['focus']

from Hamamatsu_camera import *
from template_matching import *
from get_img import *
import cv2
from scipy.optimize import minimize_scalar, minimize
from math import fabs

def focus(devtype, microscope, template, cv2cap=None, step = 0):
    """
    Autofocus by searching the best template match in the image around the current height
    :param devtype: type of used controller
    :param microscope: device controlling the microscope
    :param template: template image to look for
    :param cv2cap: video capture from cv2, unnecessary if devtype='SM5' 
    :param step: step length made if the arm is moving (for quicker tracking)
    """

    # Getting the microscope height according to the used controller
    if devtype == 'SM5':
        current_z = microscope.getPosition()
    elif devtype== 'SM10':
        current_z = microscope.position(2)
    else:
        raise TypeError('Unknown device. Should be either "SM5" or "SM10".')

    # Tabs of maxval and their locations during the process
    vals = []
    location = []

    # Getting the maxval and their locations at +-4um, 1um steps, around the current height
    for i in range(9):
        if step <= 0:
            _, img = getImg(devtype, microscope, current_z - i + 4, cv2cap)
        else:
            _, img = getImg(devtype, microscope, current_z + i - 4, cv2cap)
        res, val, loc = templatematching(img, template)
        location += [loc]
        if res:
            # Template has been detected
            vals += [val]
        else:
            # Template has not been detected, maxval set at 0
            vals += [0]

        if val > 0.95:
            maxval = val
            x, y = loc[:2]
            return maxval



    # Search of the highest value, indicating that focus has been achieved
    maxval = max(vals)

    if maxval != 0:
        # Template has been detected at least once, setting the microscope at corresponding height
        index = vals.index(maxval)
        locate = location[index]
        _, img = getImg(devtype, microscope, current_z - index + 4, cv2cap)
        x, y = locate[:2]
    else:
        # Template has never been detected, focus can not be achieved
        raise ValueError('The template image has not been detected.')

    return maxval