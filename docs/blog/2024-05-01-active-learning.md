---
title: "Reducing Labeling Costs with Active Learning"
description: How Groundlight uses active learning to train accurate vision models while saving on data labeling costs.
slug: active-learning
authors:
  - name: Ted Sandler
    title: Senior Applied Scientist
    image_url: https://a-us.storyblok.com/f/1015187/1000x1000/efc35da152/sandlert.jpg
tags: [active learning, uncertainty sampling, deep dive]
image: ./images/active-learning/social.png
hide_table_of_contents: false
---

At Groundlight, we train each detector's machine learning (ML) model on images that have been manually labeled with correct responses. However, these labels are expensive to collect because they require human review. Given that detectors are frequently applied to streams of images that change slowly over time, reviewing all images as they arrive is likely to result in wasted effort labeling images that are similar and add little new information to the training set.

To avoid unnecessary labeling and save customers money, Groundlight uses **[active learning](https://en.wikipedia.org/wiki/Active_learning_(machine_learning))**, a machine learning protocol in which an ML model plays an active role in determining which images get manually labeled for training. With active learning, only informative images are prioritized for review, making it possible to label small a subset of the available data but train a model that's roughly as good as one trained with all the data labeled [\[Settles, 2009\]](https://minds.wisconsin.edu/handle/1793/60660).

<!-- truncate -->

The variant of active learning we use Groundlight is based on **[uncertainty sampling](https://lilianweng.github.io/posts/2022-02-20-active-learning/#uncertainty-sampling)**, a well studied and effective method that can be used in either the streaming setting or the pool-based setting in which there exists a large reservoir of unlabeled examples to draw from. We operate in the stream-based setting, where images arrive one at a time and we have to decide in the moment whether to escalate an image for review.

Uncertainty sampling works as follows. Imagine we have a detector that processes a stream of images arriving one by one. The detector's ML model is trained on all previously labeled images from the stream. When a new image arrives, the model makes its best guess prediction for the image and also reports its confidence in its prediction. The confidence is expressed as a probability (a number between zero and one) that its prediction is correct. In uncertainty sampling, we escalate and label those images whose predictions have low confidence, and largely leave images with confident predictions unlabeled. In this way, we avoid most of the expense and effort of labeling images whose predictions are likely correct, but still continue to improve the model on images it's unsure of.

As an example, the images shown below were sent to a detector that identifies the presence of dogs in and around an indoor swimming pool. The model reports with 95% confidence that there is a dog in the image on the left. But it is less confident in its response for the image on the right, saying there is no dog present with only 75% confidence. There is in fact a dog in that image, at the back left corner of the swimming pool, but it is difficult to see.
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

Assuming the detector's confidence threshold is set to a value between 75% and 95%, uncertainty sampling will escalate the image on the right for cloud labeling but not the one on the left. A user can set their detector's confidence threshold by adjusting the confidence threshold slider on the detector detail page. The image below shows the slider.
<img src={require('./images/active-learning/confidence-threshold.png').default} />
<br/>

### Label Savings with Uncertainty Sampling

We now present experimental results on a time-series dataset of images that we collected and labeled for the purpose of measuring uncertainty sampling's impact on model accuracy and labeling cost. There are 500 images of a gate, and the task is to determine for every image if the gate has been left open or closed. All images in the experiment are labeled so we know the correct response for each. But this would not be the case if we were running active learning in real life because, by design, active learning does not recruit labels on high confidence images. (In practice, however, we perform manual audits on a constant fraction of the unescalated images which serves as an additional source of labeled images.)

Our results compare the performance of three models trained under different protocols:
1. No uncertainty sampling, all images are escalated for manual review and labeling
2. Moderate uncertainty sampling, predictions less than 95% confident get escalated
3. Aggressive uncertainty sampling, only predictions below 75% confidence are escalated

The training sets of all three models are initialized with the same 20 images, 10 labeled in each class.

The plot below shows that the model trained with moderate uncertainty sampling (confidence threshold 95%) has an error rate similar to the model trained without any uncertainty sampling (confidence threshold 100%). This demonstrates that uncertainty sampling can be just as accurate as training models on all available data.
<img
 src={require('./images/active-learning/error-rate-over-time.png').default} 
 width="500 px"
/>

On the other hand, aggressive uncertainty sampling (confidence threshold 75%) does not escalate enough images for labeling, resulting in a model trained on less data that makes more mistakes. This shows how the confidence threshold controls the trade off between model accuracy and human labeling cost. Indirectly, it also demonstrates the importance of calibrating models so that their reported probabilities reflect observed frequencies and can be used as decision criteria. We calibrate machine learning models at Groundlight, though the details of model calibration are beyond the scope of this post.

Strikingly, plotting the number of images escalated by each of these models shows that active learning dramatically reduces labeling cost. The model trained without uncertainty sampling escalates all 500 of the images for review manual review. In contrast, the model trained with moderate uncertainty sampling escalates just 132 images. This is a nearly 75% reduction in manual labeling effort with little change in model error. Aggressive uncertainty sampling escalates even fewer images, just 60, but the resulting model does have noticeably higher error.
<img
 src={require('./images/active-learning/labels-over-time.png').default}
 width="500 px"
/>


## Conclusion

At Groundlight, we use active learning to reduce labeling costs for our customers. In particular, we use a variant based on uncertainty sampling that is extremely effective and easily explained. A small experiment on image time-series data shows that uncertainty sampling can dramatically reduce the number of images labeled without impacting model accuracy. To learn more about active learning and its various formulations, see the references below.

## References

1. [Settles, Burr. *Active learning literature survey*. University of Wisconsin-Madison Department of Computer Sciences, 2009.](https://minds.wisconsin.edu/handle/1793/60660)
2. [Weng, Lilian. "Learning with not Enough Data Part 2: Active Learning." Lil'Log, February 20 2022. April 29 2024.](https://lilianweng.github.io/posts/2022-02-20-active-learning/)
3. [Raj, Anant, and Francis Bach. "Convergence of uncertainty sampling for active learning." International Conference on Machine Learning. PMLR, 2022.](https://proceedings.mlr.press/v162/raj22a.html)
