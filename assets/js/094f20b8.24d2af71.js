"use strict";(self.webpackChunkweb=self.webpackChunkweb||[]).push([[9604],{7879:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>d,contentTitle:()=>a,default:()=>u,frontMatter:()=>r,metadata:()=>s,toc:()=>l});var i=n(5893),o=n(1151);const r={title:"Building your first computer vision model just got easier",slug:"getting-started",authors:[{name:"Sunil Kumar",title:"Machine Learning Engineer",image_url:"https://a-us.storyblok.com/f/1015187/1000x1000/a265e322bd/kumars.jpg"}],tags:["Getting started","Groundlight Python SDK"],image:"./images/getting_started/cvme1.jpg",hide_table_of_contents:!1},a=void 0,s={permalink:"/python-sdk/blog/getting-started",editUrl:"https://github.com/groundlight/python-sdk/tree/main/docs/blog/blog/2024-02-15-getting_started.md",source:"@site/blog/2024-02-15-getting_started.md",title:"Building your first computer vision model just got easier",description:"We're thrilled to announce a new repository that makes it incredibly easy for anyone to get started for free with Groundlight, a computer vision (CV) platform powered by natural language. This first steps guide is designed to walk you through setting up your first Groundlight detector to answer a simple question: \"Is the door open?\" Behind the scenes, Groundlight will automatically train and deploy a computer vision model that can answer this question in real time. With our escalation technology, you don't need to provide any labeled data - you get answers from your first image submission.",date:"2024-02-15T00:00:00.000Z",formattedDate:"February 15, 2024",tags:[{label:"Getting started",permalink:"/python-sdk/blog/tags/getting-started"},{label:"Groundlight Python SDK",permalink:"/python-sdk/blog/tags/groundlight-python-sdk"}],readingTime:2.925,hasTruncateMarker:!0,authors:[{name:"Sunil Kumar",title:"Machine Learning Engineer",image_url:"https://a-us.storyblok.com/f/1015187/1000x1000/a265e322bd/kumars.jpg",imageURL:"https://a-us.storyblok.com/f/1015187/1000x1000/a265e322bd/kumars.jpg"}],frontMatter:{title:"Building your first computer vision model just got easier",slug:"getting-started",authors:[{name:"Sunil Kumar",title:"Machine Learning Engineer",image_url:"https://a-us.storyblok.com/f/1015187/1000x1000/a265e322bd/kumars.jpg",imageURL:"https://a-us.storyblok.com/f/1015187/1000x1000/a265e322bd/kumars.jpg"}],tags:["Getting started","Groundlight Python SDK"],image:"./images/getting_started/cvme1.jpg",hide_table_of_contents:!1},unlisted:!1,prevItem:{title:"Navigating the Ambiguity with Groundlight AI Detectors",permalink:"/python-sdk/blog/dealing-with-unclear-images"},nextItem:{title:"The Grime Guardian: Building Stateful Multi-camera applications with Groundlight",permalink:"/python-sdk/blog/grime-guardian"}},d={image:n(6988).Z,authorsImageUrls:[void 0]},l=[{value:"What is Groundlight?",id:"what-is-groundlight",level:2},{value:"What&#39;s Inside?",id:"whats-inside",level:2},{value:"How do I get started?",id:"how-do-i-get-started",level:2},{value:"We&#39;re Here to Help!",id:"were-here-to-help",level:2}];function h(e){const t={a:"a",code:"code",h2:"h2",img:"img",p:"p",pre:"pre",...(0,o.a)(),...e.components};return(0,i.jsxs)(i.Fragment,{children:[(0,i.jsxs)(t.p,{children:["We're thrilled to announce a new ",(0,i.jsx)(t.a,{href:"https://github.com/groundlight/getting_started",children:"repository"}),' that makes it incredibly easy for anyone to get started for free with Groundlight, a computer vision (CV) platform powered by natural language. This first steps guide is designed to walk you through setting up your first Groundlight detector to answer a simple question: "Is the door open?" Behind the scenes, Groundlight will automatically train and deploy a computer vision model that can answer this question in real time. With our escalation technology, you don\'t need to provide any labeled data - you get answers from your first image submission.']}),"\n",(0,i.jsx)(t.p,{children:(0,i.jsx)(t.a,{href:"https://github.com/groundlight/getting_started",children:(0,i.jsx)(t.img,{src:"https://gh-card.dev/repos/groundlight/getting_started.svg",alt:"groundlight/getting_started - GitHub"})})}),"\n",(0,i.jsx)(t.h2,{id:"what-is-groundlight",children:"What is Groundlight?"}),"\n",(0,i.jsxs)(t.p,{children:["Groundlight offers a truly modern take on computer vision, combining the best AI models with real-time human supervision in the cloud. Our Escalation Technology automatically chooses the best solution for your problem - whether that's a traditional CV model like an ",(0,i.jsx)(t.a,{href:"https://pytorch.org/hub/nvidia_deeplearningexamples_efficientnet/",children:"EfficentNet"})," on the edge, a powerful Visual LLM in the cloud, or a live sensible human monitor. The result is fairly incredible if you're used to the traditional ",(0,i.jsx)(t.code,{children:'["gather data", "train model", "evaluate", "repeat"]'})," pattern of machine learning.  Instead, Groundlight empowers you to just phrase the visual question you want answered in English, send in images, and Groundlight provides confidence-calibrated answers.  At first, the answers will be slow and/or unconfident, but after not very many examples you're using a customized CV model trained just for your task."]}),"\n",(0,i.jsxs)("figure",{children:[(0,i.jsx)("img",{src:n(755).Z}),(0,i.jsx)("figcaption",{children:(0,i.jsx)("small",{children:(0,i.jsx)(t.p,{children:"Groundlight's escalation technology backs every question you ask Groundlight. Escalation ensures we find the best answer for your question, every time."})})})]}),"\n",(0,i.jsx)(t.h2,{id:"whats-inside",children:"What's Inside?"}),"\n",(0,i.jsxs)(t.p,{children:["Our ",(0,i.jsx)(t.a,{href:"https://github.com/groundlight/getting_started",children:"getting started repository"})," provides an easy to understand Python codebase that you can run on any modern computer (including a Raspberry Pi). It captures images from a camera of your choice (by default your webcam) and uses Groundlight to continuously train and deploy a computer vision model that determines if your door is open or closed. Whether you're just starting out or a seasoned developer, this example is crafted to provide a smooth introduction to integrating Groundlight into your projects and provide a springboard for building advanced applications with Groundlight."]}),"\n",(0,i.jsxs)(t.p,{children:["The ",(0,i.jsx)(t.code,{children:"main.py"})," file could hardly be simpler.  First you just initialize the camera and your Groundlight detector:"]}),"\n",(0,i.jsx)(t.pre,{children:(0,i.jsx)(t.code,{className:"language-python",metastring:"notest",children:'camera = setup_camera()\n\ngl = Groundlight()\n\nquery_text = "Is the door open? This includes if the door is only partially open."\n\ndetector_name = "door_open_detector"\n\ndetector = gl.get_or_create_detector(\n    name=detector_name,\n    query=query_text,\n)\n'})}),"\n",(0,i.jsx)(t.p,{children:"and then a simple infinite loop to send images from the camera to your detector:"}),"\n",(0,i.jsx)(t.pre,{children:(0,i.jsx)(t.code,{className:"language-python",metastring:"notest",children:'try:\n    while True:\n        image = camera.grab()\n\n        image_query = gl.ask_ml(detector=detector, image=image)\n        \n        print(f"The answer to the query is {image_query.result.label.value}")\n\n        sleep(10)\nfinally:\n    camera.release()\n'})}),"\n",(0,i.jsx)(t.h2,{id:"how-do-i-get-started",children:"How do I get started?"}),"\n",(0,i.jsxs)(t.p,{children:["Visit the ",(0,i.jsx)(t.a,{href:"https://github.com/groundlight/getting_started",children:"repository"})," and follow the steps in the ",(0,i.jsx)(t.code,{children:"README"}),". After trying it out, we encourage you to modify the code to solve a real world problem you experience. Doing so should be as simple as changing the ",(0,i.jsx)(t.code,{children:"query"})," you ask Groundlight. See the ",(0,i.jsx)(t.code,{children:"Learning More - Additional Resources"})," section of the ",(0,i.jsx)(t.code,{children:"README"})," for more information. If you want to learn more about the Groundlight Python SDK, which is used to power this repository, check out our ",(0,i.jsx)(t.a,{href:"https://github.com/groundlight/python-sdk",children:"SDK"})," or visit the ",(0,i.jsx)(t.a,{href:"https://code.groundlight.ai/python-sdk/docs/getting-started",children:"documentation"}),"."]}),"\n",(0,i.jsx)(t.h2,{id:"were-here-to-help",children:"We're Here to Help!"}),"\n",(0,i.jsxs)(t.p,{children:["Got questions? We're eager to assist! Reach out to us through email (",(0,i.jsx)(t.a,{href:"mailto:support@groundlight.ai",children:"support@groundlight.ai"}),"), or chat on the ",(0,i.jsx)(t.a,{href:"https://app.groundlight.ai",children:"Groundlight web app"})," - a Groundlight engineer or scientist is available to help every weekday during business hours."]}),"\n",(0,i.jsx)(t.p,{children:"We can't wait to see what you build with Groundlight!"})]})}function u(e={}){const{wrapper:t}={...(0,o.a)(),...e.components};return t?(0,i.jsx)(t,{...e,children:(0,i.jsx)(h,{...e})}):h(e)}},6988:(e,t,n)=>{n.d(t,{Z:()=>i});const i=n.p+"assets/images/cvme1-eabc644cb5714c29144965632c5ff11e.jpg"},755:(e,t,n)=>{n.d(t,{Z:()=>i});const i=n.p+"assets/images/escalation_diagram-05fa7abe4f95261f01a79faf002e0925.jpg"},1151:(e,t,n)=>{n.d(t,{Z:()=>s,a:()=>a});var i=n(7294);const o={},r=i.createContext(o);function a(e){const t=i.useContext(r);return i.useMemo((function(){return"function"==typeof e?e(t):{...t,...e}}),[t,e])}function s(e){let t;return t=e.disableParentContext?"function"==typeof e.components?e.components(o):e.components||o:a(e.components),i.createElement(r.Provider,{value:t},e.children)}}}]);