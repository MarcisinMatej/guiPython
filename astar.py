import pygame
import math
from queue import PriorityQueue


# todo move to config
WIDTH=500
# the more rows the smaller cubes
ROWS = 20
WIN=pygame.display.set_mode((WIDTH,WIDTH))

pygame.display.set_caption("A-star pathing algorithm")

# todo move to separate file
RED = (255, 0, 0) # closed color
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255) # default state color
BLACK = (0, 0, 0) # barier color
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

# alternatively it can be node
class Spot():
    def __init__(self, row, col, width, total_rows):
        # we use row, col annotation to move inside the gird of squares
        self.row = row
        self.col = col
        # pygame needs x,y, x+width, y+height location to draw an object
        self.x = row*width
        self.y = col*width
        self.width = width
        self.height = width

        self.color=WHITE
        self.neighbours = []
        self.total_row = total_rows

    def get_pos(self):
        """
        Return column row position
        :return:
        """
        return self.row, self.col

    def is_closed(self):
        """
        If the spot is closed it means, that we have already visited this node
        :return:
        """
        return self.color == RED

    def is_open(self):
        """
        If node is opened we are currently processing it
        :return:
        """
        return self.color == GREEN

    def is_barrier(self):
        """
        Barier node are nodes which cannot be passed through the path
        :return:
        """
        return self.color == BLACK

    def is_start(self):
        """
        Check if the current node is start
        :return:
        """
        return self.color == ORANGE

    def is_end(self):
        """
        Check if node is our target
        :return:
        """
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def set_as_start(self):
        """
        Set color and
        :return:
        """
        self.color = ORANGE

    def make_closed(self):
        if not self.is_end() or self.is_start():
            self.color = RED

    def make_opened(self):
        if not self.is_end() or self.is_start():
            self.color = GREEN

    def make_barrier(self):
        if not self.is_end() or self.is_start():
            self.color = BLACK

    def set_as_goal(self):
        self.color = TURQUOISE

    def make_path(self):
        if not self.is_end() or self.is_start():
            self.color = PURPLE

    def get_rect_position(self)->tuple:
        """
        Returns x_0, y_0 and x+1 and y+1 position of rectangle node as a tupple
        :return:
        """
        return self.x, self.y, self.width, self.height

    def draw(self, win):
        """
        draw node into the window object
        :param win:
        :return:
        """
        pygame.draw.rect(win, self.color, self.get_rect_position())

    def update_neighbours(self,grid):
        """
        Method to identify valid neighbours of the node from current grid.
        This is quite crucial step, as we need to know which nodes are
        bariers / outside of the grid etc..
        :param grid:
        :return:
        """
        self.neighbours = []
        if self.row+1 < self.total_row and not grid[self.row+1][self.col].is_barrier():  # neighbour below
            self.neighbours.append(grid[self.row+1][self.col])

        if self.row-1 > 0 and not grid[self.row-1][self.col].is_barrier():  # neighbour upper
            self.neighbours.append(grid[self.row-1][self.col])

        if self.col+1 < self.total_row and not grid[self.row][self.col+1].is_barrier():  # neighbour right
            self.neighbours.append(grid[self.row][self.col+1])

        if self.col-1 > 0 and not grid[self.row][self.col-1].is_barrier():  # neighbour left
            self.neighbours.append(grid[self.row][self.col-1])

        # TODO add option to move on diagonal

    def __lt__(self, other):
        """
        Comparing spot object by required for using it in sets.
        :param other:
        :return:
        """
        return False


def heuristic(node, goal)->int:
    """
    Heuristic function that estimates the cost of the cheapest path from node to the goal.
    In our case it is simple manhatan distance.
    :param node:
    :param goal:
    :return: Manhatan distance of nodes
    """
    # expand nodes
    x1, y1 = node.get_pos()
    x2, y2 = goal.get_pos()
    # compute
    return abs(x1 - x2) + abs(y1 - y2)


def make_grid(rows, width) -> [Spot]:
    """
    Prepare a list with spots to create square grid of specific number of rows and width.
    Grid is defined as 2D list of spots
    :param rows: Number of rows in the grid
    :param width: Total width of the grid
    :return:
    """
    grid = []
    gap = width // rows

    for i in range(rows):
        # initialize row
        grid.append([])
        for j in range(rows):
            # initialize spots in the row
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)

    return grid


def draw_grid(win, rows, width):
    gap = width // rows
    # first draw grid lines
    for i in range(rows):
        # draw horizontal lines
        pygame.draw.line(win, GREY, (0, i*gap), (width, i*gap))
        # draw verical lines
        pygame.draw.line(win, GREY, (i * gap, 0), (i * gap, width))


def draw(win, grid, rows, width):
    """
    Function to draw every single object on the window,
    not optimal but simplest for the start.
    This will be called at every frame.
    :param win:
    :param grid:
    :param rows:
    :param width:
    :return:
    """
    win.fill(WHITE)
    # draw each rows
    for row in grid:
        for spot in row:
            # TODO simple check if we need to re-draw
            spot.draw(win)

    draw_grid(win,rows,width)
    # refresh pygame screen
    pygame.display.update()


def get_clicked_pos(pos, rows, width):
    """
    Identify spot which was clicked on.
    Basically we need to find the position of mouse on the screen
    in the terms of our grid.
    :param pos: position of click from pygame
    :param rows:
    :param width:
    :return:
    """
    gap = width // rows
    y, x = pos
    row = y // gap
    col = x // gap
    return row, col


def reconstruct_path(came_from_dict, path_node, start, goal):
    # start node does not have entry here,
    while path_node in came_from_dict:
    # while path_node != start:

        path_node = came_from_dict[path_node]
        if path_node != start and path_node != goal:
            path_node.make_path()
    return


def algorithm(update_view_function, grid, start, goal):
    """

    :param update_view_function:
    :param grid:
    :param start:
    :param goal:
    :return:
    """
    count = 0
    open_set = PriorityQueue()
    # todo just remove this non-sense
    open_set_hash = {start}
    open_set.put((0, count, start))
    came_from = {}
    # initialize g score at infinity
    g_score = {spot: math.inf for row in grid for spot in row}
    g_score[start] = 0

    f_score = {spot: math.inf for row in grid for spot in row}
    f_score[start] = heuristic(start, goal)
    update_view_function()

    # todo add additional improvement if end is reachable from the start
    # run algorithm while we have something the open set, possible end is also no path found
    while not open_set.empty():
        for event in pygame.event.get(): # option to end the program
            if event.type == pygame.QUIT:
                pygame.quit()

        current_node = open_set.get()[2]
        open_set_hash.remove(current_node)

        if current_node == goal:  # we found the path
            reconstruct_path(came_from, current_node, start, goal)
            update_view_function()
            return True

        if current_node != start:
            current_node.make_closed()

        # update scores of neighbours for the current node
        # TODO here we can use cost of path, we set it to 1
        temp_g_score = g_score[current_node] + 1
        for neighbour in current_node.neighbours:
            if neighbour.is_closed():
                continue
            if g_score[neighbour] > temp_g_score:  # we found better/cheaper path from current node to neighbour
                g_score[neighbour] = temp_g_score
                f_score[neighbour] = temp_g_score + heuristic(neighbour, goal)
                came_from[neighbour] = current_node
            if neighbour not in open_set_hash:
                count += 1
                neighbour.make_opened()
                open_set.put((f_score[neighbour], count, neighbour))
                open_set_hash.add(neighbour)


        update_view_function()



    return False


def main(win, width):
    # Todo move to config or initial set-up
    grid = make_grid(ROWS, width)

    start = None
    goal = None

    run = True
    algo_running = False

    while run:
        draw(win, grid, ROWS, WIDTH)
        # check all events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # quit by clicking X in top right corner. This must be first!
                run = False
            if algo_running:
                # once the algorithm started we do not want user to interact with the map
                # by this we skip interaction while algorithm is running
                continue

            # TODO move whole mouse processing logic to separate method
            pos = pygame.mouse.get_pos()
            row, col = get_clicked_pos(pos, ROWS, width)
            clicked_spot:Spot = grid[row][col]
            # check which button we pressed
            if pygame.mouse.get_pressed()[0]:  # LEFT button pressed
                if not start and clicked_spot != goal:
                    clicked_spot.set_as_start()
                    start=clicked_spot
                elif not goal and clicked_spot != start:
                    clicked_spot.set_as_goal()
                    goal=clicked_spot
                elif clicked_spot != goal and clicked_spot != start:
                    clicked_spot.make_barrier()

            elif pygame.mouse.get_pressed()[2]:  # Right button pressed
                if clicked_spot == start:
                    start = None
                elif clicked_spot == goal:
                    goal = None
                clicked_spot.reset()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not algo_running:  # start runnign algo
                    algo_running = True
                    # initialize valid neighbours for our nodes
                    for row in grid:
                        for spot in row:
                            spot.update_neighbours(grid)
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, goal)
                if event.key == pygame.K_c:  # RESET THE GRID
                    start = None
                    goal = None
                    grid = make_grid(ROWS, width)

    pygame.quit()

if __name__ == '__main__':
    main(WIN,WIDTH)