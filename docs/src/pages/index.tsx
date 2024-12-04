import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import Layout from "@theme/Layout";
import { useLocation } from "react-router-dom";
// There should be a line here that says
// import React from "react";
// VSCode might try to delete it, but that will break the site.
import { useEffect, useState } from "react";
import baseStyles from '../css/style.module.css';
import "../css/styles.css";

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();
  const [isActive, setIsActive] = useState(false);
  const toggleMenu = () => {
    setIsActive((prevState) => !prevState);
  };


  return (
    <header className={baseStyles.munheader}>
      <div className={baseStyles.container}>
        <div className={baseStyles.headerwrapper}>
          <a href="" className={baseStyles.logo}><img src="img/dev_logo_dark.svg" alt="logo"/></a>
          <ul className={`${baseStyles.menu} ${isActive ? baseStyles.active : ""}`}>
            <li className={baseStyles.containlogo}><a href="" className={baseStyles.logo}><img src="img/logo.png" alt=""/></a></li>
            <li className={baseStyles.menuitem}><a className={baseStyles.menulink} href="/python-sdk/docs/getting-started">Docs</a></li>
            <li className={baseStyles.menuitem}><a className={baseStyles.menulink} href="/python-sdk/docs/building-applications">Applications</a></li>
            <li className={baseStyles.menuitem}><a className={baseStyles.menulink} href="/python-sdk/api-reference-docs/">API Reference</a></li>
            <li className={baseStyles.menuitem}><a className={baseStyles.menulink} href="https://github.com/groundlight/python-sdk">GitHub</a></li>
            <li className={baseStyles.menuitem}><a href="https://dashboard.groundlight.ai/" className={`${baseStyles.cmnButton} ${baseStyles.outline}`}>Login</a></li>
          </ul>
          <button onClick={toggleMenu} className={`${baseStyles.menutoggle} ${isActive ? baseStyles.active : ""}`}>
            <img className={baseStyles.toggle} src="img/burger-menu-right-svgrepo-com.svg" alt="menu toggle"/>
            <img className={baseStyles.closee} src="img/close-svgrepo-com.svg" alt="menu close"/>
          </button>
        </div>
      </div>
    </header>
  );
}

export default function Home(): JSX.Element {
  const { siteConfig } = useDocusaurusContext();

  const location = useLocation();
  const isBasePath = location.pathname === "/python-sdk/";

  useEffect(() => {
    // Add or remove the class on the <body> tag
    const mainWrapper = document.querySelector('#__docusaurus')

    if (isBasePath) {
      mainWrapper.classList.add("remove-default-components", "landing-page-container", "custom-head", "custom-a", "custom-img");
    } else {
      mainWrapper.classList.remove("remove-default-components", "landing-page-container", "custom-head", "custom-a", "custom-img");
    }
    
    // Cleanup on component unmount
    return () => {
      mainWrapper.classList.remove("remove-default-components", "landing-page-container", "custom-head", "custom-a", "custom-img");
    };
  }, [isBasePath]);

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
        <section className={baseStyles.munbannersection}>
          <div className={baseStyles.container}>
            <div className={baseStyles.bannerwrapper}>
              <h1 className={baseStyles.title}>Build custom computer vision apps - faster & more reliably</h1>
              <div className={baseStyles.content}>
                <p>With Groundlight’s Python SDK, you don’t need to be a machine learning scientist to develop your own
                  computer vision application. Groundlight’s fully managed computer vision solution takes care of the ML so
                  you can focus on building.</p>
                <div className={baseStyles.buttonwrapper}>
                  <a href="https://dashboard.groundlight.ai" className={baseStyles.cmnButton}>Start building</a>
                  <a href="/python-sdk/docs/getting-started" className={`${baseStyles.cmnButton} ${baseStyles.outline}`}>See the docs</a>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className={baseStyles.munfeaturesection}>
          <div className={baseStyles.container}>
            <div className={baseStyles.featurewrapper}>
              <div className={baseStyles.featureitem}>
                <div className={baseStyles.icon}>
                  <img src="img/brain1.png" alt="img"/>
                </div>
                <div className={baseStyles.content}>
                  <h3 className={baseStyles.title}>AutoML</h3>
                  <p>Aspects such as selecting the model architecture, choosing hyperparameters, determining the training
                    dataset, or managing dataset labels are automated</p>
                </div>
              </div>
              <div className={baseStyles.featureitem}>
                <div className={baseStyles.icon}>
                  <img src="img/brain2.png" alt="img"/>
                </div>
                <div className={baseStyles.content}>
                  <h3 className={baseStyles.title}>24/7 Human Annotation</h3>
                  <p>No need to label all your images yourself, Groundlight system provides annotation by humans, 24/7</p>
                </div>
              </div>
              <div className={baseStyles.featureitem}>
                <div className={baseStyles.icon}>
                  <img src="img/brain3.png" alt="img"/>
                </div>
                <div className={baseStyles.content}>
                  <h3 className={baseStyles.title}>Fast Edge Inference</h3>
                  <p>On-premises deployment, so you can have real-time predictions without having to rely on the cloud</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className={baseStyles.munintegrationcompatibility}>
          <div className={baseStyles.container}>
            <h2 className={baseStyles.sectiontitle}>Groundlight <span style={{color: '#FF00D4'}}>integrations</span> and <span
                style={{color: '#991EFF'}}>compatibility</span></h2>
            <div className={baseStyles.munintegrationcompatibilitywrapper}>
              <div className={baseStyles.leftcontent}>
                <p>Groundlight is compatible across major development platforms and available through a REST API or Python
                  SDK. Enjoy easy deployments using Arduino, Raspberry Pi, or any number of hardware kits.</p>
                <div className={baseStyles.logoswrapper}>
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
              <span className={baseStyles.pipe}></span>
              <div className={baseStyles.rightcontent}>
                <div className={baseStyles.munintegrationcompatibilitygrid}>
                  <div className={baseStyles.munintegrationcompatibilityitem}>
                    <h3 className={baseStyles.title}>Python SDK</h3>
                    <p>With only a few lines of code, you can have custom computer vision inside your application.</p>
                    <a href="/python-sdk/docs/getting-started" className={`${baseStyles.cmnButton} ${baseStyles.outline}`}>Learn More</a>
                  </div>
                  <div className={baseStyles.munintegrationcompatibilityitem}>
                    <h3 className={baseStyles.title}>API</h3>
                    <p>API to let you access your models in the cloud - no need to run your own models or hardware.</p>
                    <a href="/python-sdk/docs/getting-started " className={`${baseStyles.cmnButton} ${baseStyles.outline}`}>Learn More</a>
                  </div>
                  <div className={baseStyles.munintegrationcompatibilityitem}>
                    <h3 className={baseStyles.title}>Fast Edge Inference</h3>
                    <p>We offer specialized hardware for local inference. Reduce latency, cost, network bandwidth, and energy.
                    </p>
                    <a href="https://www.groundlight.ai/products/groundlight-hub " className={`${baseStyles.cmnButton} ${baseStyles.outline}`}>Learn More</a>
                  </div>
                  <div className={baseStyles.munintegrationcompatibilityitem}>
                    <h3 className={baseStyles.title}>ROS</h3>
                    <p>Seamlessly integrate AI-driven perception into ROS2 projects, enabling natural language queries and
                      real-time decision-making for smarter, more adaptable robotic systems.</p>
                    <a href="https://github.com/groundlight/groundlight_ros" className={`${baseStyles.cmnButton} ${baseStyles.outline}`}>Learn More</a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className={baseStyles.muncodesection}>
          <div className={baseStyles.container}>
            <h2 className={baseStyles.sectiontitle}>Build a <span style={{color: "#991EFF"}}>working computer vision application</span> in just
              a few lines of code:</h2>
              <div className={baseStyles.muncodeheader}>
              <div className={baseStyles.title}>Code Block</div>
              <div className={baseStyles.codelang}>PYTHON</div>
            </div>
            <div className={baseStyles.muncodecontainer}>
      {/* Line numbers container */}
      <div className={baseStyles.linenumbers}>
        {codeLines.map((_, index) => (
          <div key={index}>{index + 1}</div>
        ))}
      </div>
      {/* Code container */}
      <pre className={baseStyles.codecontent}>
        {codeLines.map((line, index) => (
          <div key={index}>{line === "" ? "" : line}</div>
        ))}
      </pre>
    </div>
          </div>
        </section>

        <section className={baseStyles.supportsection}>
          <div className={baseStyles.container}>
            <h2 className={baseStyles.sectiontitle}><span style={{color: "#EACC8B"}}>Connect with us,</span> we’re here to support you:</h2>
            <div className={baseStyles.supportgrid}>
              <div className={baseStyles.supportitem}>
                <div className={baseStyles.icon}>
                  <img src="img/youtube.png" alt="youtube"/>
                </div>
                <div className={baseStyles.content}>
                  <h3 className={baseStyles.title}>YouTube</h3>
                  <p>Watch our tutorials and learn how computer vision can be applied to various industries. </p>
                  <a href="https://www.youtube.com/@Groundlight-AI " className={baseStyles.cmnButton}>Go to YouTube</a>
                </div>
              </div>
              <div className={baseStyles.supportitem}>
                <div className={baseStyles.icon}>
                  <img src="img/x.png" alt="x"/>
                </div>
                <div className={baseStyles.content}>
                  <h3 className={baseStyles.title}>X</h3>
                  <p>Follow us at @GroundlightAI - we post about the latest in machine learning and more.</p>
                  <a href="https://x.com/GroundlightAI " className={baseStyles.cmnButton}>Follow us on X</a>
                </div>
              </div>
              <div className={baseStyles.supportitem}>
                <div className={baseStyles.icon}>
                  <img src="img/support.png" alt="support"/>
                </div>
                <div className={baseStyles.content}>
                  <h3 className={baseStyles.title}>Support</h3>
                  <p>Reach out to us for questions and get an answer from a real human being.</p>
                  <a href="support@groundlight.ai" className={baseStyles.cmnButton}>Contact us</a>
                </div>
              </div>
            </div>
          </div>
        </section>

        <footer className={baseStyles.munfooter}>
          <div className={baseStyles.container}>
            <div className={baseStyles.munfooterwrapper}>
              <div className={baseStyles.munfooterwidget}>
                <h3 className={baseStyles.title}>Documentation</h3>
                <ul className={baseStyles.footerlinks}>
                  <li><a href="/python-sdk/docs/getting-started">Getting Started</a></li>
                  <li><a href="/python-sdk/docs/building-applications">Building Applications</a></li>
                  <li><a href="/python-sdk/docs/installation">Installation</a></li>
                </ul>
              </div>
              <div className={baseStyles.munfooterwidget}>
                <h3 className={baseStyles.title}>Company</h3>
                <ul className={baseStyles.footerlinks}>
                  <li><a href="https://www.groundlight.ai/">About</a></li>
                  <li><a href="https://www.groundlight.ai/team">Team</a></li>
                  <li><a href="https://www.groundlight.ai/careers">Careers</a></li>
                  <li><a href="https://dashboard.groundlight.ai/">Sign in</a></li>
                </ul>
              </div>
              <div className={baseStyles.munfooterwidget}>
                <h3 className={baseStyles.title}>Code</h3>
                <ul className={baseStyles.footerlinks}>
                  <li><a href="https://github.com/groundlight/">GitHub</a></li>
                  <li><a href="https://pypi.org/project/groundlight/">Python SDK</a></li>
                  <li><a href="https://github.com/groundlight/stream">Video Straming</a></li>
                  <li><a href="https://github.com/groundlight/esp32cam">Arduino</a></li>
                </ul>
              </div>
            </div>
            <div className={baseStyles.copyright}>Copyright © 2024 Groundlight AI.</div>
          </div>
        </footer>
      </main>
    </Layout>
  );
}