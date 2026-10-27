---
schema_version: "1.0"
lesson:
  title: Equivalent Fractions
  topic: Fractions
  grade: "5"
  language: en
  duration_minutes: 4
  aspect_ratio: "16:9"
  theme: midnight
objectives:
  - Recognise that 1/2, 2/4 and 3/6 name the same amount.
  - Explain equivalence with equal-sized bars.
  - Generate equivalent fractions by scaling numerator and denominator.
prerequisites:
  - Reading fractions
  - Sharing into equal parts
recap: >-
  Equivalent fractions describe the same amount written with different
  numbers. Multiply or divide the top and bottom by the same number and the
  value does not change.
practice_questions:
  - Write two fractions equivalent to 3/5.
  - "Which is larger: 1/3 or 2/6?"
verification:
  - id: v1
    kind: numeric
    description: One half equals two quarters.
    expression: 1 / 2 - 2 / 4
    expected: 0
  - id: v2
    kind: numeric
    description: One half equals three sixths.
    expression: 1 / 2 - 3 / 6
    expected: 0
---

# Equivalent Fractions

Teacher note: the first proof uses two bars of identical size. The left bar
is split in two halves with one half shaded; the right bar is split into
four quarters with two quarters shaded — the same amount of shading.

```scene
id: s1
title: Opening
type: intro
duration: 12
narration: >-
  One half, two quarters, three sixths. Three different names that all
  describe exactly the same amount.
objects:
  - id: title
    kind: text
    params:
      content: "Equivalent Fractions"
      position: [0, 2]
      font_size: 56
      color: violet
  - id: subtitle
    kind: text
    params:
      content: "Different names, the same amount"
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
title: Three names for one amount
type: explanation
duration: 14
narration: >-
  Here are three fractions. They look different, but each one names the
  same part of a whole.
objects:
  - id: cap
    kind: text
    params:
      content: "All three name the same part of a whole"
      position: [0, 2.6]
      font_size: 34
  - id: f1
    kind: fraction
    params:
      numerator: "1"
      denominator: "2"
      position: [-4, 1]
      font_size: 64
      color: violet
  - id: eq1
    kind: text
    params:
      content: "="
      position: [-2.2, 1]
      font_size: 48
  - id: f2
    kind: fraction
    params:
      numerator: "2"
      denominator: "4"
      position: [0, 1]
      font_size: 64
      color: violet
  - id: eq2
    kind: text
    params:
      content: "="
      position: [2.2, 1]
      font_size: 48
  - id: f3
    kind: fraction
    params:
      numerator: "3"
      denominator: "6"
      position: [4, 1]
      font_size: 64
      color: violet
actions:
  - { action: create, target: cap, at: 0 }
  - { action: reveal, target: [f1, eq1, f2, eq2, f3], at: 2, interval: 0.7 }
  - { action: indicate, target: f1, at: 6, duration: 1.5 }
  - { action: indicate, target: f3, at: 7.5, duration: 1.5 }
  - { action: wait, at: 9.5, duration: 2 }
```

```scene
id: s3
title: Proving it with bars
type: explanation
duration: 26
narration: >-
  Two bars of the same length. The left bar is cut into two equal parts with
  one part shaded. The right bar is cut into four equal parts with two parts
  shaded. The shaded amount is identical: half of the bar.
objects:
  - id: caption
    kind: text
    params:
      content: "One shaded half, however the bar is cut"
      position: [0, 2.8]
      font_size: 32
  - id: bar1
    kind: rectangle
    params:
      origin: [-4, -2]
      width: 3
      height: 1.5
      color: ivory
      stroke_width: 4
  - id: half1
    kind: rectangle
    params:
      origin: [-4.75, -2]
      width: 1.5
      height: 1.5
      color: violet
      fill_opacity: 0.4
  - id: split1
    kind: segment
    params:
      start: [-4, -1.25]
      end: [-4, -2.75]
      color: ivory
      stroke_width: 4
  - id: lbl1
    kind: text
    params:
      content: "1/2"
      position: [-4, -3.4]
      font_size: 34
      color: violet
  - id: bar2
    kind: rectangle
    params:
      origin: [3.5, -2]
      width: 3
      height: 1.5
      color: ivory
      stroke_width: 4
  - id: q1
    kind: rectangle
    params:
      origin: [2.75, -2]
      width: 1.5
      height: 1.5
      color: violet
      fill_opacity: 0.4
  - id: split2a
    kind: segment
    params:
      start: [2.75, -1.25]
      end: [2.75, -2.75]
      color: ivory
      stroke_width: 4
  - id: split2b
    kind: segment
    params:
      start: [3.5, -1.25]
      end: [3.5, -2.75]
      color: ivory
      stroke_width: 4
  - id: split2c
    kind: segment
    params:
      start: [4.25, -1.25]
      end: [4.25, -2.75]
      color: ivory
      stroke_width: 4
  - id: lbl2
    kind: text
    params:
      content: "2/4"
      position: [3.5, -3.4]
      font_size: 34
      color: violet
actions:
  - { action: create, target: caption, at: 0 }
  - { action: create, target: bar1, at: 2, duration: 1.5 }
  - { action: create, target: half1, at: 4, duration: 1.5 }
  - { action: create, target: split1, at: 6, duration: 1 }
  - { action: create, target: lbl1, at: 7.5 }
  - { action: create, target: bar2, at: 9.5, duration: 1.5 }
  - { action: create, target: q1, at: 11.5, duration: 1.5 }
  - { action: reveal, target: [split2a, split2b, split2c], at: 13.5, interval: 0.5 }
  - { action: create, target: lbl2, at: 15.5 }
  - { action: indicate, target: half1, at: 17, duration: 1.5 }
  - { action: indicate, target: q1, at: 19, duration: 1.5 }
  - { action: wait, at: 21, duration: 2 }
```

```scene
id: s4
title: The rule
type: recap
duration: 15
narration: >-
  To build an equivalent fraction, multiply or divide the top and the bottom
  by the same number. The amount of the whole never changes.
objects:
  - id: f_sum
    kind: formula
    params:
      content: "1/2 = 2/4 = 3/6"
      position: [0, 1.8]
      font_size: 54
      color: violet
  - id: note1
    kind: text
    params:
      content: "Equivalent fractions describe the same amount"
      position: [0, 0.5]
      font_size: 32
  - id: note2
    kind: text
    params:
      content: "Scale the top and bottom by the same number"
      position: [0, -0.8]
      font_size: 30
actions:
  - { action: write, target: f_sum, at: 0 }
  - { action: create, target: note1, at: 3 }
  - { action: create, target: note2, at: 5.5 }
  - { action: indicate, target: f_sum, style: highlight, at: 8, duration: 1.5 }
  - { action: wait, at: 10.5, duration: 2 }
```
