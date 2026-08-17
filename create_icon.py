from PIL import Image
import os

# Теперь ищем логотип в папке src
input_png = "src/logo.png"
output_ico = "app_icon.ico"   # результат по-прежнему сохраняем в КОРЕНЬ проекта

if not os.path.exists(input_png):
    print(f"❌ Ошибка: Файл {input_png} не найден!")
    print("Пожалуйста, положите логотип в папку src и назовите его logo.png")
    exit(1)

img = Image.open(input_png)

if img.mode != "RGBA":
    img = img.convert("RGBA")

sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
icon_images = []

for size in sizes:
    resized = img.resize(size, Image.Resampling.LANCZOS)
    icon_images.append(resized)

icon_images[-1].save(
    output_ico,
    format='ICO',
    sizes=[(im.width, im.height) for im in icon_images]
)

print(f"✅ Иконка успешно создана: {output_ico}")