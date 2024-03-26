"use strict";(self.webpackChunkweb=self.webpackChunkweb||[]).push([[9555],{281:(e,t,i)=>{i.r(t),i.d(t,{assets:()=>l,contentTitle:()=>r,default:()=>g,frontMatter:()=>s,metadata:()=>o,toc:()=>c});var n=i(5893),a=i(1151);const s={title:"Navigating the Ambiguity with Groundlight AI Detectors",description:"Let's talk more about ambiguous image queries",slug:"dealing-with-unclear-images",authors:[{name:"Sharmila Reddy Nangi",title:"Applied ML Scientist",image_url:"https://a-us.storyblok.com/f/1015187/1000x1000/b66d1cddeb/nangis.jpg"}],tags:["unclears","real world ambiguity"],image:"./images/unclear_blog/unclear_label.png",hide_table_of_contents:!1},r=void 0,o={permalink:"/python-sdk/blog/dealing-with-unclear-images",editUrl:"https://github.com/groundlight/python-sdk/tree/main/docs/blog/blog/2024-03-20-unclear-blog.md",source:"@site/blog/2024-03-20-unclear-blog.md",title:"Navigating the Ambiguity with Groundlight AI Detectors",description:"Let's talk more about ambiguous image queries",date:"2024-03-20T00:00:00.000Z",formattedDate:"March 20, 2024",tags:[{label:"unclears",permalink:"/python-sdk/blog/tags/unclears"},{label:"real world ambiguity",permalink:"/python-sdk/blog/tags/real-world-ambiguity"}],readingTime:3.14,hasTruncateMarker:!1,authors:[{name:"Sharmila Reddy Nangi",title:"Applied ML Scientist",image_url:"https://a-us.storyblok.com/f/1015187/1000x1000/b66d1cddeb/nangis.jpg",imageURL:"https://a-us.storyblok.com/f/1015187/1000x1000/b66d1cddeb/nangis.jpg"}],frontMatter:{title:"Navigating the Ambiguity with Groundlight AI Detectors",description:"Let's talk more about ambiguous image queries",slug:"dealing-with-unclear-images",authors:[{name:"Sharmila Reddy Nangi",title:"Applied ML Scientist",image_url:"https://a-us.storyblok.com/f/1015187/1000x1000/b66d1cddeb/nangis.jpg",imageURL:"https://a-us.storyblok.com/f/1015187/1000x1000/b66d1cddeb/nangis.jpg"}],tags:["unclears","real world ambiguity"],image:"./images/unclear_blog/unclear_label.png",hide_table_of_contents:!1},unlisted:!1,nextItem:{title:"Building your first computer vision model just got easier",permalink:"/python-sdk/blog/getting-started"}},l={image:i(2307).Z,authorsImageUrls:[void 0]},c=[{value:"Exploring the Gray Areas: Real-World Examples:",id:"exploring-the-gray-areas-real-world-examples",level:2},{value:"Strategies for Navigating Ambiguity:",id:"strategies-for-navigating-ambiguity",level:2}];function d(e){const t={a:"a",h2:"h2",li:"li",ol:"ol",p:"p",strong:"strong",...(0,a.a)(),...e.components};return(0,n.jsxs)(n.Fragment,{children:[(0,n.jsx)(t.p,{children:'When you first explore the capabilities of our Groundlight AI detectors, you\'ll quickly notice that they excel at answering binary questions. These are queries expecting a straightforward "Yes" or "No" response. However, the world around us rarely conforms to such black-and-white distinctions, particularly when analyzing images. In reality, many scenarios present challenges that defy a simple binary answer.'}),"\n",(0,n.jsx)(t.h2,{id:"exploring-the-gray-areas-real-world-examples",children:"Exploring the Gray Areas: Real-World Examples:"}),"\n",(0,n.jsx)(t.p,{children:"Consider the following scenarios that highlight the complexity of interpreting real-world images:"}),"\n",(0,n.jsxs)(t.ol,{children:["\n",(0,n.jsxs)(t.li,{children:[(0,n.jsx)(t.strong,{children:"The Case of the Hidden Oven"}),': Imagine asking, "Is the oven light turned on?" only to find the view partially blocked by a person. With the contents on the other side hidden from view, providing a definitive "Yes" or "No" becomes impossible. Such instances are best described as "Unclear."']}),"\n"]}),"\n",(0,n.jsxs)("figure",{style:{textAlign:"center"},children:[(0,n.jsx)("img",{src:i(2923).Z,width:"350px"}),(0,n.jsx)("figcaption",{children:(0,n.jsx)("small",{children:(0,n.jsx)(t.p,{children:"Oven is hidden from the camera view"})})})]}),"\n",(0,n.jsxs)(t.ol,{start:"2",children:["\n",(0,n.jsxs)(t.li,{children:[(0,n.jsx)(t.strong,{children:"The Locked Garage Door Dilemma"}),': When faced with a query like, "Is the garage door locked?" accompanied by an image shrouded in darkness or blurred beyond recognition, identifying the status of the door lock is a challenge. In these circumstances, clarity eludes us, leaving us unable to confidently answer.']}),"\n"]}),"\n",(0,n.jsxs)("figure",{style:{textAlign:"center"},children:[(0,n.jsx)("img",{src:i(8189).Z,width:"350px"}),(0,n.jsx)("figcaption",{children:(0,n.jsx)("small",{children:(0,n.jsx)(t.p,{children:"Dark images make it difficult to answer the query"})})})]}),"\n",(0,n.jsxs)(t.ol,{start:"3",children:["\n",(0,n.jsxs)(t.li,{children:[(0,n.jsx)(t.strong,{children:"Irrelevant Imagery"}),': At times, the images presented may bear no relation to the question posed. These irrelevant scenes further underscore the limitations of binary responses in complex situations. For instance, responding to the question "Is there a black jacket on the coat hanger?" with the following image (that doesn\'t even include a coat hanger) exemplifies how such imagery can be off-topic and fail to address the query appropriately.']}),"\n"]}),"\n",(0,n.jsxs)("figure",{style:{textAlign:"center"},children:[(0,n.jsx)("img",{src:i(570).Z,width:"350px"}),(0,n.jsx)("figcaption",{children:(0,n.jsx)("small",{children:(0,n.jsx)(t.p,{children:"Images unrelated to the query lead to ambiguity"})})})]}),"\n",(0,n.jsx)(t.h2,{id:"strategies-for-navigating-ambiguity",children:"Strategies for Navigating Ambiguity:"}),"\n",(0,n.jsx)(t.p,{children:"Although encountering unclear images might seem like a setback, it actually opens up avenues for improvement and customization. Our detectors are designed to identify and flag these ambiguous cases, empowering you to steer their interpretation. Here are some strategies you can employ to enhance the process:"}),"\n",(0,n.jsxs)(t.ol,{children:["\n",(0,n.jsxs)(t.li,{children:[(0,n.jsx)(t.strong,{children:"Clarify your queries"})," : It's crucial to formulate your questions to the system with precision, avoiding any vagueness. For instance, instead of asking, \u201cIs the light ON?\u201d opt for a more detailed inquiry such as, \u201cCan you clearly see the red LED on the right panel turned ON?\u201d This approach ensures your queries are direct and specific."]}),"\n",(0,n.jsxs)(t.li,{children:[(0,n.jsx)(t.strong,{children:"Customize Yes/ No classifications"}),": You can specify how the model should interpret and deal with unclear images by reframing your queries and notes. For instance, by specifying \u201cIf the garage door is not visible, mark it as a NO\u201d in your notes, you can make the detector sort unclear images into the \u201cNO\u201d class. You can refer to our ",(0,n.jsx)(t.a,{href:"https://code.groundlight.ai/python-sdk/blog/best-practices",children:"previous blog post"})," for best practices while refining your queries and notes."]}),"\n",(0,n.jsxs)(t.li,{children:[(0,n.jsx)(t.strong,{children:"Flagging \u201cUnclear\u201d images"}),': Should you prefer to classify an obstructed view or irrelevant imagery as \u201cUnclear\u201d, simply add a couple of labels as \u201cUNCLEAR\u201d or provide instructions in the notes. Groundlight\'s machine learning systems will adapt to your preference and continue to flag them as "Unclear" for you.']}),"\n"]}),"\n",(0,n.jsxs)("figure",{style:{textAlign:"center"},children:[(0,n.jsx)("img",{src:i(8468).Z,width:"350px",class:"center"}),(0,n.jsx)("figcaption",{children:(0,n.jsx)("small",{children:(0,n.jsx)(t.p,{children:'Marking an image query as \u201cUnclear" in the data review page'})})})]}),"\n",(0,n.jsx)(t.p,{children:"The strategies outlined above will significantly improve your ability to navigate through unclear\nscenarios. However, there exist many other situations, such as borderline classifications or cases where there's insufficient information for a definitive answer. Recognizing and managing the inherent uncertainty in these tasks is crucial as we progress. We are committed to building more tools that empower you to deal with these challenges."})]})}function g(e={}){const{wrapper:t}={...(0,a.a)(),...e.components};return t?(0,n.jsx)(t,{...e,children:(0,n.jsx)(d,{...e})}):d(e)}},2307:(e,t,i)=>{i.d(t,{Z:()=>n});const n=i.p+"assets/images/unclear_label-caa7bfe352df67a9cb4611894807b14a.png"},8189:(e,t,i)=>{i.d(t,{Z:()=>n});const n=i.p+"assets/images/dark_door-2c9df78f2745af46f8c13280a3317ac6.png"},2923:(e,t,i)=>{i.d(t,{Z:()=>n});const n=i.p+"assets/images/hidden_oven-b7fdb5b37f74a65ebf99fc30d11cd238.png"},8468:(e,t,i)=>{i.d(t,{Z:()=>n});const n=i.p+"assets/images/unclear_label-caa7bfe352df67a9cb4611894807b14a.png"},570:(e,t,i)=>{i.d(t,{Z:()=>n});const n=i.p+"assets/images/unrelated_img-e2fbf4a7e7018cc3df9d90713bf17d86.png"},1151:(e,t,i)=>{i.d(t,{Z:()=>o,a:()=>r});var n=i(7294);const a={},s=n.createContext(a);function r(e){const t=n.useContext(s);return n.useMemo((function(){return"function"==typeof e?e(t):{...t,...e}}),[t,e])}function o(e){let t;return t=e.disableParentContext?"function"==typeof e.components?e.components(a):e.components||a:r(e.components),n.createElement(s.Provider,{value:t},e.children)}}}]);