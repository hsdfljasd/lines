from tkinter import *
from random import *
import math

root = Tk()
root.title("Игра в линии")

#Константные параметры
W, H = 700, 700
num_points = 14
line_thickness = 3
point_rad = 5
spawn_rad = W / 2
tool_frame_height = 80
point_color = "black"
pt_active_color = "red"
user_color = "yellow"
ai_color = "blue"
collision_color = "red"

#Устанавливаем размеры окна
root.geometry("{}x{}".format(str(W), str(H + tool_frame_height)))

#Создаём панель инструментов и холст
tool_frame = Frame(root, bg = 'grey')
tool_frame.place(x = 0, y = 0, width = W, height = tool_frame_height)
canv = Canvas(root, bg = 'white')
canv.place(x = 0, y = tool_frame_height, width = W, height = H)

description = """На каждом ходу игроки поочерёдно соединяют две точки линией.
При этом нельзя использовать уже занятые точки и нельзя
допускать пересечения с уже нарисованными линиями.
Проигрывает тот, кто не может сделать свой ход.
"""

def show_info():
    top = Toplevel(root)
    top.title("Справка")
    Label(top, text = "Игра \"в линии\"", font = ("Times New Roman", 28)).pack()
    Label(top, text = description, font = ("Times New Roman", 16)).pack()

#Генерация точек
def get_coords(k, n):
    angle = uniform(0, 2 * math.pi)
    a = k / n * spawn_rad
    radius = uniform(a, a + spawn_rad / n)
    x = radius * math.cos(angle) + W / 2
    y = radius * math.sin(angle) + H / 2
    return x, y

points = []
for i in range(num_points):
    x, y = get_coords(i, num_points)
    point = canv.create_oval(x - point_rad, y - point_rad, x + point_rad, y + point_rad, fill=point_color)
    points.append(point)

#Создаём кнопки на панели инструментов
def restart():
    global lines, line_coords, taken_points, x1, y1, x2, y2, active_point, line, collision, points
    canv.delete("all")
    points = []
    for i in range(num_points):
        x, y = get_coords(i, num_points)
        point = canv.create_oval(x - point_rad, y - point_rad, x + point_rad, y + point_rad, fill=point_color)
        points.append(point)
    lab['text'] = ''
    x1, y1 = -1, -1
    x2, y2 = -1, -1
    active_point = None
    line = None
    taken_points = []
    lines = []
    line_coords = []
    collision = False

btn_q = Button(tool_frame, text = "?", font = ("Times New Roman", 28), command = show_info)
btn_q.place(width = 60, height = 60, x = 10, y = 10)
btn_restart = Button(tool_frame, text = "Заново", font = ("Times New Roman", 28), command = restart)
btn_restart.place(height = 60, x = 80, y = 10)

lab = Label(tool_frame, text = "", font = ("Times New Roman", 28), bg = 'grey')
lab.place(height = 60, x = 300, y = 10)

#Переменные параметры
x1, y1 = -1, -1 #Координаты первой выбранной точки
x2, y2 = -1, -1 #Координаты второй выбранной точки
active_point = None
line = None
taken_points = []
lines = []
line_coords = []
collision = False

def get_covered_point(mouse_x, mouse_y):
    for i in range(num_points):
        x1, y1, x2, y2 = canv.coords(points[i])
        x0 = x1 + point_rad
        y0 = y1 + point_rad
        x = mouse_x - x0
        y = mouse_y - y0
        if x**2 + y**2 <= point_rad**2:
            return points[i]
    return None

def mouse_move(e):
    global active_point, line, collision
    if lab['text'] != "":
        return
    point = get_covered_point(e.x, e.y)
    if point is not None:
        if taken_points.count(point) > 0 and line is not None and point != active_point:
            canv.itemconfig(line, fill = collision_color)
            collision = True
            return
        else:
            canv.itemconfig(line, fill = user_color)
            collision = False
        canv.itemconfig(point, fill = pt_active_color)
        active_point = point
    else:
        if active_point is not None:
            canv.itemconfig(active_point, fill = point_color)
            active_point = None
    if x1 != -1:
        if line is None:
            line = canv.create_line(x1, y1, e.x, e.y, fill = user_color, width = line_thickness)
        else:
            canv.coords(line, x1, y1, e.x, e.y)
        if check_all_intersections(x1, y1, e.x, e.y):
            canv.itemconfig(line, fill = collision_color)
            collision = True
        else:
            canv.itemconfig(line, fill = user_color)
            collision = False

def mouse_click(e):
    global x1, y1, x2, y2, line, active_point, taken_points, line_coords
    if lab['text'] != "":
        return
    if active_point is not None and not collision:
        if x1 == -1:
            a, b, c, d = canv.coords(active_point)
            x1 = a + point_rad
            y1 = b + point_rad
            taken_points.append(active_point)
        else:
            a, b, c, d = canv.coords(active_point)
            x2, y2 = a + point_rad, b + point_rad
            if active_point == taken_points[-1]:
                canv.delete(line)
                line = None
                x1, y1 = -1, -1
                if len(taken_points) % 2 == 1:
                    taken_points = taken_points[:-1]
            else:
                taken_points.append(active_point)
                canv.coords(line, x1, y1, x2, y2)
                lines.append(line)
                line_coords.append(tuple(canv.coords(line)))
                line = None
                active_point = None
                x1, y1 = -1, -1
                x2, y2 = -1, -1
                if not is_where_move():
                    lab['text'] = "Вы выиграли!"
                    return
                move = search_best_move()
                line_coords.append(move)
                for i in range(num_points):
                    a, b, c, d = canv.coords(points[i])
                    x, y = a + point_rad, b + point_rad
                    if x == move[0] and y == move[1] or x == move[2] and y == move[3]:
                        taken_points.append(points[i])
                canv.create_line(*move, fill = ai_color, width = line_thickness)
                if not is_where_move():
                    lab['text'] = "Вы проиграли"
    else:
        if len(taken_points) % 2 == 1:
            taken_points = taken_points[:-1]
        canv.delete(line)
        line = None
        x1, y1 = -1, -1

def check_line_intersection(x1, y1, x2, y2, x3, y3, x4, y4):
    denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denominator == 0:
        return False
    numerator_t = (x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)
    numerator_u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3))
    t = numerator_t / denominator
    u = numerator_u / denominator
    if 0 <= t <= 1 and 0 <= u <= 1:
        return True
    return False

def check_all_intersections(x1, y1, x2, y2):
    for tpl in line_coords:
        if check_line_intersection(x1, y1, x2, y2, *tpl):
            return True
    return False

def minimax(N, maximize):
    global coords, line_coords, bestMove
    score = 0
    bm = None
    if maximize:
        if N < 2:
            return -1
        for i in range(N):
            for j in range(i + 1, N):
                line = coords[i] + coords[j]
                if check_all_intersections(*line):
                    continue
                coords.remove(line[:2])
                coords.remove(line[2:])
                line_coords.append(line)
                res = minimax(N-2, False)
                line_coords.remove(line)
                coords.append(line[:2])
                coords.append(line[2:])
                if bm is None:
                    bm = line
                if res > score:
                    score = res
                    if bestMove is None:
                        bm = line
        if score == 0:
            score = -1
        if bestMove is None:
            bestMove = bm
    else:
        if N < 2:
            return 1
        for i in range(N):
            for j in range(i + 1, N):
                line = coords[i] + coords[j]
                if check_all_intersections(*line):
                    continue
                coords.remove(line[:2])
                coords.remove(line[2:])
                line_coords.append(line)
                res = minimax(N-2, True)
                line_coords.remove(line)
                coords.append(line[:2])
                coords.append(line[2:])
                if res < score:
                    score = res
        if score == 0:
            score = 1
    return score

def search_best_move():
    global coords, bestMove
    bestMove = None
    free_points = [p for p in points if taken_points.count(p) == 0]
    coords = []
    for p in free_points:
        x1, y1, x2, y2 = canv.coords(p)
        x = x1 + point_rad
        y = y1 + point_rad
        coords.append((x, y))
    N = len(free_points)
    res = minimax(N, True)
    return bestMove

def is_where_move():
    free_points = [p for p in points if taken_points.count(p) == 0]
    coords = []
    for p in free_points:
        x1, y1, x2, y2 = canv.coords(p)
        x = x1 + point_rad
        y = y1 + point_rad
        coords.append((x, y))
    N = len(coords)
    for i in range(N):
        for j in range(i + 1, N):
            line = coords[i] + coords[j]
            if check_all_intersections(*line):
                continue
            return True
    return False

canv.bind("<Motion>", mouse_move)
canv.bind("<Button-1>", mouse_click)

root.mainloop()
