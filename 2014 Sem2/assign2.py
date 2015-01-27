from assign2_support import *

import datetime

class PVPlotApp(object):

    def __init__(self, master):
    
        master.title("PV Plotter")
        master.minsize(800,600)
        self.master = master
        self.pvData = PVData()
        
        self.plotter = Plotter(master, self)
        self.optionsframe = OptionsFrame(master, self)
        
        
    def update_plot_info(self, array, checkValue):
        """This method is called from the child (self.optionsframe) when the apply button is clicked"""
        self.plotter.clear_plot() # clear all data on the plot
        self.plotter._plotsToUpdate = [0,0,0] # set all plot flags to be false
        
        # Plot each plot that has its checkBox ticked.
        
        if(checkValue[2].get()): #plot this first because it sits under everything
            # plot sunlight
            self.plotter.plot_sunlight(self.pvData.get_sunlight())
            
        if(checkValue[0].get()):
            #plot power
            self.plotter.plot_power(self.pvData.get_power(array), array)
            
        if(checkValue[1].get()): # plot this last as it goes on top of everything
            # plot temp
            self.plotter.plot_temp(self.pvData.get_temperature())
            
    def change_date(self, newDate, array, checkValue):
        """This method is called from the child (self.optionsframe) when the apply button is clicked"""
        if self.pvData.change_date(newDate): # if newDate is a valid date
            self.plotter.change_date(newDate) # set the new date on the label
            self.update_plot_info(array, checkValue) # re-plot the new data loaded
        
    def get_detailed_info(self, timeIndex):
        """ This returns the data needed to display on the top label while the user is clicking the canvas """
        # Get the selected location
        arrayName = self.optionsframe.DefaultLocation.get()
        # return (current time string, power at that time, temperature at that time, sunlight value at that time)
        return (self.pvData.get_time(timeIndex), self.pvData.get_power(arrayName)[timeIndex], self.pvData.get_temperature()[timeIndex], self.pvData.get_sunlight()[timeIndex])
        
        
class PVData(object):

    def __init__(self):
        """
        Initializes PV data to use yesterdays data
        """
        self.date = yesterday()
        self.change_date(self.date)

    def change_date(self, date):
        """
        changes the date to be for the given date (making this date the
        'current date')
        change_date(str) -> None

        Precondition: date must be in correct format 'dd-mm-yyyy' or
        'd-mm-yyyy', or 'd-m-yyyy', etc.
        
        Returns False is an invalid date is supplied. True otherwise
        """
    
        if date == "": 
            tkMessageBox.showerror("Date Error", "No date given.")
            return False
            
        try: # if anything goes wrong trying to make the date it must be wrong, so error out
            SplitDate = date.split("-")
            newDate = datetime.date(int(SplitDate[2]), int(SplitDate[1]), int(SplitDate[0])) #make the date object here
            if newDate > datetime.date.today(): # if the date is not before today
                tkMessageBox.showerror("Date Error", "Date must be before today.")
                return False
        except:
            tkMessageBox.showerror("Date Error", 'Invalid date: "' + str(date) + '"')
            return False
            
        # date must be valid if we got this far, so load the data from the current date    
        self.date = date
        self.timeStrings = [] # all times for the current date
        self.temperatures = [] # all temperatures for the mapped to time indexes for the current date
        self.sunValues = [] # all sunlight values mapped to time indexes for the current date
        
        # set the powerLevels to map to a list from an array name
        
        # power value relative to time as a dictionary
        # Loop over arrays and associate each array name with a new, empty list
        self.powerLevels = dict((arrayName, []) for arrayName in ARRAYS)

        # load the data from the server
        self.data = load_data(self.date)

        for EachMinute in self.data:
            ## tuple from load_data is
            ## (time,temp,sun,(powers))
            self.timeStrings.append(EachMinute[0])
            self.temperatures.append(EachMinute[1])
            self.sunValues.append(EachMinute[2])
            for index, value in enumerate(ARRAYS):
                # Access the array with value, then add its respective
                # power value onto that list
                self.powerLevels[value].append(EachMinute[3][index])
        return True
        
    def get_date(self):
        """
            Returns the date for the stored data
            get_date(None) -> str
        """
        return self.date

    def get_time(self, time_index):
        """
            Returns tie for the given index of time data
            get_time(int) -> str
        """
        return self.timeStrings[time_index]

    def get_temperature(self):
        """
            Returns the list of temperature values for the current date
            get_temperature(None) -> list <float>
        """
        return self.temperatures

    def get_sunlight(self):
        """
            Returns the list of sunlight values for the current date
        """
        return self.sunValues

    def get_power(self, array):
        """
            Returns the list of power output for the current date and the given
            array (the array name)
            get_power(str) -> list <int>
        """
        
        return self.powerLevels[array]

class Plotter(Canvas):
    """
        Responsible for doing the plotting and inherits from Canvas
    """
    def __init__(self, master, parent):

        Canvas.__init__(self, master, bd = 2, relief = SUNKEN, bg="white") # create the canvas
        # bind the canvas to some user actions
        
        self.bind("<Configure>", self.resize) #when the canvas is resized, run self.resize
        self.bind('<Button-1>', self.mouse_down) # when the canvas s clicked, run mouse_down
        self.bind('<ButtonRelease-1>', self.mouse_up) # when the left mouse is released
        self.bind('<B1-Motion>', self.mouse_move) #bind the mouse movement action, while the left mouse utton is down
        
        # An array that stores which plots to update (Powers, Temp, Sun)
        self._plotsToUpdate = [0,0,0]
        
        # Temporary storage for re-plotting data on the self.resize(event) callback
        self._powerData = []
        self._tempData = []
        self._sunData = []
        self._arrayName = ARRAYS[-1]
        self._date = yesterday()
        
        # Set up the parent and master
        self.master = master
        self.parent = parent
       
        # set up the date label
        self.date1 = Label(master, text = "Data for " + str(self._date))
        
        self.date1.pack(anchor = W, pady = 10, padx = 10) #pack label
        
        self.pack(fill = BOTH, pady = 5, padx = 5, side = TOP, expand = True)
        #packing canvas and using expand made sure than it actually resized with window resize
        
        # Set up the coordinate Translator
        self.coordTranslator = CoordinateTranslator(self.winfo_width(), self.winfo_height(), len(self.parent.pvData.get_temperature()))

    def resize(self, event):
        """ This event triggers when the canvas is resized. It updates the coordinate Translator with the
            new canvas dimensions """
        self.coordTranslator.resize(self.winfo_width(), self.winfo_height())
        self.update_plots()
        
    def change_date(self, NewDate):
        """
            This event is called from its parent, and when mouse_up happens. It updates the date label to show the specified date
        """
        self._date = NewDate
        self.date1.config(text = "Data for " + NewDate)
        
    def update_plots(self):
        """
            Re-plots all the data if the self._plotsToUpdate[n] is set for n
        """
        self.clear_plot()
        if(self._plotsToUpdate[2]):
            self.plot_sunlight(self._sunData)
            
        if(self._plotsToUpdate[0]):
            self.plot_power(self._powerData, self._arrayName)
            
        if(self._plotsToUpdate[1]):
            self.plot_temp(self._tempData)
            
        
        
    def plot_power(self, powerData, arrayName):
        """
            Plots the power of the specified array using the data stored in powerData
        """
        self._plotsToUpdate[0] = 1 # flag this as being an active plot
        self._powerData = powerData # re-assign temporary variables
        self._arrayName = arrayName
        
        height = self.winfo_height() # get the canvas height
        
        for index, value in enumerate(powerData):
            y1 = height # The canvas coords are inverted, so we want to plot from height (which is actually the bottom)
            x2, y2 = self.coordTranslator.power_coords(index, value, arrayName) # convert y-coord to canvas-y-coord
            self.create_line(x2, y1, x2, y2, fill="purple", w=2) # draw the line, keeping the x-axis constant
        
    def plot_temp(self, tempData):
        """
            Plots the temperature using the data in tempData
        """
        self._plotsToUpdate[1] = 1# flag this as being an active plot
        self._tempData  = tempData # re-assign temporary variables
        height = self.winfo_height() # get the canvas height
        
        for index, value in enumerate(tempData):
            if index < len(tempData)-1:  #make sure we don't go out of bounds of the array
                x1, y1 = self.coordTranslator.temperature_coords(index, value) # get the current point
                x2, y2 = self.coordTranslator.temperature_coords(index+1, tempData[index+1]) # get the next point
                self.create_line(x1, y1, x2, y2, fill="red", w = 1) # plot for current time, to next time
                
    def plot_sunlight(self, sunData):
        """
            Plots the sunlight data using the data in sunData
        """
        self._plotsToUpdate[2] = 1 # flag this as being an active plot
        self._sunData = sunData # re-assign temporary variables
        height = self.winfo_height() # get the canvas height
        for index, value in enumerate(sunData):
            y1 = height # the height is actually the bottom of the canvas
            x2, y2 = self.coordTranslator.sunlight_coords(index, value) # translate the sunlight index and value into x,y coords
            self.create_line(x2, y1, x2, y2, fill="orange", w=2) # plot the line, keeping the x-axis constant
        
    def clear_plot(self):
        """
            This deletes everything on the canvas
        """
        self.delete(ALL)
    
    
    def update_label(self, x):
        """
            This updates the label at the top of the window with detailed information:
                eg. Data for xx-xx-xx at 10:00 Power :yy Temperature: 99 etc.
        """
        labelInfo = "" # make an empty string for adding data to later
        # use the coordinate translator to turn the canvas coord into a useful time index
        infoAtTime = self.parent.get_detailed_info(self.coordTranslator.get_index(x)) # use the parent to retrieve the appropriate data
        
        # Add the date and the time to be displayed
        labelInfo = "Data for " + self._date + " at " + infoAtTime[0] + ":    "
        
        if self._plotsToUpdate[0]: # if the Power plot is flagged as being displayed, add its info the the label
            labelInfo += "Power " + str(round(infoAtTime[1]/1000.0,2))+ "kW    " 
        if self._plotsToUpdate[1]: # if the Temperature plot is flagged as being opened, add its info to the label
            labelInfo += "Temperature " + str(infoAtTime[2]) + "C    "
        if self._plotsToUpdate[2]: # if the sunlight is flagged as being opened, add its info to the label
            labelInfo += "Sunlight " + str(infoAtTime[3]) + "W/m^2"
            
        self.date1.config(text = labelInfo) # set the label to the new info
        
            
    def mouse_up(self, event):
        """ the callback function for when the mouse click is released"""
        self.delete(self._infoLine) # delete the information line
        self.change_date(self._date) # set the label at the top of the screen to only display the date
        
    def mouse_move(self, event):
        """
            This is the call back function for when the mouse moves with the left button pressed
        """
        self.delete(self._infoLine) # delete the informtion line
        x1 = event.x # calculate the new coordinates for the information line
        y1 = 0
        y2 = self.winfo_height()
        x2 = x1
        self._infoLine = self.create_line(x1, y1, x2, y2) # re-draw the information line
        self.update_label(x1) #update the information label for the current coordinate
        
    def mouse_down(self, event):
        """
            This is the callback function for when the user initially left-clicks the canvas. It initialises the self._infoLine variable
        """
        x1 = self.coordTranslator.temperature_coords(event.x, 0)[0] # we don't care about the y-coord, as the line goes from top to bottom
        y1 = 0 # set the y1 and y2 to go from 0 to canvas height
        y2 = self.winfo_height()
        x2 = x1 # set the x2 and x1 to point to the same location, this will create a straight line up and down with the y1 and y2 values
        self._infoLine = self.create_line(x1, y1, x2, y2)
        self.update_label(x1)
        
class OptionsFrame(Frame):
    """
    This class is the widget used for choosing options and inherits from Frame
    consists of 3 checkbuttons, entrybox, button and options menu
    """

    def __init__(self, master, parent):
        
        Frame.__init__(self, master)
        #makes the frame from the inherited class
        
        self.parent = parent
        
        # self.checks is used by the checkboxes. self.checks[0].get() == True means that self.powerBox is checked.
        self.checks = [IntVar(),IntVar(),IntVar()]
        #now make a new frame inside self with checkboxes
        
        self.checkBoxFrame = Frame(self) # add a frame to render the check boxes to. This makes it easier to center them all evenly
        self.powerBox = Checkbutton(self.checkBoxFrame, text = "Power",
                                     variable = self.checks[0], command = self.check_apply_changes)
        self.tempBox = Checkbutton(self.checkBoxFrame, text = "Temperature",
                                     variable= self.checks[1], command = self.check_apply_changes)
        self.sunBox = Checkbutton(self.checkBoxFrame, text = "Sunlight",
                                     variable = self.checks[2], command = self.check_apply_changes)

        self.powerBox.pack(side = LEFT, fill = BOTH, padx = 15) # pack each checkbox, adding some padding and pushing it to the left. this will cause them to center in the checkBoxFrame
        self.tempBox.pack(side = LEFT, fill = BOTH, padx = 15)
        self.sunBox.pack(side = LEFT, fill = BOTH, padx = 15)

        self.checkBoxFrame.pack(side = TOP) # pack this frame, pushing it to the top

        #setting up the label to choose the date
        self.choosedate = Label(self, text = "Choose Date:")
        self.choosedate.pack(side = LEFT, anchor = W, pady = 10, padx = 10)
        
        # make a textbox for the user to put the date into
        self.dateEntryBox = Entry(self)
        # inset the default date into the box
        self.dateEntryBox.insert(0, yesterday())
        self.dateEntryBox.pack(side = LEFT, anchor = W, pady = 10)
        
        #make an apply button, and make it run apply_changes when it is clicked
        self.applyButton = Button(self, text = "Apply", command = self.apply_changes)
        self.applyButton.pack(side = LEFT, anchor = W, padx = 5)

        #setting up array drop down box
        #All arrays combined is the default option
        self.DefaultLocation = StringVar()
        self.DefaultLocation.set(ARRAYS[-1])
        self.ArrayLocations = OptionMenu(self, self.DefaultLocation, ARRAYS[0],
                                         ARRAYS[1], ARRAYS[2], ARRAYS[3],
                                         ARRAYS[4], ARRAYS[5], ARRAYS[6],
                                         ARRAYS[7], ARRAYS[8], ARRAYS[9], command=self.option_apply_changes)
        self.ArrayLocations.pack(side = RIGHT, padx = 10, pady = 10)
        self.pack(side = TOP, fill = X, pady = 10)

    def apply_changes(self):
        """ This function runs when the user clicks the apply button """
        # This sends the parent the current date in the text box, the selected value in the dropdown box,
        # and the array of checkBox info
        self.parent.change_date(self.dateEntryBox.get(), self.DefaultLocation.get(), self.checks)
        
    def option_apply_changes(self, newValue):
        """ This function runs when the user changes the value in the optionMenu box"""
        # This sends the parent the new value, and the update checkBox information
        self.parent.update_plot_info(newValue, self.checks)
        
    def check_apply_changes(self):
        """ THis value is run every time the user clicks on a checkBox """
        # This calls the parent class, and sends it the selected array and new checkbox information
        self.parent.update_plot_info(self.DefaultLocation.get(), self.checks)  
    
####################################################################
#
# WARNING: Leave the following code at the end of your code
#
# DO NOT CHANGE ANYTHING BELOW
#
####################################################################

def main():
    root = Tk()
    app = PVPlotApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
