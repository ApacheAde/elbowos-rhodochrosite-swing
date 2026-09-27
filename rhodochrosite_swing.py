#!/usr/bin/env python3
"""Rhodochrosite Swing — neon grappling-swing arcade for ElbowOS."""
from __future__ import annotations

import math
import os
import random
import subprocess
import sys

os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

W, H = 1080, 1920
FPS = 30
TITLE = "RHODOCHROSITE SWING"
HANDLE = "x.com/ElbowOS"
OUT = "/home/workdir/artifacts/rhodochrosite_swing_ElbowOS.mp4"

BG = (14, 4, 20)
ROSE = (255, 72, 132)
PINK = (255, 158, 196)
MINT = (80, 255, 210)
GOLD = (255, 214, 96)
WHITE = (246, 240, 255)
PLUM = (56, 18, 52)
INK = (24, 8, 30)


def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


class Spark:
    def __init__(self, x, y, col):
        self.bits = []
        for _ in range(14):
            a = random.uniform(0, math.tau)
            s = random.uniform(3, 13)
            self.bits.append([x, y, math.cos(a) * s, math.sin(a) * s, col, 16])

    def tick(self):
        live = []
        for b in self.bits:
            b[0] += b[2]
            b[1] += b[3]
            b[3] += 0.35
            b[5] -= 1
            if b[5] > 0:
                live.append(b)
        self.bits = live

    def draw(self, s, cam):
        for x, y, _, _, col, life in self.bits:
            pygame.draw.circle(s, col, (int(x), int(y - cam)), max(2, life // 4))


class Game:
    def __init__(self):
        self.score = 0
        self.combo = 0
        self.px, self.py = W * 0.5, 1500.0
        self.vx, self.vy = 0.0, 0.0
        self.hooked = False
        self.ax = self.ay = 0.0
        self.ang = 0.0
        self.omega = 0.1
        self.len = 240.0
        self.cool = 0
        self.hang = 0
        self.cam = 900.0
        self.anchors = []
        self.shards = []
        self.haz = []
        self.sparks = []
        self.stars = [(random.randrange(W), random.randrange(4000), random.randint(1, 3)) for _ in range(160)]
        self.t = 0
        self.side = 1
        self.next_y = 1680.0
        self._grow(40)
        first = min(self.anchors, key=lambda a: abs(a[1] - (self.py - 220)))
        self.attach(first[0], first[1])

    def _grow(self, n=8):
        for _ in range(n):
            x = clamp(W * 0.5 + self.side * random.uniform(150, 310), 160, W - 160)
            y = self.next_y
            self.anchors.append([x, y, random.choice((24, 28, 32))])
            self.shards.append([clamp(x - self.side * 90, 80, W - 80), y + 90, True])
            if random.random() < 0.45:
                self.haz.append([clamp(W * 0.5 - self.side * random.uniform(20, 160), 80, W - 80), y + 50, 16])
            self.next_y -= 240
            self.side *= -1

    def attach(self, ax, ay):
        self.hooked = True
        self.ax, self.ay = ax, ay
        dx, dy = self.px - ax, self.py - ay
        self.len = clamp(math.hypot(dx, dy), 140.0, 300.0)
        if self.len < 8:
            self.len = 220.0
            self.px, self.py = ax, ay + 220
            dx, dy = 0.0, 220.0
        self.ang = math.atan2(dy, dx)
        self.omega = 0.085 if self.px <= ax else -0.085
        self.cool = 6
        self.hang = 0

    def release(self):
        if not self.hooked:
            return
        self.hooked = False
        tx, ty = -math.sin(self.ang), math.cos(self.ang)
        spd = self.omega * self.len
        self.vx = tx * spd * 1.05
        self.vy = ty * spd * 1.05 - 4
        self.cool = 4
        self.hang = 0

    def pick_anchor(self):
        best, bd = None, 1e12
        for a in self.anchors:
            d = math.hypot(a[0] - self.px, a[1] - self.py)
            bias = 0 if a[1] < self.py - 30 else 180
            score = d + bias
            if 90 < d < 520 and score < bd:
                best, bd = a, score
        if best is None and self.anchors:
            best = min(self.anchors, key=lambda a: math.hypot(a[0] - self.px, a[1] - self.py))
        return best

    def autoplay(self):
        self.hang += 1
        if self.hooked:
            high = self.py < self.ay + 40
            outward = (self.omega < -0.02 and self.ang < -0.25) or (self.omega > 0.02 and self.ang > 0.25)
            if self.hang > 18 and (high or outward or self.hang > 36):
                self.release()
        elif self.cool == 0 or self.hang > 10:
            nxt = self.pick_anchor()
            if nxt:
                self.attach(nxt[0], nxt[1])
            else:
                self.vy -= 1.0

    def tick(self, keys=None, auto=False):
        self.t += 1
        if self.next_y > self.py - 2200:
            self._grow(10)
        if auto:
            self.autoplay()
        elif keys is not None:
            if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.cool == 0:
                if self.hooked:
                    self.release()
                else:
                    nxt = self.pick_anchor()
                    if nxt:
                        self.attach(nxt[0], nxt[1])
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                if self.hooked:
                    self.omega -= 0.005
                else:
                    self.vx -= 0.7
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                if self.hooked:
                    self.omega += 0.005
                else:
                    self.vx += 0.7
        if self.cool:
            self.cool -= 1
        if self.hooked:
            self.omega += math.sin(self.ang) * -0.0052
            self.omega *= 0.999
            self.ang += self.omega
            self.px = self.ax + math.cos(self.ang) * self.len
            self.py = self.ay + math.sin(self.ang) * self.len
        else:
            self.vy += 0.62
            self.vx *= 0.994
            self.px += self.vx
            self.py += self.vy
        self.px = clamp(self.px, 70, W - 70)
        if self.py > self.cam + H - 60:
            self.py = self.cam + H - 160
            nxt = self.pick_anchor()
            if nxt:
                self.attach(nxt[0], nxt[1])
        want = self.py - H * 0.52
        self.cam += (want - self.cam) * 0.16
        for sh in self.shards:
            if not sh[2]:
                continue
            if (sh[0] - self.px) ** 2 + (sh[1] - self.py) ** 2 < 48 * 48:
                sh[2] = False
                self.combo += 1
                self.score += 90 + self.combo * 14
                self.sparks.append(Spark(sh[0], sh[1], MINT))
        for hz in self.haz:
            if (hz[0] - self.px) ** 2 + (hz[1] - self.py) ** 2 < (hz[2] + 16) ** 2:
                self.combo = 0
                self.sparks.append(Spark(self.px, self.py, GOLD))
                self.vx = -self.vx * 0.5
                self.vy = -12
                if self.hooked:
                    self.release()
        for sp in self.sparks:
            sp.tick()
        self.sparks = [sp for sp in self.sparks if sp.bits]
        if self.t % 30 == 0:
            self.score += 4

    def draw(self, s, font, big, tiny):
        s.fill(BG)
        cam = self.cam
        for x, y, r in self.stars:
            yy = int((y - cam * 0.32) % (H + 30))
            pygame.draw.circle(s, (58, 20, 54), (x, yy), r)
        for i in range(16):
            yy = int((i * 150 - cam * 0.75) % (H + 150) - 40)
            pygame.draw.polygon(s, INK, [(0, yy), (78 + (i % 4) * 14, yy + 75), (0, yy + 150)])
            pygame.draw.polygon(s, INK, [(W, yy), (W - 78 - (i % 4) * 14, yy + 75), (W, yy + 150)])
            pygame.draw.line(s, PLUM, (0, yy + 75), (60, yy + 75), 3)
            pygame.draw.line(s, PLUM, (W, yy + 75), (W - 60, yy + 75), 3)
        for ax, ay, r in self.anchors:
            sy = int(ay - cam)
            if sy < -70 or sy > H + 70:
                continue
            pygame.draw.circle(s, (110, 24, 60), (int(ax), sy), r + 12)
            pygame.draw.circle(s, ROSE, (int(ax), sy), r)
            pygame.draw.circle(s, PINK, (int(ax), sy), max(6, r - 10))
            pygame.draw.circle(s, WHITE, (int(ax) - 5, sy - 5), 4)
        for hx, hy, r in self.haz:
            sy = int(hy - cam)
            if -40 < sy < H + 40:
                pygame.draw.circle(s, (100, 22, 70), (int(hx), sy), r + 7)
                pygame.draw.circle(s, (190, 46, 96), (int(hx), sy), r)
                pygame.draw.line(s, GOLD, (hx - 7, sy - 7), (hx + 7, sy + 7), 3)
                pygame.draw.line(s, GOLD, (hx + 7, sy - 7), (hx - 7, sy + 7), 3)
        for sx, sy, live in self.shards:
            if not live:
                continue
            yy = int(sy - cam)
            if -30 < yy < H + 30:
                pulse = 9 + int(3 * math.sin(self.t * 0.28 + sx * 0.01))
                pygame.draw.circle(s, (20, 90, 70), (int(sx), yy), pulse + 4)
                pygame.draw.circle(s, MINT, (int(sx), yy), pulse)
                pygame.draw.circle(s, WHITE, (int(sx), yy), 4)
        if self.hooked:
            pygame.draw.line(s, ROSE, (self.ax, self.ay - cam), (self.px, self.py - cam), 8)
            pygame.draw.line(s, WHITE, (self.ax, self.ay - cam), (self.px, self.py - cam), 2)
        px, py = int(self.px), int(self.py - cam)
        pygame.draw.circle(s, (90, 18, 50), (px, py), 30)
        pygame.draw.circle(s, ROSE, (px, py), 22)
        pygame.draw.circle(s, PINK, (px - 4, py - 5), 9)
        pygame.draw.circle(s, WHITE, (px - 7, py - 8), 4)
        for sp in self.sparks:
            sp.draw(s, cam)
        banner = pygame.Surface((W, 210), pygame.SRCALPHA)
        banner.fill((14, 4, 20, 215))
        s.blit(banner, (0, 0))
        t = big.render(TITLE, True, PINK)
        s.blit(t, t.get_rect(center=(W // 2, 58)))
        sc = font.render(f"SCORE  {self.score}", True, MINT)
        s.blit(sc, sc.get_rect(center=(W // 2, 118)))
        cmb = tiny.render(f"STREAK  {self.combo}    HOOK  SPACE", True, ROSE)
        s.blit(cmb, cmb.get_rect(center=(W // 2, 168)))
        foot = pygame.Surface((W, 90), pygame.SRCALPHA)
        foot.fill((14, 4, 20, 205))
        s.blit(foot, (0, H - 90))
        h = font.render(HANDLE, True, GOLD)
        s.blit(h, h.get_rect(center=(W // 2, H - 46)))


def overlay_fonts():
    pygame.font.init()
    return (
        pygame.font.SysFont("dejavusans", 42, bold=True),
        pygame.font.SysFont("dejavusans", 52, bold=True),
        pygame.font.SysFont("dejavusans", 28, bold=True),
    )


def play():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    font, big, tiny = overlay_fonts()
    g = Game()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                pygame.quit()
                return
        g.tick(keys=pygame.key.get_pressed(), auto=False)
        g.draw(screen, font, big, tiny)
        pygame.display.flip()
        clock.tick(FPS)


def record():
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    surface = pygame.Surface((W, H))
    font, big, tiny = overlay_fonts()
    g = Game()
    frames = FPS * 15
    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-crf", "20", "-preset", "fast", "-movflags", "+faststart",
        OUT,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for _ in range(frames):
            g.tick(auto=True)
            g.draw(surface, font, big, tiny)
            proc.stdin.write(pygame.image.tostring(surface, "RGB"))
    finally:
        proc.stdin.close()
        rc = proc.wait()
    pygame.quit()
    if rc != 0:
        raise SystemExit(f"ffmpeg failed with {rc}")
    print("wrote", OUT)


def main():
    if "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1":
        record()
    else:
        play()


if __name__ == "__main__":
    main()
