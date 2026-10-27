---
schema_version: "1.0"
lesson:
  title: The Sum of Angles in a Triangle
  topic: Triangle geometry
  grade: "8"
  language: English
  duration_minutes: 4
  aspect_ratio: "16:9"
  theme: midnight
objectives:
  - Identify the three interior angles of a triangle.
  - Show that the three angles together make a straight line, that is 180°.
prerequisites:
  - Measuring angles in degrees
  - Knowing that a straight line is 180°
recap: >-
  The three interior angles of any triangle add up to 180°. If you cut off
  the three corners and lay them end to end, they exactly fill a straight line.
practice_questions:
  - Two angles of a triangle are 50° and 60°. What is the third angle?
  - Can a triangle have three right angles? Explain.
verification:
  - id: v1
    kind: numeric
    description: The angles of the 63.4-50.2-66.4 degree triangle sum to 180 degrees.
    expression: 63.43 + 50.19 + 66.38 - 180
    expected: 0
    tolerance: 0.001
---

# The Sum of Angles in a Triangle

Teacher note: the example triangle has vertices A(-2, -1.5), B(2, -1.5) and
C(-0.5, 1.5); its interior angles measure approximately 63.43°, 50.19° and
66.38°. Scene s3 places the three angle values on a number line where they
fill 0° to 180° end to end.

```scene
id: s1
title: Opening
type: intro
duration: 12
narration: >-
  Every triangle, no matter how it is shaped, holds the same secret: its
  three angles always add up to a straight line.
objects:
  - id: title
    kind: text
    params:
      content: "Angles in a Triangle"
      position: [0, 2]
      font_size: 56
      color: violet
  - id: subtitle
    kind: text
    params:
      content: "Three angles, one straight line"
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
title: Marking the three angles
type: explanation
duration: 16
narration: >-
  Here is one triangle. Its corners hold the angles alpha, beta and gamma.
  Alpha measures 63.4 degrees, beta 50.2 degrees, gamma 66.4 degrees.
objects:
  - id: tri
    kind: triangle
    params:
      vertices: [[-2, -1.5], [2, -1.5], [-0.5, 1.5]]
      labels: [A, B, C]
      color: ivory
      stroke_width: 5
  - id: ang_a
    kind: angle
    params:
      vertex: [-2, -1.5]
      start_angle: 0
      end_angle: 63.43
      radius: 0.6
      color: violet
      label: "α"
  - id: ang_b
    kind: angle
    params:
      vertex: [2, -1.5]
      start_angle: 129.81
      end_angle: 180
      radius: 0.6
      color: blue
      label: "β"
  - id: ang_c
    kind: angle
    params:
      vertex: [-0.5, 1.5]
      start_angle: 243.43
      end_angle: 309.81
      radius: 0.6
      color: teal
      label: "γ"
  - id: caption
    kind: text
    params:
      content: "α = 63.4°    β = 50.2°    γ = 66.4°"
      position: [0, 3.2]
      font_size: 32
actions:
  - { action: create, target: tri, at: 0 }
  - { action: create, target: ang_a, at: 2, duration: 1.5 }
  - { action: create, target: ang_b, at: 4, duration: 1.5 }
  - { action: create, target: ang_c, at: 6, duration: 1.5 }
  - { action: write, target: caption, at: 9 }
  - { action: wait, at: 11.5, duration: 2 }
```

```scene
id: s3
title: Laying the angles end to end
type: proof
duration: 20
narration: >-
  Now take the three angles away from the corners and place them end to end
  on a number line. Alpha fills the first stretch, beta continues, and gamma
  completes exactly to 180 degrees — a straight line.
objects:
  - id: nl
    kind: number_line
    params:
      range: [0, 180]
      step: 15
      color: ivory
      label: "End to end along a line"
      markers:
        - { value: 63.43, label: "α", color: violet }
        - { value: 113.62, label: "α + β", color: blue }
        - { value: 180, label: "180°", color: teal }
  - id: f_sum
    kind: formula
    params:
      content: "α + β + γ = 180°"
      position: [0, 2.4]
      font_size: 50
      color: violet
  - id: note
    kind: text
    params:
      content: "Cut off the corners and they fill a straight line"
      position: [0, -2.6]
      font_size: 30
actions:
  - { action: create, target: nl, at: 0, duration: 2 }
  - { action: indicate, target: nl, at: 3, duration: 1.5 }
  - { action: write, target: f_sum, at: 6 }
  - { action: create, target: note, at: 10 }
  - { action: indicate, target: f_sum, style: highlight, at: 13, duration: 1.5 }
  - { action: wait, at: 15.5, duration: 2 }
```

```scene
id: s4
title: Recap
type: recap
duration: 14
narration: >-
  The three angles of every triangle add up to 180 degrees. This holds for
  sharp triangles, flat triangles and right triangles alike.
objects:
  - id: r1
    kind: formula
    params:
      content: "α + β + γ = 180°"
      position: [0, 1.8]
      font_size: 52
      color: violet
  - id: r2
    kind: text
    params:
      content: "This is true for every triangle"
      position: [0, 0.5]
      font_size: 32
  - id: r3
    kind: text
    params:
      content: "Even a triangle with a 90° angle"
      position: [0, -0.8]
      font_size: 30
actions:
  - { action: write, target: r1, at: 0 }
  - { action: create, target: r2, at: 3 }
  - { action: create, target: r3, at: 5.5 }
  - { action: indicate, target: r1, style: highlight, at: 8, duration: 1.5 }
  - { action: wait, at: 10.5, duration: 2 }
```
