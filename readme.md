# SVG to Gcode for pen plotting
This python command line application is designed for the Creality Ender 3 with a pen attachment, to take an SVG and output GCODE that will correctly draw it.

## Creality Ender 3 bed size
220mm x 220mm

## SVG Settings
Make sure to set the width, height, and viewbox of the SVG to the size of the print bed.
```xml
<svg
  width="220mm"
  height="220mm"
  viewBox="0 0 220 220"
  xmlns="http://www.w3.org/2000/svg">
<!-- Your SVG content -->
</svg>
```