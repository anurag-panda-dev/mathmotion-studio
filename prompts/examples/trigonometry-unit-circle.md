---
schema_version: "1.0"
lesson:
  title: Trigonometry on the Unit Circle
  topic: Trigonometry — sine and cosine
  grade: "10"
  language: English
  duration_minutes: 5
  aspect_ratio: "16:9"
  theme: midnight
objectives:
  - Explain sine and cosine as ratios in a right triangle.
  - Read the coordinates of a point on a circle from an angle.
  - Verify the identity sin²θ + cos²θ = 1 for 45°.
prerequisites:
  - Right-triangle ratios
  - Angles in degrees
recap: >-
  Sine is the opposite side divided by the hypotenuse, cosine is the adjacent
  side divided by the hypotenuse. On a circle of radius 1 the coordinates of
  the point are exactly (cos θ, sin θ), which is why sin²θ + cos²θ = 1.
practice_questions:
  - What are sin 30° and cos 30°?
  - Which coordinate of P is larger when the angle is 70°?
verification:
  - id: v1
    kind: numeric
    description: sin squared plus cos squared of 45 degrees equals 1.
    expression: sin(pi / 4) ** 2 + cos(pi / 4) ** 2 - 1
    expected: 0
---

# Trigonometry on the Unit Circle

Teacher note: the circle is drawn with radius 2 so the triangle inside it is
easy to read; the ratio definitions apply unchanged to the radius-1 unit
circle referenced in scene s3.

```scene
id: s1
title: Opening
type: intro
duration: 12
narration: >-
  Sine and cosine start as sides of a right triangle, but they are really
  about one angle swinging around a circle.
objects:
  - id: title
    kind: text
    params:
      content: "Trigonometry on the Circle"
      position: [0, 2]
      font_size: 52
      color: violet
  - id: subtitle
    kind: text
    params:
      content: "Sine and cosine from a single angle"
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
title: The triangle inside the circle
type: explanation
duration: 21
narration: >-
  A radius swings out from the centre and stops at 45 degrees. The horizontal
  leg is the cosine part, the vertical leg is the sine part, and together
  with the radius they form a right triangle.
objects:
  - id: axes1
    kind: axes
    params:
      x_range: [-3, 3]
      y_range: [-3, 3]
      grid: false
      x_label: x
      y_label: y
  - id: circ
    kind: circle
    params:
      center: [0, 0]
      radius: 2
      color: ivory
      stroke_width: 4
  - id: ang
    kind: angle
    params:
      vertex: [0, 0]
      start_angle: 0
      end_angle: 45
      radius: 0.9
      color: violet
      label: "45°"
  - id: adj
    kind: segment
    params:
      start: [0, 0]
      end: [1.41, 0]
      color: blue
      stroke_width: 4
      label: "cos 45°"
  - id: opp
    kind: segment
    params:
      start: [1.41, 0]
      end: [1.41, 1.41]
      color: teal
      stroke_width: 4
      label: "sin 45°"
  - id: hyp
    kind: segment
    params:
      start: [0, 0]
      end: [1.41, 1.41]
      color: violet
      stroke_width: 5
  - id: p_point
    kind: point
    params:
      position: [1.41, 1.41]
      color: amber
      label: "P"
  - id: note
    kind: text
    params:
      content: "The radius (hypotenuse) has length 2"
      position: [0, 3.2]
      font_size: 30
actions:
  - { action: create, target: axes1, at: 0 }
  - { action: create, target: circ, at: 1.5, duration: 2 }
  - { action: create, target: ang, at: 4, duration: 1.5 }
  - { action: reveal, target: [adj, opp], at: 6.5, interval: 0.7 }
  - { action: create, target: hyp, at: 8.5, duration: 1 }
  - { action: create, target: p_point, at: 10 }
  - { action: write, target: note, at: 12 }
  - { action: indicate, target: p_point, at: 14.5, duration: 1.5 }
  - { action: wait, at: 16.5, duration: 2 }
```

```scene
id: s3
title: From the triangle to the ratios
type: explanation
duration: 16
narration: >-
  Sine is the opposite side over the hypotenuse. Cosine is the adjacent side
  over the hypotenuse. On a circle of radius 1, those ratios are exactly the
  coordinates of the point P.
objects:
  - id: f1
    kind: formula
    params:
      content: "sin θ = opposite / hypotenuse"
      position: [0, 1.8]
      font_size: 44
      color: violet
  - id: f2
    kind: formula
    params:
      content: "cos θ = adjacent / hypotenuse"
      position: [0, 0.6]
      font_size: 44
      color: blue
  - id: note
    kind: text
    params:
      content: "On a circle of radius 1, P = (cos θ, sin θ)"
      position: [0, -1.2]
      font_size: 32
actions:
  - { action: create, target: f1, at: 0, duration: 1.5 }
  - { action: create, target: f2, at: 2.5, duration: 1.5 }
  - { action: write, target: note, at: 5 }
  - { action: indicate, target: f1, style: highlight, at: 7, duration: 1.5 }
  - { action: indicate, target: f2, style: highlight, at: 9, duration: 1.5 }
  - { action: wait, at: 11.5, duration: 2 }
```

```scene
id: s4
title: Recap
type: recap
duration: 14
narration: >-
  The squares of sine and cosine of the same angle always add up to 1.
  At 45 degrees both are the same value, about 0.707.
objects:
  - id: r1
    kind: formula
    params:
      content: "sin²θ + cos²θ = 1"
      position: [0, 1.8]
      font_size: 54
      color: violet
  - id: r2
    kind: text
    params:
      content: "The identity holds for every angle θ"
      position: [0, 0.5]
      font_size: 32
  - id: r3
    kind: text
    params:
      content: "At 45°: sin θ = cos θ ≈ 0.707"
      position: [0, -0.8]
      font_size: 30
actions:
  - { action: write, target: r1, at: 0 }
  - { action: create, target: r2, at: 3 }
  - { action: create, target: r3, at: 5.5 }
  - { action: indicate, target: r1, style: highlight, at: 8, duration: 1.5 }
  - { action: wait, at: 10.5, duration: 2 }
```
