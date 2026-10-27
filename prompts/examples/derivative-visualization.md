---
schema_version: "1.0"
lesson:
  title: What Is a Derivative?
  topic: Derivatives — the slope of a curve
  grade: "11"
  language: en
  duration_minutes: 5
  aspect_ratio: "16:9"
  theme: midnight
objectives:
  - Explain a derivative as the slope of a curve at one point.
  - Compare a secant line with a tangent line.
  - Compute the derivative of a simple polynomial at a point.
prerequisites:
  - Slope of a straight line
  - Coordinates and the graph of y = x²
recap: >-
  The derivative of a function at a point is the slope of the tangent line at
  that point. It is what the secant slope becomes when the second point slides
  toward the first. For f(x) = x², the derivative is f′(x) = 2x.
practice_questions:
  - What is the slope of y = x² at x = 3?
  - "The derivative of x² at x = 0: is it positive, zero or negative?"
verification:
  - id: v1
    kind: numeric
    description: The tangent line to y = x² at (1, 1) has slope 2.
    expression: (3 - 1) / (2 - 1) - 2
    expected: 0
---

# What Is a Derivative?

Teacher note: scene s3 animates the classic secant-to-tangent limit: point Q
slides along the curve toward P while the secant line transforms into the
tangent line. The tangent is declared but deliberately never created — it
only appears through the `transform` action.

```scene
id: s1
title: Opening
type: intro
duration: 12
narration: >-
  A straight line has one constant slope. A curve does not. So what do we
  mean by the slope of a curve at a single point? The answer is the derivative.
objects:
  - id: title
    kind: text
    params:
      content: "What Is a Derivative?"
      position: [0, 2]
      font_size: 56
      color: violet
  - id: subtitle
    kind: text
    params:
      content: "The slope of a curve at one point"
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
title: The secant line
type: explanation
duration: 19
narration: >-
  Take two points on the curve, P at 1 and Q at 1.5. The straight line
  through them is called a secant. Its slope is 2.5 — an average rate of
  change across the gap between the two points.
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
  - id: p_pt
    kind: point
    params:
      position: [1, 1]
      color: amber
      label: "P (1, 1)"
  - id: q_pt
    kind: point
    params:
      position: [1.5, 2.25]
      color: blue
      label: "Q (1.5, 2.25)"
  - id: secant
    kind: line
    params:
      start: [0, -1.5]
      end: [2, 3.5]
      color: amber
      stroke_width: 4
  - id: lbl
    kind: text
    params:
      content: "Secant through P and Q: slope = 2.5"
      position: [-4.6, 3.4]
      font_size: 30
actions:
  - { action: create, target: axes1, at: 0 }
  - { action: create, target: graph1, at: 1.5, duration: 2.5 }
  - { action: reveal, target: [p_pt, q_pt], at: 5, interval: 0.8 }
  - { action: create, target: secant, at: 7, duration: 1.5 }
  - { action: write, target: lbl, at: 9 }
  - { action: indicate, target: q_pt, at: 12, duration: 1.5 }
  - { action: wait, at: 14.5, duration: 2 }
```

```scene
id: s3
title: The tangent appears
type: explanation
duration: 27
narration: >-
  Now Q slides down the curve toward P. Watch the secant line: as the gap
  shrinks, the line settles into the tangent, which touches the curve only
  at P. Its slope, 2, is the derivative at x equals 1.
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
  - id: p2
    kind: point
    params:
      position: [1, 1]
      color: amber
      label: "P"
  - id: q2
    kind: point
    params:
      position: [1.5, 2.25]
      color: blue
      label: "Q"
  - id: secant2
    kind: line
    params:
      start: [0, -1.5]
      end: [2, 3.5]
      color: amber
      stroke_width: 4
  - id: tangent
    kind: line
    params:
      start: [0, -1]
      end: [2, 3]
      color: teal
      stroke_width: 4
  - id: lbl
    kind: text
    params:
      content: "Q slides toward P"
      position: [-4.6, 3.4]
      font_size: 30
  - id: lbl2
    kind: text
    params:
      content: "The tangent touches the curve only at P"
      position: [0, -3.2]
      font_size: 30
  - id: f_der
    kind: formula
    params:
      content: "f′(x) = 2x"
      position: [0, 2.6]
      font_size: 48
      color: teal
actions:
  - { action: create, target: axes2, at: 0 }
  - { action: create, target: graph2, at: 1.5, duration: 2.5 }
  - { action: reveal, target: [p2, q2], at: 4.5, interval: 0.7 }
  - { action: create, target: secant2, at: 6, duration: 1.5 }
  - { action: write, target: lbl, at: 8 }
  - { action: move, target: q2, to: [1.05, 1.1], at: 10, duration: 2.5 }
  - { action: transform, target: secant2, into: tangent, at: 13, duration: 1.5 }
  - { action: write, target: f_der, at: 15.5, duration: 2 }
  - { action: create, target: lbl2, at: 18 }
  - { action: indicate, target: tangent, at: 20, duration: 1.5 }
  - { action: wait, at: 22, duration: 2 }
```

```scene
id: s4
title: Recap
type: recap
duration: 14
narration: >-
  The derivative gives the slope of the curve at every x. For x squared it
  is 2x, so at x equals 1 the slope is 2 and at x equals 3 the slope is 6.
objects:
  - id: r1
    kind: formula
    params:
      content: "f′(x) = 2x"
      position: [0, 1.8]
      font_size: 54
      color: violet
  - id: r2
    kind: text
    params:
      content: "The derivative gives the slope at any x"
      position: [0, 0.5]
      font_size: 32
  - id: r3
    kind: text
    params:
      content: "Secant becomes tangent as Q approaches P"
      position: [0, -0.8]
      font_size: 30
actions:
  - { action: write, target: r1, at: 0 }
  - { action: create, target: r2, at: 3 }
  - { action: create, target: r3, at: 5.5 }
  - { action: indicate, target: r1, style: highlight, at: 8, duration: 1.5 }
  - { action: wait, at: 10.5, duration: 2 }
```
