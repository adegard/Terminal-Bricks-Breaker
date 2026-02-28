#!/usr/bin/env python3
import curses
import time
import random

# ---------- SAFE DRAW ----------
def safe_addstr(scr, y, x, s, color=0):
    h, w = scr.getmaxyx()
    if y < 0 or y >= h:
        return
    if x < 0:
        s = s[-x:]
        x = 0
    if x >= w:
        return
    scr.addstr(y, x, s[:max(0, w - x)], color)

# ---------- LEVELS ----------
def generate_level(level, w):
    bricks = []
    patterns = []

    # Level 1: full rows
    patterns.append(lambda y, x: True)

    # Level 2: checkerboard
    patterns.append(lambda y, x: (x//6 + y) % 2 == 0)

    # Level 3: spaced blocks
    patterns.append(lambda y, x: (x//12) % 2 == 0)

    # Level 4: pyramid
    patterns.append(lambda y, x: abs((w//2) - x) < (y * 3))

    # Level 5: zigzag
    patterns.append(lambda y, x: ((x//6) + (y//2)) % 2 == 0)

    pattern = patterns[(level - 1) % len(patterns)]

    for by in range(3, 10):
        for bx in range(4, w - 4, 6):
            if pattern(by, bx):
                bricks.append((by, bx))

    return bricks

# ---------- MAIN GAME ----------
def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(40)

    curses.start_color()
    curses.use_default_colors()

    # Neon palette
    curses.init_pair(1, curses.COLOR_MAGENTA, -1)
    curses.init_pair(2, curses.COLOR_CYAN, -1)
    curses.init_pair(3, curses.COLOR_GREEN, -1)
    curses.init_pair(4, curses.COLOR_YELLOW, -1)
    curses.init_pair(5, curses.COLOR_WHITE, -1)

    h, w = stdscr.getmaxyx()

    lives = 3
    level = 1
    score = 0

    while True:
        # Setup paddle
        paddle_w = 12
        paddle_x = w//2 - paddle_w//2
        paddle_y = h - 2

        # Setup ball
        ball_x = w//2
        ball_y = h//2
        vel_x = random.choice([-1, 1])
        vel_y = -1

        # Load level
        bricks = generate_level(level, w)

        # ---------- LEVEL LOOP ----------
        while True:
            h, w = stdscr.getmaxyx()
            stdscr.clear()

            # HUD
            safe_addstr(stdscr, 0, 2, f"Vite: {lives}", curses.color_pair(3))
            safe_addstr(stdscr, 0, w//2 - 5, f"Livello {level}", curses.color_pair(3))
            safe_addstr(stdscr, 0, w - 15, f"Punti: {score}", curses.color_pair(3))

            # Draw bricks
            for (by, bx) in bricks:
                color = curses.color_pair(random.choice([1,2,3]))
                safe_addstr(stdscr, by, bx, "#", color)

            # Draw paddle
            safe_addstr(stdscr, paddle_y, paddle_x, "=" * paddle_w, curses.color_pair(4))

            # Draw ball
            safe_addstr(stdscr, ball_y, ball_x, "O", curses.color_pair(5))

            # Input
            key = stdscr.getch()
            if key == ord('q'):
                return
            if key in (curses.KEY_LEFT, 260):
                paddle_x = max(0, paddle_x - 2)
            if key in (curses.KEY_RIGHT, 261):
                paddle_x = min(w - paddle_w, paddle_x + 2)

            # Move ball
            ball_x += vel_x
            ball_y += vel_y

            # Wall collisions
            if ball_x <= 0 or ball_x >= w - 1:
                vel_x *= -1
            if ball_y <= 1:
                vel_y *= -1

            # Paddle collision
            if ball_y == paddle_y - 1 and paddle_x <= ball_x <= paddle_x + paddle_w:
                vel_y *= -1

            # Brick collision
            hit = None
            for b in bricks:
                if (ball_y, ball_x) == b:
                    hit = b
                    vel_y *= -1
                    score += 10
                    break
            if hit:
                bricks.remove(hit)

            # Lose life
            if ball_y >= h - 1:
                lives -= 1
                if lives == 0:
                    safe_addstr(stdscr, h//2, w//2 - 5, "GAME OVER", curses.color_pair(1))
                    stdscr.refresh()
                    time.sleep(2)
                    return
                break  # restart level

            # Win level
            if not bricks:
                level += 1
                safe_addstr(stdscr, h//2, w//2 - 6, "LIVELLO SUPERATO!", curses.color_pair(2))
                stdscr.refresh()
                time.sleep(1.5)
                break

            stdscr.refresh()
            time.sleep(0.03)

curses.wrapper(main)
