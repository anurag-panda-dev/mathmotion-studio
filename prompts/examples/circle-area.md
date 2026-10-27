---
schema_version: "1.0"
lesson:
  title: The Area of a Circle
  topic: Area of a circle
  grade: "7"
  language: English
  duration_minutes: 4
  aspect_ratio: "16:9"
  theme: midnight
objectives:
  - Relate the area of a circle to its radius.
  - Explain where the formula A = πr² comes from.
  - Compute the area of a circle with radius 3.
prerequisites:
  - Squaring numbers
  - The value of π ≈ 3.14159
recap: >-
  The area of a circle is πr². Cutting the circle in half gives the curve
  y = √(r² − x²); the shaded half-area is πr²/2, so the full circle is πr².
practice_questions:
  - What is the area of a circle with radius 5?
  - Doubling the radius multiplies the area by how much?
verification:
  - id: v1
    kind: numeric
    description: A circle of radius 3 has area 9 pi, approximately 28.27.
    expression: pi * 3**2
    expected: 28.274333882308138
---

# The Area of a Circle

Teacher note: scene s3 shows the upper half of a radius-3 circle as the graph
of y = √(9 − x²) with the area beneath it shaded — the visual bridge between
"circle" and "area under a curve". The `fade_in` action is used for the
shaded region.

```scene
id: s1
title: Opening
type: intro
duration: 12
narration: >-
  Every circle, from a coin to a planet, follows one simple rule for its
  area. Today we see where that rule comes from.
objects:
  - id: title
    kind: text
    params:
      content: "The Area of a Circle"
      position: [0, 2]
      font_size: 56
      color: violet
  - id: subtitle
    kind: text
    params:
      content: "Where A = πr² comes from"
      position: [0, 0.8]
      font_size: 34
actions:
  - { action: create, target: title, at: 0 }
  - { action: create, target: subtitle, at: 2 }
  - { action: indicate, target: title, style: pulse, at: 5, duration: 1.5 }
  - { action: wait, at: 8, duration: 2 }
```

```scene
id: s2
title: The radius
type: explanation
duration: 20
narration: >-
  The radius r is the distance from the centre to the edge. Every edge point
  sits exactly r away. The area formula uses nothing but this single length.
objects:
  - id: circ
    kind: circle
    params:
      center: [0, 0]
      radius: 2.5
      color: ivory
      stroke_width: 4
  - id: cpoint
    kind: point
    params:
      position: [0, 0]
      color: amber
      label: "centre"
  - id: rad
    kind: segment
    params:
      start: [0, 0]
      end: [2.5, 0]
      color: violet
      stroke_width: 5
  - id: lbl
    kind: text
    params:
      content: "r"
      position: [1.3, 0.5]
      font_size: 36
      color: violet
  - id: f_area
    kind: formula
    params:
      content: "A = πr²"
      position: [0, 3.2]
      font_size: 48
      color: violet
  - id: note
    kind: text
    params:
      content: "Every edge point is r away from the centre"
      position: [0, -3.4]
      font_size: 30
actions:
  - { action: create, target: circ, at: 0, duration: 2 }
  - { action: create, target: cpoint, at: 2.5, duration: 1 }
  - { action: create, target: rad, at: 4, duration: 1.5 }
  - { action: create, target: lbl, at: 6 }
  - { action: write, target: f_area, at: 8, duration: 2 }
  - { action: create, target: note, at: 11 }
  - { action: indicate, target: rad, at: 13.5, duration: 1.5 }
  - { action: wait, at: 15.5, duration: 2 }
```

```scene
id: s3
title: The circle as a curve
type: explanation
duration: 23
narration: >-
  Cut a radius-3 circle in half. Its upper edge is the curve y equals the
  square root of 9 minus x squared. Shade the region beneath the curve from
  minus 3 to 3 — that shaded area is exactly half of the circle.
objects:
  - id: axes1
    kind: axes
    params:
      x_range: [-4, 4]
      y_range: [-4, 4]
      grid: true
      x_label: x
      y_label: y
  - id: circ3
    kind: circle
    params:
      center: [0, 0]
      radius: 3
      color: ivory
      stroke_width: 3
  - id: fill3
    kind: area_fill
    params:
      expression: "sqrt(9 - x**2)"
      domain: [-3, 3]
      color: violet
      fill_opacity: 0.35
  - id: graph3
    kind: function_graph
    params:
      expression: "sqrt(9 - x**2)"
      domain: [-3, 3]
      color: violet
      stroke_width: 5
  - id: lbl
    kind: text
    params:
      content: "The upper half of the circle"
      position: [0, 3.4]
      font_size: 30
  - id: lbl2
    kind: text
    params:
      content: "Shaded area = half the circle"
      position: [0, -3.2]
      font_size: 30
actions:
  - { action: create, target: axes1, at: 0 }
  - { action: create, target: circ3, at: 2, duration: 2 }
  - { action: fade_in, target: fill3, at: 4.5, duration: 2.5 }
  - { action: create, target: graph3, at: 7.5, duration: 2.5 }
  - { action: write, target: lbl, at: 10.5 }
  - { action: create, target: lbl2, at: 13.5 }
  - { action: indicate, target: fill3, at: 16, duration: 1.5 }
  - { action: wait, at: 18, duration: 2 }
```

```scene
id: s4
title: The rule
type: recap
duration: 17
narration: >-
  Square the radius, multiply by pi, and you have the area. A radius-3
  circle has area 9 pi, which is about 28.27 square units.
objects:
  - id: f1
    kind: formula
    params:
      content: "A = πr²"
      position: [0, 1.8]
      font_size: 54
      color: violet
  - id: f2
    kind: formula
    params:
      content: "r = 3  →  A = 9π ≈ 28.27"
      position: [0, 0.5]
      font_size: 42
  - id: r3
    kind: text
    params:
      content: "Squaring the radius and multiplying by π gives the area"
      position: [0, -0.8]
      font_size: 30
actions:
  - { action: write, target: f1, at: 0, duration: 2 }
  - { action: write, target: f2, at: 3, duration: 2 }
  - { action: create, target: r3, at: 6 }
  - { action: indicate, target: f2, style: highlight, at: 8.5, duration: 1.5 }
  - { action: scale, target: f2, factor: 1.15, at: 11, duration: 1 }
  - { action: wait, at: 13, duration: 2 }
```
