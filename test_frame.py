"""Draw one 1920x1080 test frame and save it as test.png."""
import skia

WIDTH, HEIGHT = 1920, 1080

surface = skia.Surface(WIDTH, HEIGHT)
with surface as canvas:
    # Dark background
    canvas.clear(skia.Color(18, 20, 30))

    # Pale circle in the middle
    circle = skia.Paint(Color=skia.Color(235, 228, 210), AntiAlias=True)
    canvas.drawCircle(WIDTH / 2, HEIGHT / 2, 300, circle)

    # The word "hello", centered on the circle
    font = skia.Font(skia.Typeface('DejaVu Sans', skia.FontStyle.Bold()), 140)
    text = skia.Paint(Color=skia.Color(18, 20, 30), AntiAlias=True)
    word = "hello"
    text_width = font.measureText(word)
    canvas.drawString(word, (WIDTH - text_width) / 2, HEIGHT / 2 + 50, font, text)

surface.makeImageSnapshot().save('test.png', skia.kPNG)
print("Saved test.png")
