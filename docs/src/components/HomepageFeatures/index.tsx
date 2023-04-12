import clsx from "clsx";
import styles from "./styles.module.css";
// There should be a line here that says
// import React from "react";
// VSCode might try to delete it, but that will break the site.
import React from "react";

type FeatureItem = {
  title: string;
  imgsrc: string;
  description: JSX.Element;
};

const FeatureList: FeatureItem[] = [
  {
    title: "Instant Models",
    imgsrc: "img/1-models.png",
    description: (
      <>
        Groundlight's Visual Large Language Model (VLLM) technology creates
        computer vision models from English instructions instead of a dataset.
        This reduces the time to get an AI-driven solution off the ground.
        Did we mention you don't need a dataset?
      </>
    ),
  },
  {
    title: "Human Reliability",

    imgsrc: "img/2-reliability.png",
    description: (
      <>
        Groundlight's models are allowed to say they're "<i>Unsure</i>" and can
        escalate to a larger model or human expert for assistance.
        By knowing what they know, Groundlight's models act more robust,
        combining the speed of AI with the reliability of human oversight.
      </>
    ),
  },
  {
    title: "Seamless MLOps",
    imgsrc: "img/3-mlops.png",
    description: (
      <>
        Because Groundlight starts with humans-in-the-loop (HITL),
        continuous monitoring and auditing are automatic.
        Any data drift is automatically detected and corrected for.
        So you know your visual applications won't fall behind as the world
        around them inevitably changes.
      </>
    ),
  },
];

function Feature({ title, imgsrc, description }: FeatureItem) {
  return (
    <div className={clsx("col col--4")}>
      <div className="text--center">
        <img src={imgsrc} width="200px" />
      </div>
      <div className="text--center padding-horiz--md">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): JSX.Element {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
