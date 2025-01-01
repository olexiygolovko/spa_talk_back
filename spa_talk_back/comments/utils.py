import random
import string
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64


def generate_captcha_text(length=6):
    """
    Generates random text from letters and numbers for captcha
    """
    # Use only capital letters and numbers for better readability.
    characters = string.ascii_uppercase + string.digits
    # Exclude similar symbols
    excluded = ['0', 'O', '1', 'I', 'L']
    characters = ''.join(c for c in characters if c not in excluded)
    return ''.join(random.choice(characters) for _ in range(length))


def generate_captcha_image(text):
    """
    Creates a captcha image with the given text
    """
    # Create a blank image
    width = 280
    height = 80
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)

    # Add random noise
    for i in range(1000):
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        draw.point((x, y), fill=random.choice(['#cccccc', '#666666']))

    # Load a font
    try:
        font = ImageFont.truetype('arial.ttf', size=36)
    except:
        try:
            # Try to load a system font
            font = ImageFont.truetype(
                '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', size=36)
        except:
            # if no system font is found, use the default font
            font = ImageFont.load_default()

    # Calculate the position of the text
    text_width = sum(font.getlength(char) for char in text)
    text_height = 36  # Approximate height for font size 36
    x = (width - text_width) / 2
    y = (height - text_height) / 2

    # Draw each character with a random color and position
    for char in text:
        # Random color
        color = (
            random.randint(0, 100),
            random.randint(0, 100),
            random.randint(0, 100)
        )

        # Random position with a slight offset
        char_x = x + random.randint(-5, 5)
        char_y = y + random.randint(-5, 5)

        # Draw the character
        draw.text((char_x, char_y), char, font=font, fill=color)

        # Move the position to the right
        x += font.getlength(char)

    # Add random lines
    for _ in range(4):
        start = (random.randint(0, width), random.randint(0, height))
        end = (random.randint(0, width), random.randint(0, height))
        draw.line([start, end], fill='#666666', width=2)

    # Save the image to a byte stream
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    image_data = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{image_data}"


def validate_captcha(user_input, stored_captcha):
    """
    Проверяет введенную пользователем капчу
    """
    if not user_input or not stored_captcha:
        return False
    # Compare without regard to case
    return user_input.upper() == stored_captcha.upper()
