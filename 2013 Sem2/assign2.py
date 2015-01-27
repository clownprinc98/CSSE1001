from Tkinter import *
import tkMessageBox
import tkFileDialog

#
# Do not change the following import
#

import Maze_Generator

####################################################################
#
# Insert your code below
#
####################################################################

class InvalidMaze(Exception):
    def __init__(self):
        tkMessageBox.showerror("Invalid Maze","Invalid Maze format.")

class MazeApp(object):
    """
        This is the top level interface for the maze program
    """
    def __init__(self, master):
        self._master = master
        self._master.title("Maze Game")
        self._master.minsize(300,300)
        
        self._maze = Maze(self._master)
        self._menuBar = Menu(self._master)
        self._master.configure(background="grey", menu=self._menuBar)
        self._fileMenu = Menu(self._menuBar, tearoff=0)
        self._fileMenu.add_separator()
        self._fileMenu.add_command(label="Open Maze File", command=self._maze.load_maze)
        self._fileMenu.add_command(label="Save Maze File", command=self._maze.save_maze)
        self._fileMenu.add_command(label="Exit", command=self.exit)
        
        self._menuBar.add_cascade(label="File", menu=self._fileMenu)
        self.GenMaze = Maze_Generator.MazeGenerator()

    
    def exit(self):
        """
            This method will end the application
        """
        self._master.destroy()
        
class Maze(Frame):
    """
        This class manages the drawing, movement, and coliision checking of the maze
    """
    def __init__(self, parent):
        Frame.__init__(self, bg="grey")
        self.pack(side=TOP,fill=BOTH, anchor=N)
        self._playerPosition = (1,1) #Default player position
        self._foundPlaces = [] #list of tuples of 'discovered' squares
        self._parent = parent 
        self._loadedMaze = [] #the maze is stored as a list.
        
        canvasFrame = Frame(self, bg="grey")
        self.canvas = Canvas(canvasFrame, bg="white", bd=2, relief=SUNKEN)
        self.canvas.pack(side=BOTTOM, expand=1, fill=X)
        canvasFrame.pack()
        
        # Key bindings from the keyboard
        self.canvas.bind('<Left>', self.key_left)
        self.canvas.bind('<Right>', self.key_right)
        self.canvas.bind('<Down>', self.key_down)
        self.canvas.bind('<Up>', self.key_up)
        self.canvas.focus_set()
        
        #The player object which is drawn
        self._player = self.canvas.create_rectangle(-20, -20, 0, 0, fill="purple")
        FrameSettings = Frame(self, bg="grey")
        
        #Make some buttons that control the game. No need to store their reference as we don't need to refer to them later
        Button(FrameSettings, text='Quit', relief=GROOVE, command=self.exit).pack(side=RIGHT, expand=1)
        Button(FrameSettings, text='Reset', relief=GROOVE, command=self.reset_maze).pack(side=RIGHT, expand=1)
        Button(FrameSettings, text='New', relief=GROOVE, command=self.new_maze).pack(side=RIGHT, expand=1)

        FrameSettings.pack(side=BOTTOM, anchor=S, fill=X)
        
        # Store everything else needed for the maze. no need to store the reference of their container
        mazeSettingsFrame = Frame(FrameSettings, bg="grey", relief=GROOVE, bd=1)
        self._mazeSizeText = Spinbox(mazeSettingsFrame, from_=5, to=30, command=self.spinbox_check)
        self._mazeSizeText.pack(side=LEFT)
        
        mazeSettingsFrame.pack(side=LEFT, expand=1)
        
    def key_left(self, ev):
        """
            The event of when the player presses left
        """
        self._playerPosition =  self.move(self._playerPosition, 0)[0]
        self.update_maze()
        
    def key_right(self, ev):
        """
            The event of when the player presses right
        """
        self._playerPosition =  self.move(self._playerPosition, 1)[0]
        self.update_maze()
        
    def key_down(self,ev):
        """
            The event of when the player presses down
        """
        self._playerPosition =  self.move(self._playerPosition, 2)[0]
        self.update_maze()
        
    def key_up(self, ev):
        """
            The event of when the player presses up
        """
        self._playerPosition =  self.move(self._playerPosition, 3)[0]
        self.update_maze()


    def save_maze(self):
        """
            Saves the maze to the specified dialogue box location.
        """
        savestr = ""
        self._loadedMaze[self._playerPosition[1]][self._playerPosition[0]] = "O"
        for i in self._loadedMaze:
            for c in i:
                savestr += c
            savestr += "\n"
        SaveLoc = tkFileDialog.asksaveasfilename()
        Save = file(SaveLoc, "w")
        Save.write(savestr)

    
    def init_maze(self, maze):
        """
            converts a string maze into a list, and resets all appropriate variables.
            <Str> -> <None>
        """
        if self.check_maze(maze) == True:
            self._loadedMaze = self.maze_to_list(maze)
            self._playerPosition = self.get_player_pos()
            self.canvas.config(width=20*len(self._loadedMaze[0]), height=20*len(self._loadedMaze))
            self.canvas.delete(ALL)
            self._foundPlaces = []
            self.update_maze()
            
    def new_maze(self):
        """
            Starts a new maze
        """
        mazeGen = Maze_Generator.MazeGenerator()
        size = self._mazeSizeText.get()
        if size.isdigit():
            strMaze = mazeGen.make_maze(int(size))
            self.init_maze(strMaze)
        else:
            tkMessageBox.showerror("Maze Dimension Error","Invalid maze size")
        
    def load_maze(self):
        """
            Load the maze from filename.
        """
        openfile = tkFileDialog.askopenfilename()
        try:
            File = file(openfile, "Ur")
            strMaze = File.read()
            self.init_maze(strMaze)
        except:
            pass
            

    def game_over(self):
        """
            Triggers when the player finds the finish point
        """
        tkMessageBox.showinfo("You Win","You win, loading new maze...")
        self.new_maze()
        
    def reset_maze(self):
        """
            Triggers when the player clicks the reset button
        """
        if self._foundPlaces:
            self.canvas.delete(ALL)
            self._playerPosition = (1,1)
            self._foundPlaces = []
            self.update_maze()

    def get_player_pos(self):
        """
            Returns the player position
            <None> -> <(int, int)>
        """
        for index, char in enumerate(self._loadedMaze):
            if char.count("O"):
                return (char.index("O"), index)
        return (1,1)
        
    def maze_to_list(self, strMaze):
        """
            Turns a string into a 2d list, with \n as a seperator
            <Str> -> <list(list)>
        """
        new_maze = []
        strMaze = strMaze.split("\n")
        for i in strMaze:
            new_maze.append(list(i))
        return new_maze
    
    def exit(self):
        """
            Ends the application
        """
        self._parent.destroy()

    def check_maze(self, maze):
        """
            Ensures the integrity of the maze. Makes sure there are no bad characters, etc.
            Returns True if maze is good
            <list(list)> -> bool
        """

        if len(maze) == 0:
            raise InvalidMaze
        rows  = maze.split("\n")
        rowlength = rows[0]
        for row in rows:
            if rowlength != rowlength:
                raise InvalidMaze
        for char in maze:
            if char not in Maze_Generator.SQUARES and char != "\n" and char != "O":
                raise InvalidMaze
        if maze.count(Maze_Generator.FINISH) != 1:
            raise InvalidMaze
        if maze.count("O") > 1: # if there is more than one player
            raise InvalidMaze
        return True
        
    def update_maze(self):
        """
            This re-draws all appropriate squares upon movement
        """
        x = 20*self._playerPosition[0]
        y = 20*self._playerPosition[1]
        # look at each side of player
        # 20 because each rectangle is 20px long
        locs = [(x-20, y-20), (x, y-20),(x+20, y+20), (x-20, y), (x+20, y), (x-20, y+20), (x, y+20), (x+20, y-20)]
        for i in locs:
            row = i[0]/20
            col = i[1]/20
            #If location has not been revealed yet, then reveal it
            if i not in self._foundPlaces:
                self._foundPlaces.append(i)
                
                if self._loadedMaze[col][row] == Maze_Generator.WALL:
                    self.canvas.create_rectangle(i[0], i[1], i[0]+20, i[1]+20, fill="red")
                elif self._loadedMaze[col][row] == Maze_Generator.FINISH:
                    self.canvas.create_rectangle(i[0], i[1], i[0]+20, i[1]+20, fill="blue")
            
        #re-draw the player in their new location        
        self.canvas.delete(self._player)
        self._player = self.canvas.create_rectangle(x, y, x+20, y+20, fill="purple")
        
        #Win the game if the player is on the finish line
        if self._playerPosition == self.get_finish_square():
            self.game_over()
                
    def get_finish_square(self):
        """
            This function returns the coordinates of the finish square
        """
        for index, char in enumerate(self._loadedMaze):
            if char.count("X"):
                return (char.index("X"), index)
            
    def get_position_in_direction(self,position, direction):
        """Return the position of the square adjacent to position in the given 
        direction.

        get_position_in_direction((int, int), str) -> (int, int)
        """
        row, col = position
        dr, dc = Maze_Generator.DIRECTIONS[direction]
        return (row+dr, col+dc)

    def move(self,position, direction):
        """Return information about a move from position in maze in direction.

        The return value is of the form (new_position, maze_state)
        where maze_state is the label on the square the user tried to move to
        ('X', 'F' or 'O')
        new_position is the position after the move (and is unchanged if the
        move is not valid)

        move(list(list(str)), (int, int), str) -> ((int, int), str)
        """
        x, y = new_position = self.get_position_in_direction(position, direction)
        value = self._loadedMaze[y][x]
        if value == Maze_Generator.WALL:
            new_position = position
        return new_position, value

    def get_possible_directions(self,maze, position):
        """Return a list of all legal directions in maze at position.

        get_possible_directions(list(list(str)), (int, int)) -> list(str)
        """
        dirs = []
        for d in 'nsew':
            x, y =self.get_position_in_direction(position, d)
            if maze[y][x] != Maze_Generator.WALL:
                dirs.append(d)
        return dirs

    def spinbox_check(self):
        """
            This code is run when the user clicks the arrows on the spinbox.
            The code ensures that only valid numbers are entered for the maze size.
        """
        minval = 4
        maxval = 30
        currentSize = self._mazeSizeText.get()
        try:
            currentSize = int(currentSize)
            if currentSize < minval:
                self._mazeSizeText.delete(0, END)
                self._mazeSizeText.insert(0, minval)
            else:
                raise Exception
        except:
            # If current size is alphanumeric
            if str(currentSize).isdigit() == False:
                tkMessageBox.showerror("Maze Dimension Error","Maze size was not a valid number")
            #make sure current size is not out of bounds
            elif currentSize < minval:
                tkMessageBox.showerror("Maze Dimension Error","Maze size cannot be less than {0}".format(minval))
                self._mazeSizeText.delete(0, END)
                self._mazeSizeText.insert(0, minval)
            elif currentSize < minval:
                tkMessageBox.showerror("Maze Dimension Error","Maze size cannot be less than {0}".format(minval))                
                self._mazeSizeText.delete(0, END)
                self._mazeSizeText.insert(0, minval)
            elif currentSize > maxval:
                tkMessageBox.showerror("Maze Dimension Error","Maze size cannot be more than {0}".format(maxval))                
                self._mazeSizeText.delete(0, END)
                self._mazeSizeText.insert(0, maxval)
                
            
####################################################################
#
# WARNING: Leave the following code at the end of your code
#
# DO NOT CHANGE ANYTHING BELOW
#
####################################################################

def main():
    root = Tk()
    app = MazeApp(root)
    root.mainloop()

if  __name__ == '__main__':
    main()
