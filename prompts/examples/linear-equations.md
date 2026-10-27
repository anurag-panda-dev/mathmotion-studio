---
schema_version: "1.0"
lesson:
  title: Straight-Line Graphs — y = 2x + 1
  topic: Straight-line graphs
  grade: "9"
  language: en
  duration_minutes: 4
  aspect_ratio: "16:9"
  theme: midnight
objectives:
  - Plot a straight line from its equation.
  - Read the slope and the y-intercept from an equation.
prerequisites:
  - Plotting points on a coordinate plane
  - Multiplying small integers
recap: >-
  Every straight line has an equation y = mx + c. The number m is the slope:
  how far the line rises for every step of 1 to the right. The number c is
  where the line crosses the y-axis.
practice_questions:
  - "Which line is steeper: y = 3x or y = x / 2?"
  - Where does y = 2x - 4 cross the y-axis?
verification:
  - id: v1
    kind: numeric
    description: The point (3, 7) satisfies y = 2x + 1.
    expression: 2 * 3 + 1 - 7
    expected: 0
---

# Straight-Line Graphs

Teacher note: the lesson plots one line, then isolates the slope calculation
as a worked example. This prose is teacher-facing and never rendered.

```scene
id: s1
title: Opening
type: intro
duration: 12
narration: >-
  Today we draw a straight line from its equation and learn to read two
  numbers straight out of it: the slope and the y-intercept.
objects:
  - id: title
    kind: text
    params:
      content: "Straight-Line Graphs"
      position: [0, 2]
      font_size: 56
      color: violet
  - id: subtitle
    kind: text
    params:
      content: "Every line has an equation: y = 2x + 1"
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
title: Meeting the line
type: explanation
duration: 18
narration: >-
  Here is the line y = 2x + 1. Three points sit on it. Look how the line
  rises two units for every one unit it moves to the right.
objects:
  - id: axes1
    kind: axes
    params:
      x_range: [-6, 6]
      y_range: [-4, 4]
      grid: true
      x_label: x
      y_label: y
  - id: line1
    kind: segment
    params:
      start: [-2, -3]
      end: [1, 3]
      color: violet
      stroke_width: 5
      label: "y = 2x + 1"
  - id: p_left
    kind: point
    params:
      position: [-1, -1]
      color: amber
      label: "(-1, -1)"
  - id: p_int
    kind: point
    params:
      position: [0, 1]
      color: amber
      label: "y-intercept"
  - id: p_right
    kind: point
    params:
      position: [1, 3]
      color: amber
      label: "(1, 3)"
  - id: caption
    kind: text
    params:
      content: "Rise 2 for every run of 1"
      position: [-4.2, 3.2]
      font_size: 30
actions:
  - { action: create, target: axes1, at: 0 }
  - { action: create, target: line1, at: 2, duration: 2 }
  - { action: reveal, target: [p_left, p_int, p_right], at: 6, interval: 0.8 }
  - { action: write, target: caption, at: 9 }
  - { action: circumscribe, target: p_int, at: 12, duration: 1.5, color: violet }
  - { action: wait, at: 14.5, duration: 2 }
```

```scene
id: s3
title: Reading slope and intercept
type: worked_example
duration: 16
narration: >-
  We take two points on the line, (0, 1) and (1, 3), and compute the slope.
  The rise is 3 minus 1, the run is 1 minus 0, so the slope m is 2. The line
  crosses the y-axis at 1, so c is 1.
objects:
  - id: eq1
    kind: equation
    params:
      content: "m = (3 - 1) / (1 - 0) = 2"
      position: [0, 2.6]
      font_size: 40
      color: violet
  - id: eq2
    kind: equation
    params:
      content: "c = 1"
      position: [0, 1.4]
      font_size: 40
  - id: f1
    kind: formula
    params:
      content: "y = 2x + 1"
      position: [0, 0.2]
      font_size: 48
  - id: note
    kind: text
    params:
      content: "m is the slope, c is the y-intercept"
      position: [0, -1.4]
      font_size: 32
actions:
  - { action: write, target: eq1, at: 0, duration: 2 }
  - { action: write, target: eq2, at: 3.5, duration: 1.5 }
  - { action: write, target: f1, at: 6, duration: 2 }
  - { action: indicate, target: f1, style: highlight, at: 9, duration: 1.5 }
  - { action: create, target: note, at: 11 }
  - { action: wait, at: 13, duration: 2 }
```

```scene
id: s4
title: Recap
type: recap
duration: 13
narration: >-
  Straight lines have a constant slope. In y = mx + c, the slope m decides
  how steep the line is, and c decides where it crosses the y-axis.
objects:
  - id: r1
    kind: formula
    params:
      content: "y = mx + c"
      position: [0, 1.5]
      font_size: 52
      color: violet
  - id: r2
    kind: text
    params:
      content: "Straight lines have constant slope"
      position: [0, 0.2]
      font_size: 32
  - id: r3
    kind: text
    params:
      content: "m sets the steepness, c sets the crossing point"
      position: [0, -1.4]
      font_size: 30
actions:
  - { action: write, target: r1, at: 0 }
  - { action: create, target: r2, at: 3 }
  - { action: create, target: r3, at: 5.5 }
  - { action: indicate, target: r1, style: highlight, at: 8, duration: 1.5 }
  - { action: wait, at: 10, duration: 2 }
```
