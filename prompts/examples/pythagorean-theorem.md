---
schema_version: "1.0"
lesson:
  title: The Pythagorean Theorem
  topic: Pythagorean theorem
  grade: "8"
  language: en
  duration_minutes: 5
  aspect_ratio: "16:9"
  theme: midnight
objectives:
  - State the Pythagorean theorem for a right triangle.
  - Check the relationship on a 3-4-5 triangle.
prerequisites:
  - Squaring whole numbers
  - Knowing what a right angle is
recap: >-
  In a right triangle, the squares of the two legs add up to the square of
  the hypotenuse: a² + b² = c². The relation holds only for right triangles.
practice_questions:
  - A right triangle has legs 6 and 8. What is the hypotenuse?
  - A 10 m ladder reaches 6 m up a wall. How far is its base from the wall?
verification:
  - id: v1
    kind: numeric
    description: The 3-4-5 triangle satisfies the theorem.
    expression: 3**2 + 4**2 - 5**2
    expected: 0
---

# The Pythagorean Theorem

Teacher note: this lesson builds the theorem visually from a single right
triangle and the squares on its three sides. This prose section is notes for
the teacher; it is shown on the scene-review page and never rendered on screen.

```scene
id: s1
title: Opening
type: intro
duration: 12
narration: >-
  Today we meet one of the oldest and most useful rules in mathematics:
  the Pythagorean theorem. It connects the three sides of every right triangle.
objects:
  - id: title
    kind: text
    params:
      content: "The Pythagorean Theorem"
      position: [0, 2]
      font_size: 56
      color: violet
  - id: subtitle
    kind: text
    params:
      content: "Every right triangle tells the same story"
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
title: One right triangle
type: explanation
duration: 14
narration: >-
  Here is a right triangle. The legs meet at the right angle in corner A.
  The longest side, the hypotenuse, lies opposite that right angle.
objects:
  - id: tri
    kind: triangle
    params:
      vertices: [[0, -1], [2, -1], [0, 0.5]]
      labels: [A, B, C]
      color: ivory
      stroke_width: 5
  - id: right_angle
    kind: angle
    params:
      vertex: [0, -1]
      start_angle: 0
      end_angle: 90
      radius: 0.5
      color: violet
      label: "90°"
  - id: caption
    kind: text
    params:
      content: "c is the side opposite the right angle"
      position: [0, 3]
      font_size: 32
actions:
  - { action: create, target: tri, at: 0 }
  - { action: create, target: right_angle, at: 2, duration: 1.5 }
  - { action: write, target: caption, at: 5 }
  - { action: indicate, target: right_angle, at: 9 }
  - { action: wait, at: 11, duration: 2 }
```

```scene
id: s3
title: The square on each side
type: explanation
duration: 18
narration: >-
  Now a square grows on every side. The two small squares sit on the legs,
  the large square sits on the hypotenuse. Watch their areas.
objects:
  - id: sq_a
    kind: square
    params:
      origin: [1, -2]
      side: 2
      color: violet
      fill_opacity: 0.25
  - id: label_a
    kind: text
    params:
      content: "a²"
      position: [1, -2]
      font_size: 44
      color: violet
  - id: sq_b
    kind: square
    params:
      origin: [-0.75, -0.25]
      side: 1.5
      color: blue
      fill_opacity: 0.25
  - id: label_b
    kind: text
    params:
      content: "b²"
      position: [-0.75, -0.25]
      font_size: 40
      color: blue
  - id: sq_c
    kind: square
    params:
      origin: [1.75, 0.75]
      side: 2.5
      angle: 143.13
      color: teal
      fill_opacity: 0.25
  - id: label_c
    kind: text
    params:
      content: "c²"
      position: [1.75, 0.75]
      font_size: 48
      color: teal
actions:
  - { action: create, target: sq_a, at: 0, duration: 1.5 }
  - { action: create, target: label_a, at: 1.5 }
  - { action: create, target: sq_b, at: 3.5, duration: 1.5 }
  - { action: create, target: label_b, at: 5 }
  - { action: create, target: sq_c, at: 7, duration: 2 }
  - { action: create, target: label_c, at: 9 }
  - { action: indicate, target: sq_c, at: 11, duration: 1.5 }
  - { action: wait, at: 13.5, duration: 2 }
```

```scene
id: s4
title: The rule
type: recap
duration: 16
narration: >-
  The area of the square on the hypotenuse always equals the sum of the areas
  of the other two squares. For the classic 3-4-5 triangle: 9 plus 16 is 25.
objects:
  - id: formula
    kind: formula
    params:
      content: "a² + b² = c²"
      position: [0, 2.6]
      font_size: 60
      color: violet
  - id: check
    kind: text
    params:
      content: "3² + 4² = 9 + 16 = 25 = 5²"
      position: [0, 1.2]
      font_size: 40
  - id: closing
    kind: text
    params:
      content: "This works for every right triangle"
      position: [0, -2.6]
      font_size: 34
actions:
  - { action: write, target: formula, at: 0, duration: 2.5 }
  - { action: write, target: check, at: 4, duration: 2.5 }
  - { action: indicate, target: check, style: highlight, at: 8, duration: 1.5 }
  - { action: create, target: closing, at: 11 }
  - { action: wait, at: 13.5, duration: 2 }
```
