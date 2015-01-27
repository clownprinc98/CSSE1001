#
# Support for assignment 2
#

# Imports for use in your assignment
from Tkinter import *
import tkMessageBox
from tkColorChooser import askcolor
from math import *


class FunctionError(Exception):
    """A simple function error exception produced by the make_function 
    function for invalid function definitions.
    """
    pass

def make_function(text):
    """Take a string representing a function in x and return the corresponding
    function.

    The FunctionError exception is thrown if text does not represent a valid
    function.

    make_function(string) -> (float -> float)
    """

    try:
        exec 'f = lambda x: ' + text
        1+f(2.0)       ## test to see if there are any errors in the definition
    except ZeroDivisionError:  ## ignore zero division errors
        pass
    except:
        raise FunctionError()
    return f




class FunctionIterator(object):
    """An iterator object that is intended to be used to produce (x,y)
    pairs of a function 

    Constructor: FunctionIterator(function, startx, endx, steps)
    function is the function being iterated over
    startx is the x value to start the iteration
    endx is the x value at the end of the iteration
    steps is the number of iterations.
    Assumes if a division by zero occurs at a given x it won't occur 
    'close to' x

    Example:
    Assume square is a function defined to square a number - i.e. 
    square(x) = x*x
    Then 
    >>> list(FunctionIterator(square, 0.0, 5.0, 5))
    [(0.0, 0.0), (1.0, 1.0), (2.0, 4.0), (3.0, 9.0), (4.0, 16.0), (5.0, 25.0)]

    and
    for x,y in FunctionIterator(square, 0.0, 5.0, 5): print x,y

    produces output

    0.0 0.0
    1.0 1.0
    2.0 4.0
    3.0 9.0
    4.0 16.0
    5.0 25.0

    NOTE: for functions that are undefined at a given x (e.g. log(-1))
    the y value returned is set to 10000000
    """

    def __init__(self, f, startx, endx, steps):
        self._f = f
        self._startx = startx
        self._endx = endx
        self._delta = (endx-startx)/steps


    def __iter__(self):
        self._x = self._startx
        self._zero = False
        return self

    def next(self):
        if self._x > self._endx + self._delta/2:
            raise StopIteration
        else:
            x = self._x
            try:
                y = self._f(x)
                self._x += self._delta
                return (x, y)
            except ZeroDivisionError:
                if x == self._startx:
                    x += self._delta/2
                    y = self._f(x)
                    self._x += self._delta
                    return (x, y)
                elif self._zero:
                    x += self._delta/2
                    y = self._f(x)
                    self._x += self._delta
                    self._zero = False
                    return (x, y)
                else:
                    x -= self._delta/2
                    y = self._f(x)
                    self._zero = True
                    return (x, y)
            except:
                self._x += self._delta
                return (x, 10000000)
                    

            
class WorldScreen(object):
    """The WorldScreen class is used to convert between real coodinates
    and screen coordinates.

    Constructor: WorldScreen(x1, y1, x2, y2, width, height)
    (x1, y1) : The bottom left in real coords
    (x2, y2) : The top right in real coords
    width : the width of the screen (canvas)
    height: the height of the screen (canvas)

    NOTE: On a canvas the y increases are you move down the canvas
    so a 'flip' occurs between real y values and screen values - see 
    example below

    """

    def __init__(self, x1, y1, x2, y2, width, height):
        self.x = x1
        self.y = y1
        self.xscale = (x2-x1)/width
        self.yscale = (y2-y1)/height
        self.height = height

    def world2screen(self, x, y):
        """Return the screen (canvas) coordinates given real coordinates.

        If the calculated screen y coord is outside the screen then the
        appropriate 'edge value' is returned.

        world2screen(float, float) -> (float, float)

        Example:
        >>> ws = World_Screen(0,0,10,10, 100.0, 100.0)
        >>> ws.world2screen(5, 5)
        (50.0, 50.0)
        >>> ws.world2screen(10, 10)
        (100.0, 0.0)
        Note that in this case when y is 10 in real coordinates (i.e.
        at the top then the y coord in the canvas is 0 (i.e. at the top)
        """
        wy = self.height - (y - self.y)/self.yscale
        """
        if wy < 0:
            wy = 0
        elif wy > self.height:
            wy = self.height
        """
        return ((x-self.x)/self.xscale, wy)

    def screen2world(self, x, y):
        """Return the real coordinates given screen (canvas)coordinates.

        screen2world(float, float) -> (float, float)

        Example:
        >>> ws = World_Screen(0,0,10,10, 100.0, 100.0)
        >>> ws.screen2world(50,50)
        (5.0, 5.0)
        >>> ws.screen2world(100,0)
        (10.0, 10.0)
        """

        return (x*self.xscale + self.x, (self.height - y)*self.yscale + self.y) 

