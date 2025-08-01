import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# === Settings ===
url = "https://smart-healthcare-wbkh.onrender.com"  # Your Render URL
label = "Scan to access our Smart Healthcare System"
output_file = "smart_healthcare_qr_pop.png"
logo_path = "healthcare_logo.png"  # Your logo file

# === Generate QR Code ===
qr = qrcode.QRCode(box_size=10, border=4)
qr.add_data(url)
qr.make(fit=True)
qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

qr_width, qr_height = qr_img.size

# === Setup font ===
font_path = "arial.ttf"
font_size = 28
try:
    font = ImageFont.truetype(font_path, font_size)
except:
    font = ImageFont.load_default()

# === Text wrapping function ===
def wrap_text(text, font, max_width):
    lines = []
    words = text.split()
    line = ""
    for word in words:
        test_line = f"{line} {word}".strip()
        bbox = font.getbbox(test_line)
        width = bbox[2] - bbox[0]
        if width <= max_width:
            line = test_line
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines

max_text_width = qr_width - 40  # more padding for style
lines = wrap_text(label, font, max_text_width)

line_height = (font.getbbox("Ay")[3] - font.getbbox("Ay")[1]) + 8
label_height = line_height * len(lines)
total_height = qr_height + label_height + 40  # extra space for glow effect

# === Create gradient background ===
def gradient(width, height, start_color, end_color):
    base = Image.new('RGB', (width, height), start_color)
    top = Image.new('RGB', (width, height), end_color)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(255 * (y / height))] * width)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

bg_img = gradient(qr_width + 80, total_height + 80, (255, 230, 230), (255, 150, 180))

# === Create new image with rounded rectangle container ===
container_width, container_height = qr_width + 60, total_height + 60
container = Image.new('RGBA', (container_width, container_height), (255, 255, 255, 255))

# Rounded corners mask
def rounded_rectangle_mask(size, radius):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0,0,size[0],size[1]], radius=radius, fill=255)
    return mask

mask = rounded_rectangle_mask(container.size, 30)
container.putalpha(mask)

# Drop shadow for container
shadow = Image.new("RGBA", (container_width + 20, container_height + 20), (0,0,0,0))
shadow_draw = ImageDraw.Draw(shadow)
shadow_draw.rounded_rectangle([10,10,container_width+10,container_height+10], radius=30, fill=(0,0,0,120))
shadow = shadow.filter(ImageFilter.GaussianBlur(10))

# Compose final canvas
final_width = bg_img.width
final_height = bg_img.height
final_img = Image.new('RGBA', (final_width, final_height), (0,0,0,0))
final_img.paste(bg_img, (0,0))

# Paste shadow and container centered
container_pos = ((final_width - container_width)//2, (final_height - container_height)//2)
shadow_pos = (container_pos[0]-10, container_pos[1]-10)
final_img.paste(shadow, shadow_pos, shadow)
final_img.paste(container, container_pos, container)

draw = ImageDraw.Draw(final_img)

# Paste QR code onto container (centered with some padding)
qr_pos = (container_pos[0] + 30, container_pos[1] + 30)
final_img.paste(qr_img, qr_pos, qr_img)

# Draw wrapped label text below QR with vibrant color & shadow
text_y = qr_pos[1] + qr_height + 20
for line in lines:
    bbox = font.getbbox(line)
    line_width = bbox[2] - bbox[0]
    text_x = container_pos[0] + (container_width - line_width)//2

    # Shadow for text
    shadow_offset = 2
    draw.text((text_x + shadow_offset, text_y + shadow_offset), line, font=font, fill=(80, 0, 60, 180))
    # Main text
    draw.text((text_x, text_y), line, font=font, fill=(230, 20, 80, 255))

    text_y += line_height

# === Add glowing logo overlay ===
try:
    logo = Image.open(logo_path).convert("RGBA")
    logo_size = qr_width // 5
    logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

    # Create glow effect around logo
    glow = Image.new("RGBA", (logo_size+40, logo_size+40), (255, 0, 120, 0))
    glow_draw = ImageDraw.Draw(glow)
    for i in range(20, 0, -1):
        alpha = int(12 * i)
        glow_draw.ellipse(
            [20 - i*2, 20 - i*2, 20 + logo_size + i*2, 20 + logo_size + i*2],
            fill=(255, 0, 120, alpha)
        )
    glow_pos = (qr_pos[0] + (qr_width - logo_size)//2 - 20, qr_pos[1] + (qr_height - logo_size)//2 - 20)
    final_img.paste(glow, glow_pos, glow)
    final_img.paste(logo, (glow_pos[0]+20, glow_pos[1]+20), logo)

except FileNotFoundError:
    print(f"⚠️ Logo file '{logo_path}' not found, skipping glow effect.")

# Save and show
final_img = final_img.convert("RGB")  # remove alpha for saving as PNG
final_img.save(output_file)
final_img.show()

print(f"✨ QR code saved with POP effect as {output_file}")
