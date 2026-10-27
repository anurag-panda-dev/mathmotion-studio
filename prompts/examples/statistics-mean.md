---
schema_version: "1.0"
lesson:
  title: The Mean as a Balancing Point
  topic: Statistics — mean of a data set
  grade: "6"
  language: English
  duration_minutes: 4
  aspect_ratio: "16:9"
  theme: midnight
objectives:
  - Compute the mean of a small data set.
  - See the mean as the balancing point of bar heights.
prerequisites:
  - Addition and division of whole numbers
  - Reading a simple bar chart
recap: >-
  The mean of a data set is the sum of all values divided by the number of
  values. On a bar chart it appears as the height where the bars balance.
practice_questions:
  - Find the mean of 2, 4, 6 and 8.
  - Find the mean of 5, 5, 10, 10 and 10.
verification:
  - id: v1
    kind: numeric
    description: The mean of 4, 6, 8, 10, 12 is 8.
    expression: (4 + 6 + 8 + 10 + 12) / 5
    expected: 8
---

# The Mean as a Balancing Point

Teacher note: bar heights are drawn at 0.25 scene units per data unit above a
baseline of y = -2.5, so the mean line for value 8 falls at y = -0.5 — the
height of the middle bar. Scene s2 demonstrates the `arrange`, `draw_border`
and `reveal` actions.

```scene
id: s1
title: Opening
type: intro
duration: 12
narration: >-
  Five measurements: 4, 6, 8, 10 and 12. Can one single number describe all
  of them? Yes — the mean.
objects:
  - id: title
    kind: text
    params:
      content: "Finding the Mean"
      position: [0, 2]
      font_size: 56
      color: violet
  - id: subtitle
    kind: text
    params:
      content: "One number that describes five values"
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
title: Bars and the balancing line
type: explanation
duration: 20
narration: >-
  Each bar stands for one value. The amber line marks the mean, 8. Values
  above the line and values below the line cancel each other out — the
  bars balance exactly on that line.
objects:
  - id: caption
    kind: text
    params:
      content: "The mean balances the bars"
      position: [0, 2.8]
      font_size: 32
  - id: b1
    kind: rectangle
    params:
      origin: [-3.2, -2]
      width: 0.8
      height: 1
      color: violet
      fill_opacity: 0.5
  - id: b2
    kind: rectangle
    params:
      origin: [-1.6, -1.75]
      width: 0.8
      height: 1.5
      color: violet
      fill_opacity: 0.5
  - id: b3
    kind: rectangle
    params:
      origin: [0, -1.5]
      width: 0.8
      height: 2
      color: violet
      fill_opacity: 0.5
  - id: b4
    kind: rectangle
    params:
      origin: [1.6, -1.25]
      width: 0.8
      height: 2.5
      color: violet
      fill_opacity: 0.5
  - id: b5
    kind: rectangle
    params:
      origin: [3.2, -1]
      width: 0.8
      height: 3
      color: violet
      fill_opacity: 0.5
  - id: v1
    kind: text
    params:
      content: "4"
      position: [-3.2, -3.6]
      font_size: 28
  - id: v2
    kind: text
    params:
      content: "6"
      position: [-1.6, -3.6]
      font_size: 28
  - id: v3
    kind: text
    params:
      content: "8"
      position: [0, -3.6]
      font_size: 28
  - id: v4
    kind: text
    params:
      content: "10"
      position: [1.6, -3.6]
      font_size: 28
  - id: v5
    kind: text
    params:
      content: "12"
      position: [3.2, -3.6]
      font_size: 28
  - id: meanline
    kind: segment
    params:
      start: [-4, -0.5]
      end: [4, -0.5]
      color: amber
      stroke_width: 4
      label: "mean = 8"
actions:
  - { action: create, target: caption, at: 0 }
  - { action: reveal, target: [b1, b2, b3, b4, b5], at: 2, interval: 0.5 }
  - { action: create, target: v1, at: 5 }
  - { action: create, target: v2, at: 5.3 }
  - { action: create, target: v3, at: 5.6 }
  - { action: create, target: v4, at: 5.9 }
  - { action: create, target: v5, at: 6.2 }
  - { action: arrange, target: [v1, v2, v3, v4, v5], layout: row, gap: 1.6, at: 7, duration: 1.5 }
  - { action: create, target: meanline, at: 9, duration: 1.5 }
  - { action: draw_border, target: b5, color: amber, at: 11, duration: 1.5 }
  - { action: indicate, target: meanline, at: 13, duration: 1.5 }
  - { action: wait, at: 15, duration: 2 }
```

```scene
id: s3
title: Computing the mean
type: worked_example
duration: 15
narration: >-
  Add all five values: 4 plus 6 plus 8 plus 10 plus 12 makes 40. Divide by
  how many values there are: 40 divided by 5 equals 8. The mean is 8.
objects:
  - id: f1
    kind: equation
    params:
      content: "(4 + 6 + 8 + 10 + 12) / 5 = 8"
      position: [0, 2]
      font_size: 40
      color: violet
  - id: n1
    kind: text
    params:
      content: "Add every value, then divide by how many there are"
      position: [0, 0.8]
      font_size: 32
  - id: n2
    kind: text
    params:
      content: "The mean sits at the balance point of the data"
      position: [0, -0.4]
      font_size: 30
actions:
  - { action: write, target: f1, at: 0, duration: 2 }
  - { action: create, target: n1, at: 3 }
  - { action: create, target: n2, at: 5.5 }
  - { action: indicate, target: f1, style: highlight, at: 8, duration: 1.5 }
  - { action: wait, at: 10.5, duration: 2 }
```

```scene
id: s4
title: Your turn
type: practice
duration: 12
narration: >-
  Two short exercises. Add the values, divide by the count, and check
  whether your answer sits between the smallest and largest value.
objects:
  - id: q1
    kind: text
    params:
      content: "Find the mean of 2, 4, 6, 8"
      position: [0, 1.2]
      font_size: 36
  - id: q2
    kind: text
    params:
      content: "Find the mean of 5, 5, 10, 10, 10"
      position: [0, -0.4]
      font_size: 34
actions:
  - { action: create, target: q1, at: 0 }
  - { action: create, target: q2, at: 3 }
  - { action: indicate, target: q1, at: 6, duration: 1.5 }
  - { action: wait, at: 8, duration: 2 }
```
