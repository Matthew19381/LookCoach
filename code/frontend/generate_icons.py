from PIL import Image
import os

os.makedirs('public/icons', exist_ok=True)

sizes = [
    ('icon-192.png', 192),
    ('icon-512.png', 512),
    ('icon-maskable-192.png', 192),
    ('icon-maskable-512.png', 512),
]

for filename, size in sizes:
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    if 'maskable' in filename:
        margin = size * 0.1
        draw.ellipse([margin, margin, size-margin, size-margin], fill='#111827')
        text = 'LC'
        draw.text((size/2, size/2 - 10), text, fill='#64748b', anchor='mm')
    else:
        text = 'LC'
        draw.text((size/2, size/2), text, fill='#64748b', anchor='mm')
    img.save(f'public/icons/{filename}')
    print(f'Created {filename} ({size}x{size})')

img = Image.new('RGBA', (180, 180), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
draw.text((90, 90), 'LC', fill='#64748b', anchor='mm')
img.save('public/icons/apple-touch-icon.png')
print('Created apple-touch-icon.png (180x180)')

print('All icons generated successfully!')