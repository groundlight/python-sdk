---
title: "Navigating the Ambiguity with Groundlight AI Detectors"
description: Let's talk more about ambiguous image queries
slug: dealing-with-unclear-images
authors:
  - name: Sharmila Reddy Nangi
    title: Applied ML Scientist
    image_url: https://a-us.storyblok.com/f/1015187/1000x1000/b66d1cddeb/nangis.jpg
tags: [unclears, real-world ambiguity ]
image: ./images/unclear_blog/unclear_label.png
hide_table_of_contents: false
---

When you first explore the capabilities of our Groundlight AI detectors, you'll quickly notice that they excel at answering binary questions. These are queries expecting a straightforward "Yes" or "No" response. However, the world around us rarely conforms to such black-and-white distinctions, particularly when analyzing images. In reality, many scenarios present challenges that defy a simple binary answer.

<!-- truncate -->

## Exploring the Gray Areas: Real-World Examples

Consider the following scenarios that highlight the complexity of interpreting real-world images:

1. **The Case of the Hidden Oven**: Imagine asking, "Is the oven light turned on?" only to find the view partially blocked by a person. With the contents on the other side hidden from view, providing a definitive "Yes" or "No" becomes impossible. Such instances are best described as "Unclear."
<figure style={{ textAlign: 'center' }}>
    <img src={require('./images/unclear_blog/hidden_oven.png').default} width="350px"/>
    <figcaption>
    <small>
     Oven is hidden from the camera view
    </small>
    </figcaption>
</figure>

2. **The Locked Garage Door Dilemma**: When faced with a query like, "Is the garage door locked?" accompanied by an image shrouded in darkness or blurred beyond recognition, identifying the status of the door lock is a challenge. In these circumstances, clarity eludes us, leaving us unable to confidently answer.
<figure style={{ textAlign: 'center' }}>
    <img src={require('./images/unclear_blog/dark_door.png').default} width="350px"/>
    <figcaption>
    <small>
     Dark images make it difficult to answer the query
    </small>
    </figcaption>
</figure>

3. **Irrelevant Imagery**: At times, the images presented may bear no relation to the question posed. These irrelevant scenes further underscore the limitations of binary responses in complex situations. For instance, responding to the question "Is there a black jacket on the coat hanger?" with the following image (that doesn't even include a coat hanger) exemplifies how such imagery can be off-topic and fail to address the query appropriately.
<figure style={{ textAlign: 'center' }}>
    <img src={require('./images/unclear_blog/unrelated_img.png').default} width="350px" />
    <figcaption>
    <small>
    Images unrelated to the query lead to ambiguity
    </small>
    </figcaption>
</figure>


## Strategies for Navigating Ambiguity

Although encountering unclear images might seem like a setback, it actually opens up avenues for improvement and customization. Our detectors are designed to identify and flag these ambiguous cases, empowering you to steer their interpretation. Here are some strategies you can employ to enhance the process:

1. **Clarify your queries** : It's crucial to formulate your questions to the system with precision, avoiding any vagueness. For instance, instead of asking, “Is the light ON?” opt for a more detailed inquiry such as, “Can you clearly see the red LED on the right panel turned ON?” This approach ensures your queries are direct and specific.
2. **Customize Yes/ No classifications**: You can specify how the model should interpret and deal with unclear images by reframing your queries and notes. For instance, by specifying “If the garage door is not visible, mark it as a NO” in your notes, you can make the detector sort unclear images into the “NO” class. You can refer to our [previous blog post](https://code.groundlight.ai/python-sdk/blog/best-practices) for best practices while refining your queries and notes.
3. **Flagging “Unclear” images**: Should you prefer to classify an obstructed view or irrelevant imagery as “Unclear”, simply add a couple of labels as “UNCLEAR” or provide instructions in the notes. Groundlight's machine learning systems will adapt to your preference and continue to flag them as "Unclear" for you.
<figure style={{ textAlign: 'center' }}>
    <img src={require('./images/unclear_blog/unclear_label.png').default} width="350px" class="center"/>
    <figcaption>
    <small>
    Marking an image query as “Unclear" in the data review page
    </small>
    </figcaption>
</figure>


The strategies outlined above will significantly improve your ability to navigate through unclear 
scenarios. However, there exist many other situations, such as borderline classifications or cases where there's insufficient information for a definitive answer. Recognizing and managing the inherent uncertainty in these tasks is crucial as we progress. We are committed to building more tools that empower you to deal with these challenges.

