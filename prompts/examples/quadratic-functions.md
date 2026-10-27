---
schema_version: "1.0"
lesson:
  title: The Graph of y = x²
  topic: Quadratic functions
  grade: "9"
  language: English
  duration_minutes: 4
  aspect_ratio: "16:9"
  theme: midnight
objectives:
  - Sketch the parabola y = x² from plotted values.
  - Describe the symmetry of the parabola.
  - Compare y = x² with y = 2x².
prerequisites:
  - Squaring positive and negative numbers
  - Plotting points on a coordinate plane
recap: >-
  The graph of y = x² is a parabola with its vertex at the origin, symmetric
  across the y-axis. Multiplying the equation by 2 makes the parabola narrower
  because the y-values grow twice as fast.
practice_questions:
  - What is the y-value of y = x² when x = -3?
  - "Which parabola is narrower: y = x² or y = 3x²?"
verification:
  - id: v1
    kind: numeric
    description: The point (2, 4) lies on y = x².
    expression: 2 ** 2 - 4
    expected: 0
---

# The Graph of y = x²

Teacher note: builds the parabola point by point, then uses two special
points to show symmetry, then compares with a stretched parabola.

```scene
id: s1
title: Opening
type: intro
duration: 12
narration: >-
  Today we build one of the most important graphs in mathematics, the
  parabola, from the simple rule y equals x squared.
objects:
  - id: title
    kind: text
    params:
      content: "The Parabola"
      position: [0, 2]
      font_size: 58
      color: violet
  - id: subtitle
    kind: text
    params:
      content: "The graph of y = x²"
      position: [0, 0.8]
      font_size: 36
actions:
  - { action: create, target: title, at: 0 }
  - { action: create, target: subtitle, at: 2 }
  - { action: indicate, target: title, style: pulse, at: 5, duration: 1.5 }
  - { action: wait, at: 8, duration: 2 }
```

```scene
id: s2
title: Drawing y = x squared
type: explanation
duration: 15
narration: >-
  Square every x and you get y. The lowest point sits at the origin, and the
  curve climbs away from it on both sides with the same shape.
objects:
  - id: axes1
    kind: axes
    params:
      x_range: [-3, 3]
      y_range: [-4, 4]
      grid: true
      x_label: x
      y_label: y
  - id: graph1
    kind: function_graph
    params:
      expression: "x**2"
      domain: [-2, 2]
      color: violet
      stroke_width: 5
  - id: vertex
    kind: point
    params:
      position: [0, 0]
      color: amber
      label: "vertex (0, 0)"
  - id: lbl
    kind: text
    params:
      content: "y = x²"
      position: [2.6, 3.2]
      font_size: 40
      color: violet
actions:
  - { action: create, target: axes1, at: 0 }
  - { action: create, target: graph1, at: 1.5, duration: 2.5 }
  - { action: create, target: vertex, at: 5 }
  - { action: write, target: lbl, at: 7 }
  - { action: indicate, target: vertex, at: 9 }
  - { action: wait, at: 11, duration: 2 }
```

```scene
id: s3
title: A mirror image
type: explanation
duration: 18
narration: >-
  The points (-1, 1) and (1, 1) sit at the same height. Whatever happens on
  one side of the y-axis is mirrored on the other side. That is symmetry.
objects:
  - id: axes2
    kind: axes
    params:
      x_range: [-3, 3]
      y_range: [-4, 4]
      grid: true
      x_label: x
      y_label: y
  - id: graph2
    kind: function_graph
    params:
      expression: "x**2"
      domain: [-2, 2]
      color: violet
      stroke_width: 5
  - id: p_neg
    kind: point
    params:
      position: [-1, 1]
      color: amber
      label: "(-1, 1)"
  - id: p_pos
    kind: point
    params:
      position: [1, 1]
      color: amber
      label: "(1, 1)"
  - id: mirror
    kind: segment
    params:
      start: [-1, 1]
      end: [1, 1]
      color: gray
      stroke_width: 3
  - id: note
    kind: text
    params:
      content: "Symmetric across the y-axis"
      position: [0, -2.6]
      font_size: 34
actions:
  - { action: create, target: axes2, at: 0 }
  - { action: create, target: graph2, at: 1.5, duration: 2 }
  - { action: reveal, target: [p_neg, p_pos], at: 5, interval: 0.8 }
  - { action: create, target: mirror, at: 7, duration: 1.5 }
  - { action: write, target: note, at: 9 }
  - { action: fade_out, target: mirror, at: 12, duration: 1.5 }
  - { action: wait, at: 14, duration: 2 }
```

```scene
id: s4
title: Comparing y = x squared and y = 2x squared
type: explanation
duration: 20
narration: >-
  Now watch two curves together. The blue curve is y = 2x squared. Its
  y-values are twice as large, so it rises faster and looks narrower.
objects:
  - id: axes3
    kind: axes
    params:
      x_range: [-3, 3]
      y_range: [-4, 4]
      grid: false
      x_label: x
      y_label: y
  - id: g1
    kind: function_graph
    params:
      expression: "x**2"
      domain: [-2, 2]
      color: violet
      stroke_width: 4
  - id: g2
    kind: function_graph
    params:
      expression: "2 * x**2"
      domain: [-1.4, 1.4]
      color: blue
      stroke_width: 4
  - id: lbl1
    kind: text
    params:
      content: "y = x²"
      position: [-2.7, 3.4]
      font_size: 34
      color: violet
  - id: lbl2
    kind: text
    params:
      content: "y = 2x²"
      position: [2.1, 3.4]
      font_size: 34
      color: blue
  - id: note
    kind: text
    params:
      content: "The blue curve rises twice as fast"
      position: [0, -3.2]
      font_size: 32
actions:
  - { action: create, target: axes3, at: 0 }
  - { action: create, target: g1, at: 1.5, duration: 2 }
  - { action: create, target: g2, at: 4, duration: 2 }
  - { action: create, target: lbl1, at: 6.5 }
  - { action: create, target: lbl2, at: 8 }
  - { action: write, target: note, at: 10 }
  - { action: recolor, target: g1, color: gray, at: 13, duration: 1 }
  - { action: wait, at: 15, duration: 2 }
```
