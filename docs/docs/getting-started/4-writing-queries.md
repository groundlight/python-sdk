# Writing Queries

## Introduction

With Groundlight's `detectors`, you can ask binary questions about images &mdash; i.e., the answer
should be unambiguously "YES" or "NO". If you ask an ambiguous question, you may receive an "UNSURE"
response.

```python notest
detector = gl.get_or_create_detector(
    name="Conveyor belt boxes",
    query="Are there any cardboard boxes on the conveyor belt?"
)
image_query = gl.submit_image_query(detector=detector, image=some_image)

# The SDK can return "YES" or "NO" (or "UNSURE")
print(f"The answer is {image_query.result.label}")
```

So, what makes a good question? Let's look at a few good ✅, moderate 🟡, and bad ❌ examples!

## Examples

### ✅ Are there any cardboard boxes on the conveyor belt?

This question is binary and can be answered unambiguously with a simple "YES" or "NO" based on the
image content.

### 🟡 Is the trash can full?

This question is okay, but it could be rephrased to be more specific. For example, "Is the black
trash can more than 80% full?"

:::tip
With Groundlight, your questions may be routed to a machine learning model or a human reviewer. One
way to improve your questions is to think, "If I saw this question for the first time, would I know
precisely what the person was trying to convey?"
:::

### ✅ Is the garage door completely closed?

The query is very specific about what "YES" means. According to this query, any slight / partial
opening would be considered "NO".

### 🟡 Is the weather nice out?

This question is somewhat ambiguous. Different people may have different opinions on what
is nice weather. Instead, you might ask "Can you see any clouds in the sky?"

### ❌ Where is the thing?

This is not a binary question &mdash; "YES" and "NO" don't make sense in this context. Also, it's
not clear what the "thing" refers to.

### 🟡 Is the factory floor clean and organized?

While this question is binary, "cleanliness" can be somewhat subjective. An improved version could
be: "Are there any visible spills or clutter on the factory floor?"
