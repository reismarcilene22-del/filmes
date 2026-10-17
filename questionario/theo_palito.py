import skia, math
W, H = 960, 640
SKIN = (250, 236, 226); HAIR = (248, 248, 252); INK = (22, 18, 30)
JEANS = (95, 120, 160); SHOE = (70, 72, 80); SOLE = (235, 230, 215)
def P(col, a=255): return skia.Paint(Color=skia.Color(*col, a), AntiAlias=True)
def L(col, w): return skia.Paint(Color=skia.Color(*col), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=w, StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join)
def glow(c, x, y, r, col, a=110):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial((x, y), r, [skia.Color(*col, a), skia.Color(*col, 0)])); c.drawCircle(x, y, r, p)
def bg(c, name):
    c.clear(skia.Color(14, 10, 28)); glow(c, 150, 170, 170, (70, 55, 120)); glow(c, 830, 150, 150, (50, 70, 120))
    c.drawRect(skia.Rect(100, 150, 200, 190), L((70, 55, 120), 4)); c.drawLine(0, 590, W, 590, skia.Paint(Color=skia.Color(70, 55, 120), StrokeWidth=3))
    glow(c, 480, 330, 260, (255, 240, 230), 35)
    c.drawString(name, 30, 60, skia.Font(skia.Typeface('DejaVu Sans', skia.FontStyle.Bold()), 36), P((220, 210, 240)))

def lock(x0, y0, x1, y1, w):
    # a soft curved lock of hair: thick at the root, pointed at the tip
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    nx, ny = -(y1 - y0), (x1 - x0); n = math.hypot(nx, ny) or 1; nx, ny = nx / n * w, ny / n * w
    p = skia.Path(); p.moveTo(x0 - nx, y0 - ny)
    p.quadTo(mx - nx * 0.9 + nx * 0.4, my - ny * 0.9 + ny * 0.4, x1, y1)
    p.quadTo(mx + nx * 0.9 + nx * 0.4, my + ny * 0.9 + ny * 0.4, x0 + nx, y0 + ny); p.close(); return p

def hair_path(cx, cy, r):
    # short messy hair: a cap hugging the skull, volume on top, pointed locks over the forehead
    hair = skia.Path(); hair.addOval(skia.Rect(cx - r * 1.04, cy - r * 1.12, cx + r * 1.04, cy + r * 0.2))
    clip = skia.Path(); clip.addRect(skia.Rect(cx - 2 * r, cy - 3 * r, cx + 2 * r, cy - r * 0.32))
    hair = skia.Op(hair, clip, skia.PathOp.kIntersect_PathOp)
    for deg, k, rr in [(-160, 0.9, 0.3), (-130, 1.0, 0.33), (-100, 1.06, 0.34), (-72, 1.04, 0.33), (-45, 0.98, 0.3), (-18, 0.9, 0.26)]:
        a = math.radians(deg); c = skia.Path(); c.addCircle(cx + math.cos(a) * r * k, cy + math.sin(a) * r * k, r * rr)
        hair = skia.Op(hair, c, skia.PathOp.kUnion_PathOp)
    locks = [(0.85, -0.45, 0.62, -0.02, 0.15), (0.5, -0.5, 0.22, -0.1, 0.16), (0.12, -0.5, -0.18, -0.06, 0.16),
             (-0.28, -0.48, -0.6, -0.12, 0.15), (-0.7, -0.4, -1.0, 0.05, 0.13), (0.95, -0.35, 1.06, 0.0, 0.1),
             (-0.15, -1.25, -0.5, -1.5, 0.11), (0.3, -1.3, 0.5, -1.55, 0.09)]
    for (x0, y0, x1, y1, w) in locks:
        hair = skia.Op(hair, lock(cx + x0 * r, cy + y0 * r, cx + x1 * r, cy + y1 * r, w * r), skia.PathOp.kUnion_PathOp)
    return hair

def theo(c, x, ground, shirt, mode="palito", scale=1.0):
    s = scale; r = 62 * s
    hip = (x, ground - 190 * s); neck = (x, ground - 330 * s); head = (x, neck[1] - r + 4 * s)
    limb = 12 * s
    # legs (jeans colour) with little sneakers
    for d in (-1, 1):
        knee = (x + d * 16 * s, ground - 95 * s); foot = (x + d * 26 * s, ground - 14 * s)
        pth = skia.Path(); pth.moveTo(*hip); pth.lineTo(*knee); pth.lineTo(*foot)
        c.drawPath(pth, L(JEANS if mode != "branco" else SKIN, limb))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(foot[0] - 22 * s + d * 8 * s, ground - 22 * s, foot[0] + 22 * s + d * 8 * s, ground), 10 * s, 10 * s), P(SHOE))
        c.drawRect(skia.Rect(foot[0] - 22 * s + d * 8 * s, ground - 7 * s, foot[0] + 22 * s + d * 8 * s, ground), P(SOLE))
    # arms (skin), hanging relaxed
    for d in (-1, 1):
        sh = (x + d * 6 * s, neck[1] + 22 * s); el = (x + d * 40 * s, neck[1] + 95 * s); ha = (x + d * 50 * s, neck[1] + 170 * s)
        pth = skia.Path(); pth.moveTo(*sh); pth.lineTo(*el); pth.lineTo(*ha); c.drawPath(pth, L(SKIN, limb * 0.85))
        c.drawCircle(ha[0], ha[1], 9 * s, P(SKIN))
    # torso: a stick in the shirt colour (or a small shirt shape)
    if mode == "camiseta":
        t = skia.Path(); t.moveTo(x - 22 * s, neck[1] + 8 * s); t.lineTo(x + 22 * s, neck[1] + 8 * s)
        t.lineTo(x + 46 * s, neck[1] + 55 * s); t.lineTo(x + 30 * s, neck[1] + 62 * s); t.lineTo(x + 24 * s, hip[1] + 6 * s)
        t.lineTo(x - 24 * s, hip[1] + 6 * s); t.lineTo(x - 30 * s, neck[1] + 62 * s); t.lineTo(x - 46 * s, neck[1] + 55 * s); t.close()
        c.drawPath(t, P(shirt)); c.drawPath(t, L(INK, 2.5 * s))
    else:
        c.drawLine(neck[0], neck[1], hip[0], hip[1], L(shirt if mode != "branco" else SKIN, limb * 1.6))
    # head
    c.drawCircle(head[0], head[1], r, P(SKIN))
    for d in (-1, 1): c.drawCircle(head[0] + d * r * 0.98, head[1] + 6 * s, 9 * s, P(SKIN))  # ears
    c.drawPath(hair_path(head[0], head[1], r), P(HAIR)); c.drawPath(hair_path(head[0], head[1], r), L((170, 165, 190), 2.5 * s))
    # face: thick brows, round black eyes with a shine, small smile
    for d in (-1, 1):
        ex, ey = head[0] + d * 22 * s, head[1] + 14 * s
        c.drawCircle(ex, ey, 8.5 * s, P(INK)); c.drawCircle(ex + 2.5 * s, ey - 3 * s, 2.6 * s, P((255, 255, 255)))
        b = skia.Path(); b.moveTo(ex - 11 * s, ey - 17 * s); b.quadTo(ex, ey - 22 * s, ex + 11 * s, ey - 17 * s); c.drawPath(b, L(INK, 5 * s))
    m = skia.Path(); m.moveTo(head[0] - 9 * s, head[1] + 38 * s); m.quadTo(head[0], head[1] + 45 * s, head[0] + 9 * s, head[1] + 38 * s)
    c.drawPath(m, L(INK, 2.5 * s))

GREEN = (45, 90, 60); SLATE = (60, 70, 105)
variants = [("A  Palito com camiseta verde", lambda c: theo(c, 480, 590, GREEN, "palito")),
            ("B  Palito com camiseta azul", lambda c: theo(c, 480, 590, SLATE, "palito")),
            ("C  Palito com camiseta desenhada", lambda c: theo(c, 480, 590, GREEN, "camiseta"))]
grid = skia.Surface(W * 3, H)
with grid as g:
    for i, (n, fn) in enumerate(variants):
        s = skia.Surface(W, H)
        with s as c: bg(c, n); fn(c)
        g.drawImage(s.makeImageSnapshot(), i * W, 0); g.drawRect(skia.Rect(i * W, 0, (i + 1) * W, H), L((0, 0, 0), 6))
grid.makeImageSnapshot().save('/home/user/filmes/questionario/3_theo_palito.png', skia.kPNG)
