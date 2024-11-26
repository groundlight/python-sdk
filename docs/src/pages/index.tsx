import Link from "@docusaurus/Link";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import HomepageFeatures from "@site/src/components/HomepageFeatures";
import Layout from "@theme/Layout";
import clsx from "clsx";
// There should be a line here that says
// import React from "react";
// VSCode might try to delete it, but that will break the site.
import React, { useState } from "react";
import '../css/style.css'

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();
  const [isActive, setIsActive] = useState(false);
  const toggleMenu = () => {
    setIsActive((prevState) => !prevState);
  };


  return (
      <header className="header">
        <div className="container">
          <div className="header-wrapper">
            <a href="" className="logo"><img src="img/dev_logo_dark.svg" alt="logo"/></a>
            <ul className={`menu ${isActive ? "active" : ""}`}>
              <li className="contain-logo"><a href="" className="logo"><img src="img/logo.png" alt=""/></a></li>
              <li className="menu-item"><a className="menu-link" href="/python-sdk/docs/getting-started">Docs</a></li>
              <li className="menu-item"><a className="menu-link" href="/python-sdk/docs/building-applications">Applications</a></li>
              <li className="menu-item"><a className="menu-link" href="/python-sdk/api-reference-docs/">API Reference</a></li>
              <li className="menu-item"><a className="menu-link" href="https://github.com/groundlight/python-sdk">GitHub</a></li>
              <li className="menu-item"><a href="https://dashboard.groundlight.ai/" className="cmn-button outline">Login</a></li>
            </ul>
            <button onClick={toggleMenu} className={`menu-toggle ${isActive ? "active" : ""}`}>
              <img className="toggle" src="img/burger-menu-right-svgrepo-com.svg" alt="menu toggle"/>
              <img className="closee" src="img/close-svgrepo-com.svg" alt="menu close"/>
            </button>
          </div>
        </div>
      </header>
  );
}

export default function Home(): JSX.Element {
  const { siteConfig } = useDocusaurusContext();

const code = `Install necessary dependencies:;
bash;
pip install groundlight framegrab;
Ask questions of your images:;

pythonimport framegrabimport groundlight;
# Initialize Groundlight client and create a Detector;
gl = groundlight.Groundlight();
det = gl.get_or_create_detector(name="doorway", query="Is the doorway open?");

# Grab an image from a camera or video stream;
grabber = framegrab.auto_discover()[0];
image = grabber.grab_frame();


# Process image and get a confident answer to the Detector's query;
iq = gl.ask_confident(det, image);
print(iq);
<show output of printed iq here>`;

  // Split the code into lines
  const codeLines = code.split("\n");

  return (
    <Layout
      title={`${siteConfig.title}`}
      description="Computer Vision powered by Natural Language"
    >
      <HomepageHeader />
      <main>
        <section className="banner-section">
          <div className="container">
            <div className="banner-wrapper">
              <h1 className="title">Build custom computer vision apps - faster & more reliably</h1>
              <div className="content">
                <p>With Groundlight’s Python SDK, you don’t need to be a machine learning scientist to develop your own
                  computer vision application. Groundlight’s fully managed computer vision solution takes care of the ML so
                  you can focus on building.</p>
                <div className="button-wrapper">
                  <a href="https://login.groundlight.ai/oauth2/register?tenantId=aad3d06b-ef57-454e-b952-91e9d3d347b1&client_id=ac8aac5d-c278-4c14-a549-e039f5ac54bb&nonce=&pendingIdPLinkId=&redirect_uri=https%3A%2F%2Fdashboard.groundlight.ai%2Fdevice-api%2Fauthz%2Fcallback&response_mode=&response_type=code&scope=openid%20profile%20email%20offline_access&state=&timezone=America%2FBogota&metaData.device.name=Windows%20Chrome&metaData.device.type=BROWSER&code_challenge=&code_challenge_method=&user_code=" className="cmn-button">Start building</a>
                  <a href="/python-sdk/docs/getting-started" className="cmn-button outline">See the docs</a>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="feature-section">
          <div className="container">
            <div className="feature-wrapper">
              <div className="feature-item">
                <div className="icon">
                  <img src="img/brain1.png" alt="img"/>
                </div>
                <div className="content">
                  <h3 className="title">AutoML</h3>
                  <p>Aspects such as selecting the model architecture, choosing hyperparameters, determining the training
                    dataset, or managing dataset labels are automated</p>
                </div>
              </div>
              <div className="feature-item">
                <div className="icon">
                  <img src="img/brain2.png" alt="img"/>
                </div>
                <div className="content">
                  <h3 className="title">24/7 Human Annotation</h3>
                  <p>No need to label all your images yourself, Groundlight system provides annotation by humans, 24/7</p>
                </div>
              </div>
              <div className="feature-item">
                <div className="icon">
                  <img src="img/brain3.png" alt="img"/>
                </div>
                <div className="content">
                  <h3 className="title">Fast Edge Inference</h3>
                  <p>On-premises deployment, so you can have real-time predictions without having to rely on the cloud</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="integration-compatibility">
          <div className="container">
            <h2 className="section-title">Groundlight <span style={{color: '#FF00D4'}}>integrations</span> and <span
                style={{color: '#991EFF'}}>compatibility</span></h2>
            <div className="integration-compatibility-wrapper">
              <div className="left-content">
                <p>Groundlight is compatible across major development platforms and available through a REST API or Python
                  SDK. Enjoy easy deployments using Arduino, Raspberry Pi, or any number of hardware kits.</p>
                <div className="logos-wrapper">
                  <img src="img/logo-nvidia.png" alt="icon"/>
                  <img src="img/logo-python.png" alt="icon"/>
                  <img src="img/logo-arduino.png" alt="icon"/>
                  <img src="img/logo-ras.png" alt="icon"/>
                  <img src="img/logo-github.png" alt="icon"/>
                  <img src="img/logo-boston-dynamics.png" alt="icon"/>
                  <img src="img/logo-aws.png" alt="icon"/>
                  <img src="img/universal-robotics-logo.png" alt="icon"/>
                </div>
              </div>
              <span className="pipe"></span>
              <div className="right-content">
                <div className="integration-compatibility-grid">
                  <div className="integration-compatibility-item">
                    <h3 className="title">Python SDK</h3>
                    <p>With only a few lines of code, you can have custom computer vision inside your application.</p>
                    <a href="/python-sdk/docs/getting-started" className="cmn-button outline">Learn More</a>
                  </div>
                  <div className="integration-compatibility-item">
                    <h3 className="title">API</h3>
                    <p>API to let you access your models in the cloud - no need to run your own models or hardware.</p>
                    <a href="/python-sdk/docs/getting-started " className="cmn-button outline">Learn More</a>
                  </div>
                  <div className="integration-compatibility-item">
                    <h3 className="title">Fast Edge Inference</h3>
                    <p>We offer specialized hardware for local inference. Reduce latency, cost, network bandwidth, and energy.
                    </p>
                    <a href="https://www.groundlight.ai/products/groundlight-hub " className="cmn-button outline">Learn More</a>
                  </div>
                  <div className="integration-compatibility-item">
                    <h3 className="title">ROS</h3>
                    <p>Seamlessly integrate AI-driven perception into ROS2 projects, enabling natural language queries and
                      real-time decision-making for smarter, more adaptable robotic systems.</p>
                    <a href="https://github.com/groundlight/groundlight_ros" className="cmn-button outline">Learn More</a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="code-section">
          <div className="container">
            <h2 className="section-title">Build a <span style={{color: "#991EFF"}}>working computer vision application</span> in just
              a few lines of code:</h2>
              <div class="code-header">
              <div class="title">Code Block</div>
              <div class="code-lang">PYTHON</div>
            </div>
            <div className="code-container">
      {/* Line numbers container */}
      <div className="line-numbers">
        {codeLines.map((_, index) => (
          <div key={index}>{index + 1}</div>
        ))}
      </div>
      {/* Code container */}
      <pre className="code-content">
        {codeLines.map((line, index) => (
          // Ensure blank lines are handled correctly
          <div key={index}>{line === "" ? " " : line}</div>
        ))}
      </pre>
    </div>
          </div>
        </section>

        <section className="support-section">
          <div className="container">
            <h2 className="section-title"><span style={{color: "#EACC8B"}}>Connect with us,</span> we’re here to support you:</h2>
            <div className="support-grid">
              <div className="support-item">
                <div className="icon">
                  <img src="img/youtube.png" alt="youtube"/>
                </div>
                <div className="content">
                  <h3 className="title">YouTube</h3>
                  <p>Watch our tutorials and learn how computer vision can be applied to various industries. </p>
                  <a href="https://www.youtube.com/@Groundlight-AI " className="cmn-button">Go to YouTube</a>
                </div>
              </div>
              <div className="support-item">
                <div className="icon">
                  <img src="img/x.png" alt="x"/>
                </div>
                <div className="content">
                  <h3 className="title">X</h3>
                  <p>Follow us at @GroundlightAI - we post about the latest in machine learning and more.</p>
                  <a href="https://x.com/GroundlightAI " className="cmn-button">Follow us on X</a>
                </div>
              </div>
              <div className="support-item">
                <div className="icon">
                  <img src="img/support.png" alt="support"/>
                </div>
                <div className="content">
                  <h3 className="title">Support</h3>
                  <p>Reach out to us for questions and get an answer from a real human being.</p>
                  <a href="support@groundlight.ai" className="cmn-button">Contact us</a>
                </div>
              </div>
            </div>
          </div>
        </section>

        <footer className="footer">
          <div className="container">
            <div className="footer-wrapper">
              <div className="footer-widget">
                <h3 className="title">Documentation</h3>
                <ul className="footer-links">
                  <li><a href="/python-sdk/docs/getting-started">Getting Started</a></li>
                  <li><a href="/python-sdk/docs/building-applications">Building Applications</a></li>
                  <li><a href="/python-sdk/docs/installation">Installation</a></li>
                </ul>
              </div>
              <div className="footer-widget">
                <h3 className="title">Company</h3>
                <ul className="footer-links">
                  <li><a href="https://www.groundlight.ai/">About</a></li>
                  <li><a href="https://www.groundlight.ai/team">Team</a></li>
                  <li><a href="https://www.groundlight.ai/careers">Careers</a></li>
                  <li><a href="https://dashboard.groundlight.ai/">Sign in</a></li>
                </ul>
              </div>
              <div className="footer-widget">
                <h3 className="title">Code</h3>
                <ul className="footer-links">
                  <li><a href="https://github.com/groundlight/">GitHub</a></li>
                  <li><a href="https://pypi.org/project/groundlight/">Python SDK</a></li>
                  <li><a href="https://github.com/groundlight/stream">Video Straming</a></li>
                  <li><a href="https://github.com/groundlight/esp32cam">Arduino</a></li>
                </ul>
              </div>
            </div>
            <div className="copyright">Copyright © 2024 Groundlight AI.</div>
          </div>
        </footer>
      </main>
    </Layout>
  );
}