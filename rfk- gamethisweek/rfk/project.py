
import curses
import os
import random
import re
import string
import sys
import time


from game.casting.actor import Actor
from game.casting.artifact import Artifact
from game.casting.cast import Cast

from game.directing.director import Director

from game.services.keyboard_service import KeyboardService
from game.services.video_service import VideoService

from game.shared.color import Color
from game.shared.point import Point


FRAME_RATE = 12
MAX_X = 900
MAX_Y = 600
CELL_SIZE = 15
FONT_SIZE = 15
COLS = 60
ROWS = 40
CAPTION = "Robot Finds Kitten"
DATA_PATH = os.path.dirname(os.path.abspath(__file__)) + "/data/messages.txt"
WHITE = Color(255, 255, 255)
DEFAULT_ARTIFACTS = 40
# code make by lourenzo/Sean
class Lop:
    possible_chars = 
'''0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"$
%&\'()*+,-./:;<=>?@[\]^_`{|}~'''

    def randomChar(self):
        self.char = random.choice(self.possible_chars)
        
    def randomColor(self):
        self.color = curses.color_pair(random.randint(0,7))
        if random.randint(0, 1):
            self.color = self.color | curses.A_BOLD
            
    def __init__(self, board):
            self.board = board
            self.randomColor()
            self.randomChar()
            board.placeRandomly(self)
            
    class NKI(Lop):
        
        def __init__(self, msg, board):
            Lop.__init__(self, board)
            self.message = msg
            
    def handleCollision(self, whoGoesThere): 
        self.board.setMessage(self.message)
        
class Kitten(Lop):
    
    def handleCollision(self, whoGoesThere):
        self.board.setMessage('')
        row = 1
        meet = 50
        where=self.board.top
        a = self
        b = whoGoesThere
        if a.x > b.x:
            #Kitten is to the right of player; switch the
            #order of the animation
            a,b = b,a
        for i in range(4, 0, -1):
            self.board.erase(a, x=meet-i-1, y=row, where=where)
            self.board.draw(a, x=meet-i, y=row, where=where)
            self.board.erase(b, x=meet+i, y=row, where=where)
            self.board.draw(b, x=meet+i-1, y=row, where=where)
            duration = 1
            if i == 1:
                duration = .5
            time.sleep(duration)
        self.board.top.addstr(0, 49, '<3', curses.color_pair(1) | curses.A_BOLD)
        self.board.top.refresh()
        time.sleep(.75)
        self.board.top.addstr(row, 0, 'You found kitten! Way to go, robot!')
        self.board.top.refresh()
        time.sleep(.3)
 
class Robot(Lop):
    
    CHAR = '#'
    
    def __init__(self, board):
        self.board = board
        self.char = self.CHAR
        self.color = curses.color_pair(8) | curses.A_BOLD
        board.placeRandomly(self) 
    def move(self, relX, relY):
        kitten = 0
        tryX = self.x+relX
        tryY = self.y+relY
        something = None
        if self.board.inBounds(tryX, tryY): 
            something = self.board.handleCollision(tryX, tryY, self)
            if not something:
                self.board.move(self, tryX, tryY)
            return isinstance(something, Kitten)
        
class BoardException(Exception):
    pass

class Board:
    
 STATUS_HEIGHT = 3
 
    def trim(self, s):
        """Used to make sure a message fits on the screen."""
        return s[:self.WIDTH]
    def __init__(self, game, scr):
        self.game = game
        self.scr = scr
        self.HEIGHT, self.WIDTH = self.scr.getmaxyx()
        self.HEIGHT = self.HEIGHT-1
        self.WIDTH = self.WIDTH-1
        self.FIELD_HEIGHT = self.HEIGHT-self.STATUS_HEIGHT
        instr = len(self.game.INSTRUCTIONS)
        if self.FIELD_HEIGHT < 1 or self.HEIGHT < instr or self.WIDTH < 79:
            raise BoardException, "Sorry, your screen is too small to play this 
game. (I need at least %sx80)" % max(self.STATUS_HEIGHT+1, instr)
        self.occupied = {} #Map of coordinates to things at the coordinates.
        
    def prepareForPlacement(self, number):
        #Prepares the board for the given number of random placements.
        self.unoccupied = range(0, self.FIELD_HEIGHT * self.WIDTH)
        if number > (self.FIELD_HEIGHT * self.WIDTH):
            raise BoardException, "Sorry, your screen is too small to play a game 
with %s objects." % number

 def splash(self, lines):
     
    color = curses.color_pair(0) | curses.A_BOLD
    for i in range(0, len(lines)):
        a = self.trim(lines[i])
        robot = string.find(a, Robot.CHAR)
        if robot == -1:
            self.scr.addstr(i, 0, a, color)
        else:
            self.scr.addstr(i, 0, a[:robot], color)
            self.scr.addstr(i, robot, Robot.CHAR, curses.color_pair(8) | 
curses.A_BOLD)
        if robot < len(a)-1:
            self.scr.addstr(i, robot+1, a[robot+1:], color)
        self.scr.refresh()
 
    def getch(self):
        return self.scr.getch()

    def gameSetup(self):
        self.top = curses.newwin(self.STATUS_HEIGHT, self.WIDTH+1, 0, 0)
        self.field = curses.newwin(self.FIELD_HEIGHT, self.WIDTH+1, 3, 0)
        self.top.addstr(0, 0, self.trim(self.game.INSTRUCTIONS[0]))
        try:
            self.top.addstr(2, 0, '-' * (self.WIDTH+1))
        except curses.error:
            # The try-catch ignores the error we trigger from some curses
            # versions by trying to write to the edge of the screen.
        pass
    self.top.refresh()
    
    def setMessage(self, message):
        message = self.trim(message)
        self.top.addstr(1,0, str(message))
        if len(message) < self.WIDTH:
            self.top.addstr(1, len(message), ' ' * (self.WIDTH-len(message)))
    self.top.refresh()
    
    def move(self, obj, newX, newY):
        self.occupied[(obj.x, obj.y)] = None
        self.erase(obj)
        obj.x, obj.y = newX, newY
        self.occupied[(obj.x, obj.y)] = obj
        self.draw(obj)
        
    def erase(self, obj, refresh=0, x=None, y=None, where=None):
        if not where:
            where = self.field
        if not x:
            x = obj.x
        if not y:
            y = obj.y
        try:
            where.addch(y, x, ' ') #TODO: Make sure there's no background
        except curses.error:
            # The try-catch ignores the error we trigger from some curses
            # versions by trying to write into the lowest-rightmost spot
            # in the window.
            pass
    def draw(self, obj, refresh=1, x=None, y=None, where=None):
        if not x:
            x = obj.x
        if not y:
            y = obj.y
        if not where:
            where = self.field
        try:
            # The try-catch ignores the error we trigger from some curses
            # versions by trying to write into the lowest-rightmost spot
            # in the window.
            where.addch(y, x, obj.char, obj.color)
        except curses.error:
            pass
        if refresh:
            where.refresh()
    def inBounds(self, x, y):
        return x >= 0 and y >= 0 and x <= self.WIDTH and y < self.FIELD_HEIGHT
    def handleCollision(self, x, y, whoGoesThere):
        there = self.occupied.get((x,y))
        if there:
            there.handleCollision(whoGoesThere)
        return there
    def placeRandomly(self, obj):
 """Positions the given object on a randomly selected empty
 square on the field."""
        x, y = None, None
        coded = random.choice(self.unoccupied)
        x = coded % self.WIDTH
        y = coded / self.WIDTH
        self.unoccupied.remove(coded)
        self.occupied[(x,y)] = obj
        obj.x = x
        obj.y = y
        if isinstance(obj, Lop):
            self.draw(obj, 0)
class Game:
    INSTRUCTIONS = """In this game, you are robot (#). Your job is to find kitten. This task
is complicated by the existance of various things which are not kitten.
Robot must touch items to determine if they are kitten or not. The game
ends when  you may end the game by hitting
the Esc key.
Press any key to start.""".split('\n')
    INSTRUCTIONS.insert(0, NAME + ' ' + VERSION)
    from curses import ascii
    QUIT = [ascii.ESC, ord('q'), ord('Q')]
    REDRAW = ord('L') - 64
    MOVES = {}
    for i in (curses.KEY_HOME, ord('7'), ord('y'), ord('Y')):
        MOVES[i] = (-1, -1)
    for i in (curses.KEY_UP, ord('8'), ord('k'), ord('K'), ord('P')-64):
        MOVES[i] = (0, -1) 
    for i in (curses.KEY_PPAGE, ord('9'), ord('u'), ord('U')):
        MOVES[i] = (1, -1)
    for i in (curses.KEY_LEFT, ord('4'), ord('h'), 'H', ord('B')-64 ):
        MOVES[i] = (-1, 0)
    for i in (curses.KEY_RIGHT, ord('6'), ord('l'), 'L', ord('F')-64):
        MOVES[i] = (1, 0)
    for i in (curses.KEY_END, ord('1'), ord('b'), 'B'):
        MOVES[i] = (-1, 1)
    for i in (curses.KEY_DOWN, ord('2'), ord('j'), ord('J'), ord('N')-64):
        MOVES[i] = (0, 1)
    for i in (curses.KEY_NPAGE, ord('3'), ord('n'), ord('N')):
        MOVES[i] = (1, 1)
    def __init__(self, chooseNKIs, nkis):
        """Note: the list of nkis will get mangled, so if you want to reuse
        it, pass"""
        self.chooseNKIs = chooseNKIs
        self.nkis = nkis
    def splash(self):
        self.board.prepareForPlacement(self.chooseNKIs+2)
        self.board.splash(self.INSTRUCTIONS)
        try:
            self.board.getch()
        except KeyboardInterrupt:
            sys.exit(1)
        def setupBoard(self):
            self.board.gameSetup()
            self.chooseNKIs = min(self.chooseNKIs, len(self.nkis))
            n = []
        for i in range(0, self.chooseNKIs):
            msg = random.choice(self.nkis)
            self.nkis.remove(msg)
            msg = self.BINARY.sub('?', msg)
            nki = NKI(msg, self.board)
            n.append(nki)
            self.robot = Robot(self.board)
            kitten = Kitten(self.board)
            self.board.field.refresh()
        def inputLoop(self):
            ch = None
            kitten = 0
            while not kitten and (not ch or ch not in self.QUIT):
                try: 
                ch = self.board.getch()
            except KeyboardInterrupt:
                ch = self.QUIT[0]
            coord = self.MOVES.get(ch)
            if coord:
                kitten = self.robot.move(coord[0], coord[1])
            elif ch == self.REDRAW:
                for i in 'top', 'field':
                i = getattr(self.board, i)
                i.redrawwin()
                i.refresh()
            elif ch in self.QUIT:
                sys.exit(1)
            else:
                self.board.setMessage('Invalid input: use direction keys, or Esc to
quit.')
            #You found kitten! Way to go, robot!
            sys.exit(0)
 
        def run(self, scr):
            curses.curs_set(0)
            scr.keypad(1)
            for i in range(1,8):
                curses.init_pair(i, i, 0)
            self.board = Board(self, scr)
            self.splash()
            self.setupBoard() 
            self.inputLoop()
