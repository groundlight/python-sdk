"use strict";(self.webpackChunkweb=self.webpackChunkweb||[]).push([[3571],{4373:(e,n,t)=>{t.r(n),t.d(n,{assets:()=>c,contentTitle:()=>a,default:()=>u,frontMatter:()=>r,metadata:()=>s,toc:()=>l});var i=t(5893),o=t(1151);const r={sidebar_position:3},a="Confidence Levels",s={id:"building-applications/managing-confidence",title:"Confidence Levels",description:"Groundlight gives you a simple way to control the trade-off of latency against accuracy. The longer you can wait for an answer to your image query, the better accuracy you can get. In particular, if the ML models are unsure of the best response, they will escalate the image query to more intensive analysis with more complex models and real-time human monitors as needed. Your code can easily wait for this delayed response. Either way, these new results are automatically trained into your models so your next queries will get better results faster.",source:"@site/docs/building-applications/4-managing-confidence.md",sourceDirName:"building-applications",slug:"/building-applications/managing-confidence",permalink:"/python-sdk/docs/building-applications/managing-confidence",draft:!1,unlisted:!1,editUrl:"https://github.com/groundlight/python-sdk/tree/main/docs/docs/building-applications/4-managing-confidence.md",tags:[],version:"current",sidebarPosition:3,frontMatter:{sidebar_position:3},sidebar:"tutorialSidebar",previous:{title:"Working with Detectors",permalink:"/python-sdk/docs/building-applications/working-with-detectors"},next:{title:"Handling Server Errors",permalink:"/python-sdk/docs/building-applications/handling-errors"}},c={},l=[];function d(e){const n={admonition:"admonition",code:"code",h1:"h1",p:"p",pre:"pre",...(0,o.a)(),...e.components};return(0,i.jsxs)(i.Fragment,{children:[(0,i.jsx)(n.h1,{id:"confidence-levels",children:"Confidence Levels"}),"\n",(0,i.jsx)(n.p,{children:"Groundlight gives you a simple way to control the trade-off of latency against accuracy. The longer you can wait for an answer to your image query, the better accuracy you can get. In particular, if the ML models are unsure of the best response, they will escalate the image query to more intensive analysis with more complex models and real-time human monitors as needed. Your code can easily wait for this delayed response. Either way, these new results are automatically trained into your models so your next queries will get better results faster."}),"\n",(0,i.jsx)(n.p,{children:"The desired confidence level is set as the escalation threshold on your detector. This determines the minimum confidence score for the ML system to provide before the image query is escalated."}),"\n",(0,i.jsx)(n.p,{children:"For example, say you want to set your desired confidence level to 0.95, but that you're willing to wait up to 60 seconds to get a confident response."}),"\n",(0,i.jsx)(n.pre,{children:(0,i.jsx)(n.code,{className:"language-python",metastring:"notest",children:'from groundlight import Groundlight\nfrom PIL import Image\nimport requests\n\ngl = Groundlight()\nimage_url = "https://www.photos-public-domain.com/wp-content/uploads/2010/11/over_flowing_garbage_can.jpg"\nimage = Image.open(requests.get(image_url, stream=True).raw)\n\n# highlight-start\nd = gl.get_or_create_detector(name="trash", query="Is the trash can full?", confidence_threshold=0.95)\n\n# This will wait until either 60 seconds have passed or the confidence reaches 0.95\nimage_query = gl.submit_image_query(detector=d, image=image, wait=60)\n# highlight-end\n\nprint(f"The answer is {image_query.result}")\n'})}),"\n",(0,i.jsx)(n.admonition,{type:"tip",children:(0,i.jsx)(n.p,{children:"Tuning confidence lets you balance accuracy against latency.\nHigher confidence will get higher accuracy, but will generally require higher latency.\nHigher confidence also requires more labels, which increases labor costs."})}),"\n",(0,i.jsxs)(n.p,{children:["Or if you want to execute ",(0,i.jsx)(n.code,{children:"submit_image_query"})," as fast as possible, set ",(0,i.jsx)(n.code,{children:"wait=0"}),". You will either get the ML results or a placeholder response if the ML model hasn't finished executing. Image queries which are below the desired confidence level will still be escalated for further analysis, and the results are incorporated as training data to improve your ML model, but your code will not wait for that to happen."]}),"\n",(0,i.jsx)(n.pre,{children:(0,i.jsx)(n.code,{className:"language-python",metastring:"notest continuation",children:"image_query = gl.submit_image_query(detector=d, image=image, wait=0)\n"})}),"\n",(0,i.jsx)(n.p,{children:"If the returned result was generated from an ML model, you can see the confidence score returned for the image query:"}),"\n",(0,i.jsx)(n.pre,{children:(0,i.jsx)(n.code,{className:"language-python",metastring:"notest continuation",children:'print(f"The confidence is {image_query.result.confidence}")\n'})})]})}function u(e={}){const{wrapper:n}={...(0,o.a)(),...e.components};return n?(0,i.jsx)(n,{...e,children:(0,i.jsx)(d,{...e})}):d(e)}},1151:(e,n,t)=>{t.d(n,{Z:()=>s,a:()=>a});var i=t(7294);const o={},r=i.createContext(o);function a(e){const n=i.useContext(r);return i.useMemo((function(){return"function"==typeof e?e(n):{...n,...e}}),[n,e])}function s(e){let n;return n=e.disableParentContext?"function"==typeof e.components?e.components(o):e.components||o:a(e.components),i.createElement(r.Provider,{value:n},e.children)}}}]);