import sys
import configparser
from svgpathtools import svg2paths2
import numpy as np

def load_config(config_file='config.ini'):
    config = configparser.ConfigParser()
    config.read(config_file)
    settings = config['Settings']
    PEN_UP_Z = float(settings.get('PEN_UP_Z', 5.0))
    PEN_DOWN_Z = float(settings.get('PEN_DOWN_Z', 0.0))
    X_OFFSET = float(settings.get('X_OFFSET', 0.0))
    Y_OFFSET = float(settings.get('Y_OFFSET', 0.0))
    Z_OFFSET = float(settings.get('Z_OFFSET', 0.0))
    FEED_RATE = float(settings.get('FEED_RATE', 1500))
    BED_WIDTH = float(settings.get('BED_WIDTH', 220.0))
    BED_HEIGHT = float(settings.get('BED_HEIGHT', 220.0))
    return PEN_UP_Z, PEN_DOWN_Z, X_OFFSET, Y_OFFSET, Z_OFFSET, FEED_RATE, BED_WIDTH, BED_HEIGHT

def extract_points_from_path(path, num_samples=100):
    points = []
    length = path.length(error=1e-5)
    if length == 0:
        return points
    for t in np.linspace(0, 1, num_samples):
        point = path.point(t)
        points.append((point.real, point.imag))
    return points

def svg_to_gcode(svg_file, gcode_file):
    PEN_UP_Z, PEN_DOWN_Z, X_OFFSET, Y_OFFSET, Z_OFFSET, FEED_RATE, BED_WIDTH, BED_HEIGHT = load_config()

    paths, attributes, svg_attributes = svg2paths2(svg_file)

    # Get SVG dimensions
    svg_width = svg_height = None
    if 'width' in svg_attributes and 'height' in svg_attributes:
        svg_width = float(svg_attributes['width'].replace('mm', ''))
        svg_height = float(svg_attributes['height'].replace('mm', ''))
    else:
        print("SVG dimensions not specified. Using default values.")
        svg_width = BED_WIDTH
        svg_height = BED_HEIGHT

    # Calculate scaling factors
    scale_x = BED_WIDTH / svg_width
    scale_y = BED_HEIGHT / svg_height
    scale_factor = min(scale_x, scale_y)

    # Calculate offsets to center the drawing
    total_x_offset = X_OFFSET + (BED_WIDTH - (svg_width * scale_factor)) / 2
    total_y_offset = Y_OFFSET + (BED_HEIGHT - (svg_height * scale_factor)) / 2

    with open(gcode_file, 'w') as f:
        f.write('; Generated by svg_to_gcode.py\n')
        f.write('G21 ; Set units to millimeters\n')
        f.write('G90 ; Use absolute coordinates\n')
        f.write('G1 Z{:.2f} F{:.0f}\n'.format(PEN_UP_Z + Z_OFFSET, FEED_RATE))  # Pen up

        for path in paths:
            points = extract_points_from_path(path)
            if not points:
                continue

            # Apply scaling and offsets
            points = [((x * scale_factor) + total_x_offset, (y * scale_factor) + total_y_offset) for x, y in points]

            # Move to the starting point
            x0, y0 = points[0]
            f.write('G1 X{:.3f} Y{:.3f} F{:.0f}\n'.format(x0, y0, FEED_RATE))
            f.write('G1 Z{:.2f} F{:.0f}\n'.format(PEN_DOWN_Z + Z_OFFSET, FEED_RATE))  # Pen down

            # Draw the path
            for x, y in points[1:]:
                f.write('G1 X{:.3f} Y{:.3f} F{:.0f}\n'.format(x, y, FEED_RATE))

            # Pen up after finishing the path
            f.write('G1 Z{:.2f} F{:.0f}\n'.format(PEN_UP_Z + Z_OFFSET, FEED_RATE))  # Pen up

    print(f'G-code successfully written to {gcode_file}')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python svg_to_gcode.py input.svg output.gcode')
    else:
        svg_file = sys.argv[1]
        gcode_file = sys.argv[2]
        svg_to_gcode(svg_file, gcode_file)
