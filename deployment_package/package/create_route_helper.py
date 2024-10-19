import PIL
from PIL import Image, ImageChops, ImageDraw
import requests
import re
import random
from queue import PriorityQueue
import math
import numpy as np  
def trim_image(image):
    box_color = (247, 247, 247)
    def trim(im):
        im = im.crop((0, 0, im.size[0] - 16, im.size[1]))
        im = im.crop((0, 66, im.size[0], im.size[1]))
        bg = Image.new(im.mode, im.size, box_color)
        diff = ImageChops.difference(im, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        if bbox:
            return im.crop(bbox), bbox
    
    image, bbox = trim(image)
    
    return image, bbox

def add_label_markers(image, labels, background_size):

    width, height = image.size
    top_left = None
    for y in range(height):
        for x in range(width):
            if image.getpixel((x, y)) == (247, 247, 247):
                top_left = (x, y)
                break
        if top_left:
            break

    bottom_right = None
    for y in range(height - 1, -1, -1):
        for x in range(width - 1, -1, -1):
            if image.getpixel((x, y)) == (247, 247, 247):
                bottom_right = (x, y)
                break
        if bottom_right:
            break

    oldpoint1 = float(background_size[0][0])
    oldpoint2 = float(background_size[0][1])
    oldpoint3 = float(background_size[2][0])
    oldpoint4 = float(background_size[2][1])

    scale_factor_x = (bottom_right[0] - top_left[0]) / (oldpoint3 - oldpoint1)
    scale_factor_y = (bottom_right[1] - top_left[1]) / (oldpoint4 - oldpoint2)
    offset_x = top_left[0]
    offset_y = top_left[1]

    adjusted_labels = []
    for label in labels:
        x, y = float(label[0]), float(label[1])
        
        adjusted_x = (x - oldpoint1) * scale_factor_x + offset_x + 30
        adjusted_y = (y - oldpoint2) * scale_factor_y + offset_y + 25
        
        adjusted_labels.append((adjusted_x, adjusted_y, label[2], label[3]))
    return image, adjusted_labels

def flood_fill(image, adjusted_labels):
    width, height = image.size
    pixel_data = image.load()

    def get_color(x, y):
        return pixel_data[x, y]

    def set_color(x, y, color):
        pixel_data[x, y] = color

    def get_neighbors(x, y):
        return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]

    visited = set()
    queues = []
    colors = []
    label_positions = []
    label_pixels = {}

    for label in adjusted_labels:
        x, y, _, text = label
        x, y = int(x), int(y)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        queues.append([(x, y)])
        colors.append(color)
        label_positions.append((x, y, text))
        set_color(x, y, color)
        visited.add((x, y))
        label_pixels[text] = [(x, y)]

    while any(queues):
        for i in range(len(queues)):
            if not queues[i]:
                continue

            x, y = queues[i].pop(0)
            color = colors[i]
            label_text = label_positions[i][2]

            for neighbor in get_neighbors(x, y):
                nx, ny = neighbor
                if 0 <= nx < width and 0 <= ny < height:
                    if (nx, ny) not in visited and get_color(nx, ny) == (255, 255, 255) :
                        set_color(nx, ny, color)
                        visited.add((nx, ny))
                        queues[i].append((nx, ny))
                        label_pixels[label_text].append((nx, ny))

    draw = ImageDraw.Draw(image)
    for x, y, text in label_positions:
        bbox = draw.textbbox((x, y), text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        draw.text((x - text_width // 2, y - text_height // 2), text, fill=(0, 0, 0))

    return image, label_pixels

def shopping_order(label_positions, grocery_list):
    entrances = [label for label in label_positions.keys() if 'entrance' in label.lower()]
    if not entrances:
        raise ValueError("No entrance found in the store layout")
    label_list = [label for label in grocery_list if grocery_list[label]]
    start_end = entrances[0]
    
    labels_to_visit = [label for label in label_list if label in label_positions]
    
    current_pos = label_positions[start_end]
    route = [start_end]
    
    while labels_to_visit:
        nearest_label = min(labels_to_visit, 
                            key=lambda x: math.dist(current_pos, label_positions[x]))
        route.append(nearest_label)
        current_pos = label_positions[nearest_label]
        labels_to_visit.remove(nearest_label)
    
    start_end = ["checkout", "entrance"]
    route.extend(start_end)
    
    return route

def label_positions(label_pixels):
    label_positions = {}
    for label, pixels in label_pixels.items():
        avg_x = sum(p[0] for p in pixels) / len(pixels)
        avg_y = sum(p[1] for p in pixels) / len(pixels)
        label_positions[label] = (avg_x, avg_y)
    return label_positions

def adjust_label_positions(label_positions, barriers):
    width, height = barriers.size
    barriers_array = np.array(barriers.convert('L'))
    adjusted_positions = {}

    def find_nearest_non_barrier(x, y):
        for r in range(1, max(width, height)):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    nx, ny = int(x + dx), int(y + dy)
                    if 0 <= nx < width and 0 <= ny < height and barriers_array[ny, nx] == 0:
                        return nx, ny
        return None  

    for label, pos in label_positions.items():
        x, y = int(pos[0]), int(pos[1])
        
        if 0 <= x < width and 0 <= y < height and barriers_array[y, x] == 255:  
            new_pos = find_nearest_non_barrier(x, y)
            if new_pos:
                adjusted_positions[label] = new_pos
            else:
                print(f"Warning: Could not find non-barrier position for label '{label}'. Keeping original position.")
                adjusted_positions[label] = pos
        else:
            adjusted_positions[label] = pos

    return adjusted_positions
def draw_route(image, route, label_positions, barriers, grocery_list):
    draw = ImageDraw.Draw(image)
    width, height = image.size
    
    barriers_array = np.array(barriers.convert('L'))
    

    label_positions = adjust_label_positions(label_positions, barriers)
    
    def heuristic(a, b):
        return math.dist(a, b)
    
    def get_neighbors(x, y):
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and barriers_array[ny, nx] == 0:
                neighbors.append((nx, ny))
        return neighbors
    
    def a_star(start, goal, max_iterations=50000):  
        start = (int(start[0]), int(start[1]))
        goal = (int(goal[0]), int(goal[1]))

        if barriers_array[start[1], start[0]] == 255 or barriers_array[goal[1], goal[0]] == 255:
            print(f"Warning: Start {start} or goal {goal} is in a barrier.")
            return None
        
        frontier = PriorityQueue()
        frontier.put((0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        iterations = 0
        while not frontier.empty() and iterations < max_iterations:
            current = frontier.get()[1]
            
            if current == goal:
                break
            
            for next in get_neighbors(*current):
                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + heuristic(goal, next)
                    frontier.put((priority, next))
                    came_from[next] = current
            
            iterations += 1
        
        if current != goal:
            print(f"Warning: Path not found after {iterations} iterations.")
            return None
        
        path = []
        while current != start:
            path.append(current)
            current = came_from[current]
        path.append(start)
        path.reverse()
        return path
    
    def find_nearest_walkable(point):
        x, y = int(point[0]), int(point[1])
        if 0 <= x < width and 0 <= y < height and barriers_array[y, x] == 0:
            return (x, y)  
        
        for r in range(1, min(width, height)):  
            for i in range(-r, r+1):
                for j in range(-r, r+1):
                    nx, ny = x + i, y + j
                    
                    if 0 <= nx < width and 0 <= ny < height and barriers_array[ny, nx] == 0:
                        return (nx, ny)
        print(f"Warning: No walkable point found near ({x}, {y})")
        return None 
    
    for i in range(len(route) - 1):
        start = label_positions[route[i]]
        end = label_positions[route[i+1]]
        
        
        start = find_nearest_walkable(start) or start
        end = find_nearest_walkable(end) or end
        
        if start is None or end is None:
            print(f"Warning: Could not find walkable points for {route[i]} or {route[i+1]}. Skipping this segment.")
            continue
        
        path = a_star(start, end)
        
        if path is None:
            print(f"Warning: Could not find path between {route[i]} and {route[i+1]}. Drawing direct line.")
            draw.line([start, end], fill="yellow", width=2)
        else:
            
            for j in range(len(path) - 1):
                draw.line([path[j], path[j+1]], fill="red", width=2)
        
        x, y = label_positions[route[i]]

        draw.ellipse([start[0]-5, start[1]-5, start[0]+5, start[1]+5], fill="green")
        draw.ellipse([end[0]-5, end[1]-5, end[0]+5, end[1]+5], fill="blue")
        for item in grocery_list[route[i]]:
            draw.text((x, y), item, fill='black')
            y += 10 
    return image
    
def process_barriers(barriers, bbox=None):
    im = barriers
    im = im.crop((0, 0, im.size[0] - 16, im.size[1]))
    im = im.crop((0, 66, im.size[0], im.size[1]))
    if bbox:
        im = im.crop(bbox)
    barriers = im
    barriers = barriers.convert('RGB')
    pixels = barriers.load()

    for i in range(barriers.size[0]):
        for j in range(barriers.size[1]):
            if pixels[i, j] == ( 224,224,224): 
                pixels[i, j] = (255, 255, 255)  
            else:
                pixels[i, j] = (0, 0, 0) 
    return barriers

def get_html_data(html):
    labels = re.findall(r'<text class="adjacency-name normal-format-store" font-family="Helvetica, Verdana" text-anchor="middle" x="(.+?)" y="(.+?)" font-size="(.+?)">(.+?)</text>', html)
    html_no_whitespace = re.sub(r'\n+', '', html)
    background_size = re.findall(r'id="background" role="group" aria-labelledby="background-vo">(.+?)</g>', html_no_whitespace)[0]
   
    background_size = re.sub(r'[^\d. ]', '', background_size)  
    background_size = background_size.split(" ")
    background_size = [x for x in background_size if x]
    background_size = background_size[:-2]

    background_size = list(zip(background_size[0::2], background_size[1::2]))
    return background_size, labels

