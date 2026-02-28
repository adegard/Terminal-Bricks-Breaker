#!/usr/bin/env python3
import curses
import time
import random

def safe_addstr(scr, y, x, s):
    h, w = scr.getmaxyx()
    if y < 0 or y >= h:
        return
    if x < 0:
        s = s[-x:]
        x = 0
    if x >= w:
        return
    scr.addstr(y, x, s[:max(0, w - x)])

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(50)

    h, w = stdscr.getmaxyx()

    paddle_w = 10
    paddle_x = max(0, w//2 - paddle_w//2)
    paddle_y = h - 2

    ball_x = w//2
    ball_y = h//2
    vel_x = random.choice([-1, 1])
    vel_y = -1

    bricks = []
    for by in range(3, 8):
        for bx in range(5, w-5, 6):
            bricks.append((by, bx))

    while True:
        h, w = stdscr.getmaxyx()
        stdscr.clear()

        # Draw bricks
        for (by, bx) in bricks:
            safe_addstr(stdscr, by, bx, "#")

        # Draw paddle
        safe_addstr(stdscr, paddle_y, paddle_x, "=" * paddle_w)

        # Draw ball
        safe_addstr(stdscr, ball_y, ball_x, "O")

        # Input
        key = stdscr.getch()
        if key == ord('q'):
            break
        if key in (curses.KEY_LEFT, 260):  # Termux sometimes sends 260
            paddle_x = max(0, paddle_x - 2)
        if key in (curses.KEY_RIGHT, 261): # Termux sometimes sends 261
            paddle_x = min(w - paddle_w, paddle_x + 2)

        # Move ball
        ball_x += vel_x
        ball_y += vel_y

        # Wall collisions
        if ball_x <= 0 or ball_x >= w - 1:
            vel_x *= -1
        if ball_y <= 0:
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
                break
        if hit:
            bricks.remove(hit)

        # Lose
        if ball_y >= h - 1:
            safe_addstr(stdscr, h//2, w//2 - 5, "GAME OVER")
            stdscr.refresh()
            time.sleep(2)
            break

        # Win
        if not bricks:
            safe_addstr(stdscr, h//2, w//2 - 4, "YOU WIN!")
            stdscr.refresh()
            time.sleep(2)
            break

        stdscr.refresh()
        time.sleep(0.03)

curses.wrapper(main)
