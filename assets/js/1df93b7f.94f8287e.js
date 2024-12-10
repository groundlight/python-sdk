"use strict";(self.webpackChunkcode_groundlight_ai=self.webpackChunkcode_groundlight_ai||[]).push([[4583],{8882:(e,i,s)=>{s.r(i),s.d(i,{default:()=>l});var n=s(6540);const t={container:"container_M5w6","landing-page-container":"landing-page-container_xDEE","container-fluid":"container-fluid_pNpD",cmnButton:"cmnButton_wRyG",outline:"outline_WY4x",header:"header_tggt",headerwrapper:"headerwrapper_j7IK",logo:"logo_SMK7",menutoggle:"menutoggle_Ge5Y",closee:"closee_M8ls",active:"active_s3RE",toggle:"toggle_MvTc",menu:"menu_MDwK",containlogo:"containlogo_qwHb",menuitem:"menuitem_ghrA",menulink:"menulink_kKYR",bannersection:"bannersection_NOb3",bannerwrapper:"bannerwrapper_bfS6",title:"title_tWFD",content:"content_p3lQ",buttonwrapper:"buttonwrapper_kt0C",featuresection:"featuresection_X8bb",featurewrapper:"featurewrapper_KpJw",featureitem:"featureitem_XyqN",icon:"icon_KY8h",integrationcompatibility:"integrationcompatibility_Su6f",sectiontitle:"sectiontitle_ZoWO",integrationcompatibilitywrapper:"integrationcompatibilitywrapper_nldL",leftcontent:"leftcontent_rmVJ",pipe:"pipe_kWy4",rightcontent:"rightcontent_zP7I",logoswrapper:"logoswrapper_mZC6",integrationcompatibilitygrid:"integrationcompatibilitygrid_kEMX",integrationcompatibilityitem:"integrationcompatibilityitem_JDtp",codesection:"codesection_NIgx",supportsection:"supportsection_ZlHi",supportgrid:"supportgrid_W7OH",supportitem:"supportitem_j0tv",footer:"footer_Pw4e",footerwrapper:"footerwrapper_b_Rj",footerwidget:"footerwidget_TkL9",footerlinks:"footerlinks_XRK8",copyright:"copyright_WkVg",codeheader:"codeheader_ErPA",codecontainer:"codecontainer_LYIk",linenumbers:"linenumbers_BHhc",code:"code_caOl",codecontent:"codecontent_rBL1",codeline:"codeline_m5Os"};var a=s(4848);function r(){const[e,i]=(0,n.useState)(!1);return(0,a.jsx)("header",{className:t.header,children:(0,a.jsx)("div",{className:t.container,children:(0,a.jsxs)("div",{className:t.headerwrapper,children:[(0,a.jsx)("a",{href:"",className:t.logo,children:(0,a.jsx)("img",{src:"img/dev_logo_dark.svg",alt:"logo"})}),(0,a.jsxs)("ul",{className:`${t.menu} ${e?t.active:""}`,children:[(0,a.jsx)("li",{className:t.containlogo,children:(0,a.jsx)("a",{href:"",className:t.logo,children:(0,a.jsx)("img",{src:"img/logo.png",alt:""})})}),(0,a.jsx)("li",{className:t.menuitem,children:(0,a.jsx)("a",{className:t.menulink,href:"/python-sdk/docs/getting-started",children:"Docs"})}),(0,a.jsx)("li",{className:t.menuitem,children:(0,a.jsx)("a",{className:t.menulink,href:"/python-sdk/docs/sample-applications",children:"Applications"})}),(0,a.jsx)("li",{className:t.menuitem,children:(0,a.jsx)("a",{className:t.menulink,href:"/python-sdk/api-reference-docs/",children:"API Reference"})}),(0,a.jsx)("li",{className:t.menuitem,children:(0,a.jsx)("a",{className:t.menulink,href:"https://github.com/groundlight/python-sdk",children:"GitHub"})}),(0,a.jsx)("li",{className:t.menuitem,children:(0,a.jsx)("a",{href:"https://dashboard.groundlight.ai/",className:`${t.cmnButton} ${t.outline}`,children:"Login"})})]}),(0,a.jsxs)("button",{onClick:()=>{i((e=>!e))},className:`${t.menutoggle} ${e?t.active:""}`,children:[(0,a.jsx)("img",{className:t.toggle,src:"img/burger-menu-right-svgrepo-com.svg",alt:"menu toggle"}),(0,a.jsx)("img",{className:t.closee,src:"img/close-svgrepo-com.svg",alt:"menu close"})]})]})})})}function l(){const e='import groundlight\nfrom framegrab import FrameGrabber\n\n# Initialize Groundlight client and create a Detector\ngl = groundlight.Groundlight()\ndetector = gl.get_or_create_detector(name="doorway", query="Is the doorway open?")\n\n# Grab an image from a camera or video stream\ngrabber = list(FrameGrabber.autodiscover().values())[0]\nimage = grabber.grab()\n\n# Process image and get a confident answer to the Detector\'s query\nimage_query = gl.ask_confident(detector, image)\nprint(image_query)'.split("\n");return(0,a.jsxs)("div",{className:t["landing-page-container"],children:[(0,a.jsx)(r,{}),(0,a.jsxs)("main",{children:[(0,a.jsx)("section",{className:t.bannersection,children:(0,a.jsx)("div",{className:t.container,children:(0,a.jsxs)("div",{className:t.bannerwrapper,children:[(0,a.jsx)("h1",{className:t.title,children:"Build custom computer vision apps - faster & more reliably"}),(0,a.jsxs)("div",{className:t.content,children:[(0,a.jsx)("p",{children:"With Groundlight\u2019s Python SDK, you don\u2019t need to be a machine learning scientist to develop your own computer vision application. Groundlight\u2019s fully managed computer vision solution takes care of the ML so you can focus on building."}),(0,a.jsxs)("div",{className:t.buttonwrapper,children:[(0,a.jsx)("a",{href:"https://login.groundlight.ai/oauth2/register?tenantId=aad3d06b-ef57-454e-b952-91e9d3d347b1&client_id=ac8aac5d-c278-4c14-a549-e039f5ac54bb&nonce=&redirect_uri=https%3A%2F%2Fdashboard.groundlight.ai%2Fdevice-api%2Fauthz%2Fcallback&response_type=code&scope=openid%20profile%20email%20offline_access",className:t.cmnButton,children:"Start building"}),(0,a.jsx)("a",{href:"/python-sdk/docs/getting-started",className:`${t.cmnButton} ${t.outline}`,children:"See the docs"})]})]})]})})}),(0,a.jsx)("section",{className:t.featuresection,children:(0,a.jsx)("div",{className:t.container,children:(0,a.jsxs)("div",{className:t.featurewrapper,children:[(0,a.jsxs)("div",{className:t.featureitem,children:[(0,a.jsx)("div",{className:t.icon,children:(0,a.jsx)("img",{src:"img/brain1.png",alt:"img"})}),(0,a.jsxs)("div",{className:t.content,children:[(0,a.jsx)("h3",{className:t.title,children:"AutoML"}),(0,a.jsx)("p",{children:"Aspects such as selecting the model architecture, choosing hyperparameters, determining the training dataset, or managing dataset labels are automated"})]})]}),(0,a.jsxs)("div",{className:t.featureitem,children:[(0,a.jsx)("div",{className:t.icon,children:(0,a.jsx)("img",{src:"img/brain2.png",alt:"img"})}),(0,a.jsxs)("div",{className:t.content,children:[(0,a.jsx)("h3",{className:t.title,children:"24/7 Human Annotation"}),(0,a.jsx)("p",{children:"No need to label all your images yourself, Groundlight system provides annotation by humans, 24/7"})]})]}),(0,a.jsxs)("div",{className:t.featureitem,children:[(0,a.jsx)("div",{className:t.icon,children:(0,a.jsx)("img",{src:"img/brain3.png",alt:"img"})}),(0,a.jsxs)("div",{className:t.content,children:[(0,a.jsx)("h3",{className:t.title,children:"Fast Edge Inference"}),(0,a.jsx)("p",{children:"On-premises deployment, so you can have real-time predictions without having to rely on the cloud"})]})]})]})})}),(0,a.jsx)("section",{className:t.integrationcompatibility,children:(0,a.jsxs)("div",{className:t.container,children:[(0,a.jsxs)("h2",{className:t.sectiontitle,children:["Groundlight ",(0,a.jsx)("span",{style:{color:"#FF00D4"},children:"integrations"})," and ",(0,a.jsx)("span",{style:{color:"#991EFF"},children:"compatibility"})]}),(0,a.jsxs)("div",{className:t.integrationcompatibilitywrapper,children:[(0,a.jsxs)("div",{className:t.leftcontent,children:[(0,a.jsx)("p",{children:"Groundlight is compatible across major development platforms and available through a REST API or Python SDK. Enjoy easy deployments using Arduino, Raspberry Pi, or any number of hardware kits."}),(0,a.jsxs)("div",{className:t.logoswrapper,children:[(0,a.jsx)("img",{src:"img/logo-nvidia.png",alt:"icon"}),(0,a.jsx)("img",{src:"img/logo-python.png",alt:"icon"}),(0,a.jsx)("img",{src:"img/logo-arduino.png",alt:"icon"}),(0,a.jsx)("img",{src:"img/logo-ras.png",alt:"icon"}),(0,a.jsx)("img",{src:"img/logo-github.png",alt:"icon"}),(0,a.jsx)("img",{src:"img/logo-boston-dynamics.png",alt:"icon"}),(0,a.jsx)("img",{src:"img/logo-aws.png",alt:"icon"}),(0,a.jsx)("img",{src:"img/universal-robotics-logo.png",alt:"icon"})]})]}),(0,a.jsx)("span",{className:t.pipe}),(0,a.jsx)("div",{className:t.rightcontent,children:(0,a.jsxs)("div",{className:t.integrationcompatibilitygrid,children:[(0,a.jsxs)("div",{className:t.integrationcompatibilityitem,children:[(0,a.jsx)("h3",{className:t.title,children:"Python SDK"}),(0,a.jsx)("p",{children:"With only a few lines of code, you can have custom computer vision inside your application."}),(0,a.jsx)("a",{href:"/python-sdk/docs/getting-started",className:`${t.cmnButton} ${t.outline}`,children:"Learn More"})]}),(0,a.jsxs)("div",{className:t.integrationcompatibilityitem,children:[(0,a.jsx)("h3",{className:t.title,children:"API"}),(0,a.jsx)("p",{children:"API to let you access your models in the cloud - no need to run your own models or hardware."}),(0,a.jsx)("a",{href:"/python-sdk/api-reference-docs/",className:`${t.cmnButton} ${t.outline}`,children:"Learn More"})]}),(0,a.jsxs)("div",{className:t.integrationcompatibilityitem,children:[(0,a.jsx)("h3",{className:t.title,children:"Fast Edge Inference"}),(0,a.jsx)("p",{children:"We offer specialized hardware for local inference. Reduce latency, cost, network bandwidth, and energy."}),(0,a.jsx)("a",{href:"https://www.groundlight.ai/products/groundlight-hub ",className:`${t.cmnButton} ${t.outline}`,children:"Learn More"})]}),(0,a.jsxs)("div",{className:t.integrationcompatibilityitem,children:[(0,a.jsx)("h3",{className:t.title,children:"ROS"}),(0,a.jsx)("p",{children:"Seamlessly integrate AI-driven perception into ROS2 projects, enabling natural language queries and real-time decision-making for smarter, more adaptable robotic systems."}),(0,a.jsx)("a",{href:"https://github.com/groundlight/groundlight_ros",className:`${t.cmnButton} ${t.outline}`,children:"Learn More"})]})]})})]})]})}),(0,a.jsx)("section",{className:t.codesection,children:(0,a.jsxs)("div",{className:t.container,children:[(0,a.jsxs)("h2",{className:t.sectiontitle,children:["Build a ",(0,a.jsx)("span",{style:{color:"#991EFF"},children:"working computer vision application"})," in just a few lines of code:"]}),(0,a.jsxs)("div",{className:t.codeheader,children:[(0,a.jsx)("div",{className:t.title,children:"Code Block"}),(0,a.jsx)("div",{className:t.codelang,children:"PYTHON"})]}),(0,a.jsxs)("div",{className:t.codecontainer,children:[(0,a.jsx)("div",{className:t.linenumbers,children:e.map(((e,i)=>(0,a.jsx)("div",{children:i+1},i)))}),(0,a.jsx)("pre",{className:t.codecontent,children:e.map(((e,i)=>(0,a.jsx)("div",{className:t.codeline,children:""===e?"":e},i)))})]})]})}),(0,a.jsx)("section",{className:t.supportsection,children:(0,a.jsxs)("div",{className:t.container,children:[(0,a.jsxs)("h2",{className:t.sectiontitle,children:[(0,a.jsx)("span",{style:{color:"#EACC8B"},children:"Connect with us,"})," we\u2019re here to support you:"]}),(0,a.jsxs)("div",{className:t.supportgrid,children:[(0,a.jsxs)("div",{className:t.supportitem,children:[(0,a.jsx)("div",{className:t.icon,children:(0,a.jsx)("img",{src:"img/youtube.png",alt:"youtube"})}),(0,a.jsxs)("div",{className:t.content,children:[(0,a.jsxs)("div",{children:[(0,a.jsx)("h3",{className:t.title,children:"YouTube"}),(0,a.jsx)("p",{children:"Watch our tutorials and learn how computer vision can be applied to various industries.\xa0"})]}),(0,a.jsx)("a",{href:"https://www.youtube.com/@Groundlight-AI ",className:t.cmnButton,children:"Go to YouTube"})]})]}),(0,a.jsxs)("div",{className:t.supportitem,children:[(0,a.jsx)("div",{className:t.icon,children:(0,a.jsx)("img",{src:"img/x.png",alt:"x"})}),(0,a.jsxs)("div",{className:t.content,children:[(0,a.jsxs)("div",{children:[(0,a.jsx)("h3",{className:t.title,children:"X"}),(0,a.jsx)("p",{children:"Follow us at @GroundlightAI - we post about the latest in machine learning and more."})]}),(0,a.jsx)("a",{href:"https://x.com/GroundlightAI ",className:t.cmnButton,children:"Follow us on X"})]})]}),(0,a.jsxs)("div",{className:t.supportitem,children:[(0,a.jsx)("div",{className:t.icon,children:(0,a.jsx)("img",{src:"img/support.png",alt:"support"})}),(0,a.jsxs)("div",{className:t.content,children:[(0,a.jsxs)("div",{children:[(0,a.jsx)("h3",{className:t.title,children:"Support"}),(0,a.jsx)("p",{children:"Reach out to us for questions and get an answer from a real human being."})]}),(0,a.jsx)("a",{href:"mailto:support@groundlight.ai",className:t.cmnButton,children:"Contact us"})]})]})]})]})}),(0,a.jsx)("footer",{className:t.footer,children:(0,a.jsxs)("div",{className:t.container,children:[(0,a.jsxs)("div",{className:t.footerwrapper,children:[(0,a.jsxs)("div",{className:t.footerwidget,children:[(0,a.jsx)("h3",{className:t.title,children:"Documentation"}),(0,a.jsxs)("ul",{className:t.footerlinks,children:[(0,a.jsx)("li",{children:(0,a.jsx)("a",{href:"/python-sdk/docs/getting-started",children:"Getting Started"})}),(0,a.jsx)("li",{children:(0,a.jsx)("a",{href:"/python-sdk/docs/sample-applications",children:"Building Applications"})}),(0,a.jsx)("li",{children:(0,a.jsx)("a",{href:"/python-sdk/docs/installation",children:"Installation"})})]})]}),(0,a.jsxs)("div",{className:t.footerwidget,children:[(0,a.jsx)("h3",{className:t.title,children:"Company"}),(0,a.jsxs)("ul",{className:t.footerlinks,children:[(0,a.jsx)("li",{children:(0,a.jsx)("a",{href:"https://www.groundlight.ai/",children:"About"})}),(0,a.jsx)("li",{children:(0,a.jsx)("a",{href:"https://www.groundlight.ai/team",children:"Team"})}),(0,a.jsx)("li",{children:(0,a.jsx)("a",{href:"https://www.groundlight.ai/careers",children:"Careers"})}),(0,a.jsx)("li",{children:(0,a.jsx)("a",{href:"https://dashboard.groundlight.ai/",children:"Sign in"})})]})]}),(0,a.jsxs)("div",{className:t.footerwidget,children:[(0,a.jsx)("h3",{className:t.title,children:"Code"}),(0,a.jsxs)("ul",{className:t.footerlinks,children:[(0,a.jsx)("li",{children:(0,a.jsx)("a",{href:"https://github.com/groundlight/",children:"GitHub"})}),(0,a.jsx)("li",{children:(0,a.jsx)("a",{href:"https://pypi.org/project/groundlight/",children:"Python SDK"})}),(0,a.jsx)("li",{children:(0,a.jsx)("a",{href:"https://github.com/groundlight/stream",children:"Video Straming"})}),(0,a.jsx)("li",{children:(0,a.jsx)("a",{href:"https://github.com/groundlight/esp32cam",children:"Arduino"})})]})]})]}),(0,a.jsxs)("div",{className:t.copyright,children:["Copyright \xa9 ",(new Date).getFullYear()," Groundlight AI."]})]})})]})]})}}}]);