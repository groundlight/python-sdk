# Writing Queries

## Introduction

With Groundlight's `detectors`, you can ask binary questions about images -- i.e., the answer should be
unambiguously "YES" or "NO". So, what makes a good question? Let's look at a few good 🟢, moderate
🟡, and bad ❌ examples!

## Examples

### 🟢 Are there any cardboard boxes on the conveyor belt?

This question is binary and can be answered unambiguously with a simple "YES" or "NO" based on the
image content.

### 🟡 Is the trash can full?

This question is okay, but it could be rephrased to be more specific. For example, "Is the black
trash can more than 80% full?"

:::tip
With Groundlight, your questions may be routed to a machine learning model or a human reviewer. One
way to improve your queries is to think "If I asked a person this question, what would they need to
know to answer it?"
:::

### 🟢 Is the garage door completely closed?

The query is very specific about what "YES" means. According to this query, any slight / partial
opening would be considered "NO".

### 🟡 Is the weather nice out?

This question is somewhat ambiguous. Different people may have different opinions on what
is nice weather. Instead, you might ask "Can you see any clouds in the sky?"

### ❌ Where is the thing?

This is not a binary question -- "YES" and "NO" don't make sense in this context. Also, it's not
clear what the "thing" refers to.

### 🟡 Is the factory floor clean and organized?

While this question is binary, "cleanliness" can be somewhat subjective. An improved version could
be: "Are there any visible spills or clutter on the factory floor?"

### ❌ Is the forklift on the left or right side?

It is not clear which answer corresponds to "YES" and which corresponds to "NO". Instead, you might
ask "Is there a forklift in a?".
