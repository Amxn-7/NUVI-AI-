"""
Generate an animated pet.gif from pet.png with cute idle animations:
  - Gentle bounce (up/down)
  - Slight tilt (wobble left/right)
  - Squish (squash & stretch)
Run this once: python generate_pet_gif.py
"""
from PIL import Image, ImageSequence
import math
import os

INPUT = "pet.png"
OUTPUT = "pet.gif"
SIZE = 80                # Final sprite size
FRAMES = 24              # Total animation frames
FRAME_DURATION = 80      # ms per frame

def generate():
    if not os.path.exists(INPUT):
        print(f"Error: {INPUT} not found in current directory.")
        return
    
    base = Image.open(INPUT).convert("RGBA")
    
    frames = []
    for i in range(FRAMES):
        t = i / FRAMES  # 0.0 → 1.0
        angle = math.pi * 2 * t
        
        # Bounce: moves up 3px at peak
        bounce_y = int(-3 * abs(math.sin(angle)))
        
        # Wobble: slight tilt ±3 degrees
        tilt = 3 * math.sin(angle)
        
        # Squish: squash at bottom, stretch at top
        squish = 1.0 + 0.04 * math.sin(angle)  # 0.96 → 1.04
        
        # Start with a transparent canvas slightly larger to allow movement
        canvas_size = SIZE + 10
        frame = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
        
        # Resize base with squish
        new_w = int(SIZE / squish)
        new_h = int(SIZE * squish)
        pet = base.resize((new_w, new_h), Image.LANCZOS)
        
        # Rotate for wobble
        pet = pet.rotate(tilt, resample=Image.BICUBIC, expand=False)
        
        # Center on canvas with bounce offset
        paste_x = (canvas_size - new_w) // 2
        paste_y = (canvas_size - new_h) // 2 + bounce_y
        
        frame.paste(pet, (paste_x, paste_y), pet)
        
        # Convert to P mode with transparency for GIF
        # Use a white background for the GIF palette
        bg = Image.new("RGBA", (canvas_size, canvas_size), (255, 255, 255, 255))
        composite = Image.alpha_composite(bg, frame)
        composite = composite.convert("RGB")
        frames.append(composite)
    
    # Save as animated GIF
    frames[0].save(
        OUTPUT,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_DURATION,
        loop=0,  # Loop forever
        optimize=True,
    )
    print(f"✅ Created {OUTPUT} ({FRAMES} frames, {FRAME_DURATION}ms each)")
    print(f"   Size: {os.path.getsize(OUTPUT) / 1024:.1f} KB")

if __name__ == "__main__":
    generate()
