from assign2_support import *

####################################################################
#
# Insert your code below
#
####################################################################



class PlotApp(object):
    """This top-level interface is responsible for the smooth operation of the program. It makes all the important method calls and such"""
    def __init__(self,master):
        #sep up all our labels and entry boxes
        self._master = master
        self._master.title("PlotApp")
        self._master.minsize(1000,480)
        self._master.geometry("1000x600")
        self._master.configure(background="grey")
        
        self._pointFrameArea = PointFrame(self._master, self) #make the PointFrame instance
        
        self._canvas = Canvas(self._master, bg="white", bd=2, relief=SUNKEN)
        self._canvas.pack(side=TOP, expand=1, fill=BOTH,padx=10, pady=10)
        self._canvas.bind('<Motion>', self.evt_motion) #bind the mouse movement action to the canvas widget
        self._canvas.bind('<Button-1>', self.evt_button1) #lets us know where the mouse is clicked on the widget
        self._canvas.bind("<Configure>", self.resize) #when the canvas is resized, call the resize function


        self._functionFrameArea = FunctionFrame(self._master) #make the functionframe-frame instance

        self._plotFrameArea = PlotFrame(self._master, self)#make the PlotFrame-frame instance
        
        self._buttonsArea = ButtonFrame(self._master, self)#make the ButtonFrame-frame instance

        self._functionValues = [] #this will store all our function values
        self._functions = [] #this will store all our function objects
        self._canvasCoords = False
        self.update_canvas_coords()
        
    def update_canvas_coords(self):
        """
            This method will create a WorldScreen instance and assign it to self._canvasCoords. 
            This is used to manage the cursor location and the heights.
            <None> -> <None>
        """
        if self.get_values():
            x1,y1,x2,y2,width,height = self.get_values()
            self._canvasCoords = WorldScreen(x1,y1,x2,y2,width,height)
        
    def get_values(self):
        """
            This function returns the minx, miny, maxx, maxy, width, 
            and height of the canvas, all stored in a tuple. False otherwise
            <None> -> (float, float, float, float, int, int)
            <None> -> False
        """
        
        width = float(self._canvas.winfo_width())
        height = float(self._canvas.winfo_height())
        try:
            x1=float(self._plotFrameArea._entryStartx.get())
            y1=float(self._plotFrameArea._entryEndy.get())
            x2=float(self._plotFrameArea._entryEndx.get())
            y2=float(self._plotFrameArea._entryStarty.get())
        except:
            return False
        
        return (x1,y2,x2,y1,width,height)

    ### mouse events here
    def evt_motion(self, e):
        """ 
            This method updates the PointFrame label to let the user know where
            the mouse is on the canvas. 
        """
        
        self.update_canvas_coords()
        translatedCoords = self._canvasCoords.screen2world(e.x,e.y)

        self._pointFrameArea.update_mouse_move(translatedCoords)

    def evt_button1(self,e):
        """
            This method updates the PointFrame label to let the user know where
            the mouse was last clicked on their canvas. 
        """
        
        self.update_canvas_coords()
        translatedCoords = self._canvasCoords.screen2world(e.x,e.y)

        self._pointFrameArea.update_click(translatedCoords)

    ## end mouse events
        
    def resize(self,e):
        """
            This method is called whenever the canvas is 'configured'. 
            It is used to keep the canvas a good size on the screen
        """
        self._canvas.configure(height = (self._master.winfo_height()/1.5))
        self.update_function_list()
        self.draw_all_functions()

    ### colour and function choosing###
    
    def get_function_and_colour(self):
        """
            Eeturns the function object, and the colour both stored in the same tuple
            <None> -> (Function, Str)
        """
        try:
            function = self._functionFrameArea.get_function()
            return (function, self._functionFrameArea.get_color())
        except FunctionError:
            tkMessageBox.showerror("Function Error", "Please check that your function is in the correct format.")
            return False
        except TclError:
            tkMessageBox.showerror("Colour","Not a valid hexdecimal Colour")
            return False
    ### end colour and function choosing##
    

    ## function value generation here ##
    
    def update_function_list(self):
        """This is called when the screen is resized. It generates and redraws all the functions from the self._functions list"""
        if not self.get_values():
            tkMessageBox.showerror("Dimension Error", "Please ensure you have entered valid graph ranges")
        else:
            x1,y1,x2,y2,width,height = self.get_values()
            
            if self._plotFrameArea.check_inputs(x1,x2,y2,y1) == True:
                step = self._plotFrameArea.get_step()
                if self.get_function_and_colour() != False:
                    function, colour = self.get_function_and_colour()
                    self._functionValues = []
                    for i in self._functions:
                        f = self._plotFrameArea.generate_function_values(i, x1,x2,step)
                        self._functionValues.append((f,colour))

        
    def generate_function_list(self):
        """ This method generates the list of function values using the method generate_function_values in the PlotFrame class."""
        if not self.get_values():
            tkMessageBox.showerror("Dimension Error", "Please ensure you have entered valid graph ranges")
        else:
            
            x1,y1,x2,y2,width,height = self.get_values()
            if self._plotFrameArea.check_inputs(x1,x2,y2,y1) == True:
                step = self._plotFrameArea.get_step()
                if self.get_function_and_colour() != False:
                    function, colour = self.get_function_and_colour()
                    self._functions.append(function)
                    f = self._plotFrameArea.generate_function_values(function, x1,x2,step)
                    self._functionValues.append((f,colour))
                    self.draw_all_functions()

        
    ## function value generation end ##

    ## actual function drawing ##

    
    def draw_all_functions(self):
        """This method draws all the values in the self._functionValues variable. Is the core drawing method"""
        self._canvas.delete(ALL)
        numplots = len(self._functionValues)
        numdrawn = 0
        if self.get_values() == False:
            tkMessageBox.showerror("Dimension Error", "Please ensure you have entered valid graph ranges")
        else:
            self.update_canvas_coords()
            width = float(self._canvas.winfo_width())
            height = float(self._canvas.winfo_height())
        #have a loop to dictate how many times to loop while we loop (plot each value in our list).
        
            for plotnumber in self._functionValues:
                firstval = True #find out if we have a value on the canvas yet
                for coord in plotnumber[0]:
                    colour = plotnumber[1]
                    if firstval: #if this is our first point, set the first point to be off the screen
                        x1 = 0-width
                        y1 = 0-height
                        x2,y2 = coord
                        firstval = False
                    else:
                        x1 = x2
                        y1 = y2
                        x2,y2 = coord
                    pos1 = self._canvasCoords.world2screen(x1,y1)
                    pos2 = self._canvasCoords.world2screen(x2,y2)

                    self._canvas.create_line(pos1[0],pos1[1],pos2[0],pos2[1],fill=colour)
        
    ## actual function drawing end ##


    ###buttons!
    def remove_last_function(self):
        """This method removes the last value in the self._functionValues, and self.Fucntions variables. it also removes it from the canvas"""
        if self._functions:
            self._canvas.delete(ALL)
            self._functionValues.pop(-1)
            self._functions.pop(-1)
            self.draw_all_functions()
        else:
            tkMessageBox.showerror("Function Error", "No functions to remove")
            
    def remove_all_functions(self):
        """This method removes all funtions from their respective variables. and then clears the canvas"""
        self._canvas.delete(ALL)
        self._functionValues = []
        self._functions =[]
        
    def exit_application(self):
        """This method exits the program"""
        self._canvas.delete(ALL)
        self._master.destroy()

    ###end buttons
class PointFrame(Frame):
    """This class is responsible for displaying the mouse co-ordinates as well as the last mouse-position clicked"""
    def __init__(self,master, parent):
        Frame.__init__(self, master, bg="grey")

        self.lblLastPoint = Label(self,text="Last Point Clicked: ",bg="grey")
        self.lblLastPoint.pack(side=LEFT)
        self.lblCursorPoint = Label(self, text="Last Mouse Position: ",bg="grey")
        self.lblCursorPoint.pack(side=LEFT)
        self.pack(side=TOP, fill=BOTH, expand=1)

    def update_mouse_move(self, realCoords):
        """updates the PointFrame mouse coordinates value"""
        self.lblCursorPoint.configure(text="Last Cursor Point: ({0}, {1})".format(round(realCoords[0],2), round(realCoords[1],2)))

    def update_click(self, realCoords):
        """updates the PointFrame last clicked coordinates value"""
        self.lblLastPoint.configure(text="Last Cursor Point: ({0}, {1})".format(round(realCoords[0],2), round(realCoords[1],2)))

     
class FunctionFrame(Frame):
    """This class, which inherits from the
Frame class, defines a widget for entering the function definition and choosing
the plot colour for the function.. This class also has a method that returns the function """
    def __init__(self, master):
        Frame.__init__(self, master, bd=3, pady=5, relief=SUNKEN) #make a frame from the inherited class


        #sep up all our labels and entry boxes
        self.lblFunction = Label(self, text="Function in x: ")
        self.lblFunction.pack(side=LEFT)

        self._entryFunction = Entry(self)
        self._entryFunction.insert(0,"x**2")
        self._entryFunction.pack(side=LEFT)

        self._btnColourSelect = Button(self, text="Select", command=self.select_colour)
        self._btnColourSelect.pack(side=RIGHT)

        self._entryColour = Entry(self)
        self._entryColour.insert(0,"#000000")
        self._entryColour.pack(side=RIGHT)
        
        Label(self, text="Function Colour: ").pack(side=RIGHT)

        self.pack(side=TOP, fill=X, expand=1)
        
        
    def get_color(self):
        """
            This method returns the string representation of the colour
            to plot the next function in
            <None> -> <Str>
        """
        return self._entryColour.get()
        
    def select_colour(self):
        """
            This method is responsible for interacting with the user and finding out what colour they chose
            <None> -> <None>
        """
        self._entryColour.delete(0, END)
        chosenColour = askcolor(title="Please choose your colour") #open the colour picker box
        self._entryColour.insert(0, chosenColour[1]) #the colour picker returns a tuple, with RGB and then hexdecimal. we want to keep the hexdecimal colour
        
    def get_function(self):
        """This method returns the function (as a function and not a string)"""
        return make_function(self._entryFunction.get())
    
class PlotFrame(Frame):
    """This class defnes a widget for entering the plot information for all the function."""
    def __init__(self, master, parent):
        Frame.__init__(self, master,  bd=3, pady=5, relief=SUNKEN) #make a frame from the inherited class


        #set up all the labels and entry box widgets.
        
        Label(self, text="Plot Settings").pack(side=LEFT)
        
        Label(self, text="Start X: ").pack(side=LEFT)
        
        self._entryStartx = Entry(self)
        self._entryStartx.insert(0,"0")
        self._entryStartx.pack(side=LEFT)
        
        Label(self, text="End X: ").pack(side=LEFT)

        self._entryEndx = Entry(self)
        self._entryEndx.insert(0,"10")
        self._entryEndx.pack(side=LEFT)
        
        Label(self, text="Start Y: ").pack(side=LEFT)

        self._entryStarty = Entry(self)
        self._entryStarty.insert(0,"0")
        self._entryStarty.pack(side=LEFT)
        
        Label(self, text="End Y: ").pack(side=LEFT)

        self._entryEndy = Entry(self)
        self._entryEndy.insert(0,"10")
        self._entryEndy.pack(side=LEFT)
        
        Label(self, text="Steps: ").pack(side=LEFT)

        self._entrySteps = Entry(self)
        self._entrySteps.insert(0, "50") #just a default value of 50 steps
        self._entrySteps.pack(side=LEFT)
        
        self.pack(side=TOP, fill=X, expand=1) #pack the from the widgets are going in
    
    def get_step(self):
        """
            This method returns the number of steps to plot the next function with
            <None> -> <int>
        """
        return int(self._entrySteps.get())
        
    def check_inputs(self, xmin,xmax,ymin,ymax):
        """
            This method checks all of the values to ensure there are no errors.
            <int, int, int, int> -> bool
        """
        step = self._entrySteps.get();
        if not step.isdigit():
            tkMessageBox.showerror("Value Error","Your step number must be numerical and larger than 0")
            return False
        if xmin > xmax:
            tkMessageBox.showerror("Value Error","You cannot have a minimum x value larger than your maxiumum x")
            return False
        if ymax > ymin: #cause the y vals are flipped on the canvas. ymax is actually ymin.
            tkMessageBox.showerror("Value Error","You cannot have a minimum y value larger than your maximum y")
            return False
        if step < 1: 
            tkMessageBox.showerror("Value Error","The number of steps must be greater than 0")
            return False
        return True
        
    def generate_function_values(self, function, xmin, xmax, steps):
        """
            this method uses functionIterator to get a list of all the function values
            <Function, int, int, int> -> <(float, float), (float, float) ...>
        """
        return tuple(FunctionIterator(function, xmin, xmax, steps))

        
class ButtonFrame(Frame):
    """This class, inheriting from the Frame class, defines a widget that contains a
collection of buttons."""

    def __init__(self, master, parent):
        Frame.__init__(self, master,  bd=3, relief=GROOVE) #make a frame from the inherited class
        #Make all buttons
        Button(self, text="Add Function", command=parent.generate_function_list).pack(side=LEFT)
        Button(self, text="Redraw All Functions", command=parent.draw_all_functions).pack(side=LEFT)
        Button(self, text="Remove Last Function", command=parent.remove_last_function).pack(side=LEFT)
        Button(self, text="Remove All Functions", command=parent.remove_all_functions).pack(side=LEFT)
        Button(self, text="Exit", command=parent.exit_application).pack(side=LEFT)

        self.pack(side=TOP) # pack the frame the buttons will be living in


####################################################################
#
# WARNING: Leave the following code at the end of your code
#
# DO NOT CHANGE ANYTHING BELOW
#
####################################################################

def main():
    root = Tk()
    app = PlotApp(root)
    root.mainloop()

if  __name__ == '__main__':
    main()
