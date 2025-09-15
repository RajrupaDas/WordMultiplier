# Pygame UI to visualize Booth's algorithm using BoothSimulator.

import pygame
import sys
import math
from booth import BoothSimulator
from utils import twos_to_int

pygame.init()
pygame.display.set_caption("Word Multiplier — Booth's Algorithm")

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))

FONT = pygame.font.SysFont("Consolas", 18)
BIGFONT = pygame.font.SysFont("Consolas", 26, bold=True)
CLOCK = pygame.time.Clock()

# UI colors
BG = (18, 18, 30)
CARD = (30, 34, 56)
HIGHLIGHT = (100, 180, 255)
TEXT = (230, 230, 240)
ACCENT = (255, 130, 100)
GREEN = (100, 220, 140)
YELLOW = (240, 220, 100)
PINK = (240, 150, 220)

# Default values
default_bits = 8
default_M = 7
default_Q = -3

# Input boxes (simple)
class InputBox:
    def __init__(self, x, y, w, h, text=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = (200,200,200)
        self.text = str(text)
        self.txt_surface = FONT.render(self.text, True, TEXT)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                # only allow valid characters for signed ints and '-'
                if event.unicode.isdigit() or (event.unicode == '-' and len(self.text)==0):
                    self.text += event.unicode
            self.txt_surface = FONT.render(self.text, True, TEXT)

    def draw(self, surf):
        pygame.draw.rect(surf, CARD, self.rect, border_radius=6)
        surf.blit(self.txt_surface, (self.rect.x+8, self.rect.y+8))
        if self.active:
            pygame.draw.rect(surf, HIGHLIGHT, self.rect, 2, border_radius=6)

    def get_value(self, default=0):
        try:
            return int(self.text)
        except:
            return default

# Simple button
class Button:
    def __init__(self, x,y,w,h,label):
        self.rect = pygame.Rect(x,y,w,h)
        self.label = label
    def draw(self, surf, color=ACCENT):
        pygame.draw.rect(surf, color, self.rect, border_radius=8)
        txt = FONT.render(self.label, True, TEXT)
        surf.blit(txt, (self.rect.centerx - txt.get_width()/2, self.rect.centery - txt.get_height()/2))
    def clicked(self, pos):
        return self.rect.collidepoint(pos)

# Dropdown for bit widths (simple)
class Dropdown:
    def __init__(self, x,y, options, selected_index=0):
        self.rect = pygame.Rect(x,y,120,34)
        self.options = options
        self.selected = selected_index
        self.open = False
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.open = not self.open
            else:
                if self.open:
                    # check options
                    for i,opt in enumerate(self.options):
                        r = pygame.Rect(self.rect.x, self.rect.y + (i+1)*34, self.rect.w, 34)
                        if r.collidepoint(event.pos):
                            self.selected = i
                    self.open = False
    def draw(self, surf):
        pygame.draw.rect(surf, CARD, self.rect, border_radius=6)
        txt = FONT.render(str(self.options[self.selected]) + " bits", True, TEXT)
        surf.blit(txt, (self.rect.x+8, self.rect.y+8))
        if self.open:
            for i,opt in enumerate(self.options):
                r = pygame.Rect(self.rect.x, self.rect.y + (i+1)*34, self.rect.w, 34)
                pygame.draw.rect(surf, CARD, r, border_radius=6)
                txt = FONT.render(str(opt) + " bits", True, TEXT)
                surf.blit(txt, (r.x+8, r.y+8))

# Initialize UI components
input_M = InputBox(40, 60, 140, 36, text=str(default_M))
input_Q = InputBox(200, 60, 140, 36, text=str(default_Q))
dropdown = Dropdown(360, 60, [8, 16, 32], selected_index=0)
btn_reset = Button(520, 60, 100, 36, "Reset")
btn_step = Button(640, 60, 100, 36, "Step")
btn_run = Button(760, 60, 100, 36, "Run")

# Simulator instance
sim = BoothSimulator(default_M, default_Q, default_bits)

def draw_register_card(surf, x, y, label, value_unsigned, bits, accent_color):
    pygame.draw.rect(surf, CARD, (x,y,320,110), border_radius=8)
    title = FONT.render(label + f" ({bits} bits)", True, accent_color)
    surf.blit(title, (x+12,y+10))
    utext = FONT.render("unsigned: " + str(value_unsigned), True, TEXT)
    surf.blit(utext, (x+12,y+40))
    stext = FONT.render("signed: " + str(twos_to_int(value_unsigned, bits)), True, TEXT)
    surf.blit(stext, (x+12,y+70))
    # binary display
    binstr = format(value_unsigned, '0{}b'.format(bits))
    btext = FONT.render(binstr, True, YELLOW)
    surf.blit(btext, (x+170, y+40))

def draw_log(surf, x, y, w, h, steps):
    pygame.draw.rect(surf, CARD, (x,y,w,h), border_radius=8)
    title = FONT.render("Operation Log (latest on top)", True, PINK)
    surf.blit(title, (x+8,y+8))
    # draw last 8 steps
    max_lines = 8
    lines = steps[-max_lines:][::-1]
    for i,step in enumerate(lines):
        txt = f"Step {step['step']:2d}: {step['action']:12s} | A={step['A_signed']:>6} Q={step['Q_signed']:>6} Q-1={step['Q_1']}"
        surf.blit(FONT.render(txt, True, TEXT), (x+8, y+36 + i*20))

def draw_center_visuals():
    # A, Q, Q-1 cards
    draw_register_card(screen, 40, 140, "Register A", sim.A, sim.n, HIGHLIGHT)
    draw_register_card(screen, 380, 140, "Register Q", sim.Q, sim.n, GREEN)
    # Q-1 small card
    pygame.draw.rect(screen, CARD, (720, 140, 200, 110), border_radius=8)
    title = FONT.render("Q-1 (1 bit)", True, PINK)
    screen.blit(title, (728, 150))
    bit = FONT.render(str(sim.Q_1), True, TEXT)
    screen.blit(bit, (728, 190))
    # M card
    draw_register_card(screen, 40, 270, "Register M (Multiplicand)", sim.M, sim.n, ACCENT)
    # product preview
    pygame.draw.rect(screen, CARD, (380, 270, 540, 110), border_radius=8)
    title = FONT.render("Product Preview (A Q)", True, PINK)
    screen.blit(title, (388, 280))
    prod_unsigned = ((sim.A << sim.n) | sim.Q) & ((1 << (2*sim.n)) - 1)
    prod_signed = twos_to_int(prod_unsigned, 2*sim.n)
    screen.blit(FONT.render("unsigned: " + str(prod_unsigned), True, TEXT), (388, 310))
    screen.blit(FONT.render("signed:   " + str(prod_signed), True, TEXT), (388, 340))
    bin_str = format(prod_unsigned, '0{}b'.format(2*sim.n))
    screen.blit(FONT.render(bin_str, True, YELLOW), (720, 310))

def draw_top_inputs():
    # header
    screen.blit(BIGFONT.render("Word Multiplier — Booth's Algorithm (Simulation)", True, TEXT), (28, 8))
    # input labels
    screen.blit(FONT.render("Multiplicand (M)", True, TEXT), (40, 40))
    screen.blit(FONT.render("Multiplier (Q)", True, TEXT), (200, 40))
    input_M.draw(screen)
    input_Q.draw(screen)
    dropdown.draw(screen)
    btn_reset.draw(screen)
    btn_step.draw(screen)
    btn_run.draw(screen)

def main_loop():
    global sim
    running = True
    auto_run = False
    last_step_time = 0
    run_delay_ms = 450  # delay between steps in auto-run

    while running:
        screen.fill(BG)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            input_M.handle_event(event)
            input_Q.handle_event(event)
            dropdown.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_reset.clicked(event.pos):
                    # reset simulator with provided inputs and bits
                    mval = input_M.get_value(default_M)
                    qval = input_Q.get_value(default_Q)
                    bits = dropdown.options[dropdown.selected]
                    sim.reset(multiplicand=mval, multiplier=qval, bits=bits)
                if btn_step.clicked(event.pos):
                    if sim.step_count < sim.n:
                        sim.step()
                if btn_run.clicked(event.pos):
                    # toggle auto_run
                    auto_run = not auto_run

        # If auto_run active, step with delay
        if auto_run:
            now = pygame.time.get_ticks()
            if sim.step_count < sim.n:
                if now - last_step_time >= run_delay_ms:
                    sim.step()
                    last_step_time = now
            else:
                auto_run = False

        # draw UI pieces
        draw_top_inputs()
        draw_center_visuals()
        draw_log(screen, 40, 400, 880, 260, sim.log)
        # footer info
        footer = FONT.render(f"Step: {sim.step_count}/{sim.n}   |  Current Action (last): " + (sim.log[-1]['action'] if sim.log else "—"), True, TEXT)
        screen.blit(footer, (40, 670))

        pygame.display.flip()
        CLOCK.tick(30)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_loop()
e
