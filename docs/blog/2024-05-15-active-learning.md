---
title: "Reducing Data Labeling Costs with Uncertainty Sampling Active Learning"
description: How Groundlight uses active learning to train accurate vision models while saving on data labeling costs.
slug: active-learning
authors:
  - name: Ted Sandler
    title: Senior Applied Scientist
    image_url: https://a-us.storyblok.com/f/1015187/1000x1000/efc35da152/sandlert.jpg
tags: [active learning, uncertainty sampling, deep dive]
image: ./images/active-learning/social-active-learning-flow.png
hide_table_of_contents: false
---

At Groundlight, we train each detector's machine learning (ML) model on images that have been manually labeled with correct responses. However, collecting labels at scale becomes expensive because it requires human review. Given that detectors are frequently applied to streams of images that change slowly over time, reviewing all images as they arrive is likely to result in effort wasted on labeling similar images that add little information to the training set.

<!-- truncate -->

#### What is Active Learning in Machine Learning?

To avoid unnecessary labeling and save customers money, Groundlight uses **[active learning](https://en.wikipedia.org/wiki/Active_learning_(machine_learning))**, a machine learning protocol in which the ML model plays an active role in determining which images get manually labeled for training. With active learning, only informative images are prioritized for review, making it possible to label small a subset of the available data but train a model that's roughly as good as one trained with all the data labeled [\[Settles, 2009\]](https://minds.wisconsin.edu/handle/1793/60660).

#### What is Uncertainty Sampling in Active Learning?

The variant of active learning we use at Groundlight is based on **[uncertainty sampling](https://lilianweng.github.io/posts/2022-02-20-active-learning/#uncertainty-sampling)**, a well studied and effective method that can be used in either the streaming setting or the pool-based setting in which there exists a large reservoir of unlabeled examples to draw from. We operate in the stream-based setting, where images arrive one at a time and it must be decided in the moment whether to escalate an image for review.

#### How Does Uncertainty Sampling Work?

Imagine we have a detector that processes a stream of images arriving one by one. The detector's ML model is trained on all images labeled up to that point in time. When a new image arrives, the model makes its best guess prediction for the new image and also reports its confidence in that prediction. The confidence is expressed as a probability (a number between zero and one) that the prediction is correct.

In uncertainty sampling, we escalate those images whose predictions have low confidence so they can be manually reviewed and labeled. Conversely, we largely leave images with confident predictions unescalated and therefore unlabled. In this way, we avoid the expense and effort of labeling images whose predictions are likely correct. But we still continue to label images the model is unsure of so it can be trained on them.

### An Example of Uncertainty Sampling

As an example, the images shown below were sent to a detector that identifies the presence of dogs in and around a swimming pool at [Dogmode's Aquatic Center](https://dogmode.com/aquatic-fitness-center-pool-view/). The model reports with 95% confidence that there is a dog in the image on the left. But it is less confident in its response for the image on the right, saying there is no dog present with only 75% confidence. (There is in fact a dog, at the back left corner of the pool, but it’s difficult to see.)
<table cellspacing="0" cellpadding="0">
<center>
<tr>
  <td><img src={require('./images/active-learning/dog-conf-high.png').default} /></td>
  <td><img src={require('./images/active-learning/dog-conf-low.png').default} /></td>
</tr>
<tr><td>Yes</td><td>No</td></tr>
</center>
</table>

<br/>

Assuming the detector's confidence threshold is set to a value between 75% and 95%, uncertainty sampling will escalate the image on the right for cloud labeling but not the one on the left. A user can set their detector's confidence threshold by adjusting the confidence threshold slider on the detector detail page. The image below shows this slider.
<img src={require('./images/active-learning/confidence-threshold.png').default} />
<br/>

### Results of a Data Labeling Experiment using Active Learning

We now present results from a time-series experiment of images collected and labeled for the purpose of measuring uncertainty sampling's impact on model accuracy and labeling cost. There are 500 images of a gate, and the task is to determine in every image if the gate has been left open or closed. All images in the experiment are labeled so we know the correct responses. But note[^1] that this would not be the case if we were running active learning in real life because, by design, active learning does not recruit labels on high confidence images.

[^1]: In practice, we audit a constant fraction of unescalated images for review, and these serve as an additional source of labeled data.


Our results compare the performance of three models trained under different protocols:
1. No uncertainty sampling, all images are escalated for manual review and labeling
2. Moderate uncertainty sampling, predictions less than 95% confident get escalated
3. Aggressive uncertainty sampling, only predictions below 75% confidence are escalated

The training sets of all three models are initialized with the same 20 images, 10 labeled from each class.

The plot below shows that the model trained with moderate uncertainty sampling (confidence threshold 95%) has an error rate similar to the model trained without any uncertainty sampling. This demonstrates that uncertainty sampling can fit a model as accurately as labeling and training on all the available data.
<img
 src={require('./images/active-learning/error-rate-over-time.png').default} 
 width="500 px"
/>

On the other hand, aggressive uncertainty sampling (confidence threshold 75%) escalates too few images for labeling, resulting in a model trained on less data that makes more mistakes. This shows how the confidence threshold controls the trade off between model accuracy and manual labeling cost. Indirectly, it also demonstrates the need for calibrating models so their reported confidences reflect observed frequencies and can be used for deciding at what confidence level to escalate. We calibrate machine learning models at Groundlight, though the details are beyond the scope of this post.

Strikingly, plotting the number of images escalated by each model shows that active learning dramatically reduces labeling costs. The model trained without uncertainty sampling escalates all 500 of the images for review manual review. In contrast, the model trained with moderate uncertainty sampling escalates only 132 images in total. This is a nearly 75% reduction in manual labeling and cost with little change in model error. Aggressive uncertainty sampling escalates even fewer images, only 60, but the resulting model has noticeably higher error as observed in the plot above.
<img
 src={require('./images/active-learning/labels-over-time.png').default}
 width="500 px"
/>

### Conclusion

At Groundlight, we use active learning to reduce labeling costs for our customers. In particular, we use a variant based on uncertainty sampling that is extremely effective and easy to explain. A small experiment on image time-series data shows that uncertainty sampling can dramatically reduce the number of images labeled without impacting model accuracy. To learn more about active learning and its various formulations, definitely check out the references below.

### References

1. [Settles, Burr. *Active learning literature survey*. University of Wisconsin-Madison Department of Computer Sciences, 2009.](https://minds.wisconsin.edu/handle/1793/60660)
2. [Weng, Lilian. "Learning with not Enough Data Part 2: Active Learning." Lil'Log, February 20 2022. April 29 2024.](https://lilianweng.github.io/posts/2022-02-20-active-learning/)
