"use strict";(self.webpackChunkweb=self.webpackChunkweb||[]).push([[201],{3905:(e,t,n)=>{n.d(t,{Zo:()=>u,kt:()=>g});var r=n(7294);function a(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function o(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);t&&(r=r.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,r)}return n}function i(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?o(Object(n),!0).forEach((function(t){a(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):o(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function l(e,t){if(null==e)return{};var n,r,a=function(e,t){if(null==e)return{};var n,r,a={},o=Object.keys(e);for(r=0;r<o.length;r++)n=o[r],t.indexOf(n)>=0||(a[n]=e[n]);return a}(e,t);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(e);for(r=0;r<o.length;r++)n=o[r],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(a[n]=e[n])}return a}var s=r.createContext({}),p=function(e){var t=r.useContext(s),n=t;return e&&(n="function"==typeof e?e(t):i(i({},t),e)),n},u=function(e){var t=p(e.components);return r.createElement(s.Provider,{value:t},e.children)},m="mdxType",c={inlineCode:"code",wrapper:function(e){var t=e.children;return r.createElement(r.Fragment,{},t)}},d=r.forwardRef((function(e,t){var n=e.components,a=e.mdxType,o=e.originalType,s=e.parentName,u=l(e,["components","mdxType","originalType","parentName"]),m=p(n),d=a,g=m["".concat(s,".").concat(d)]||m[d]||c[d]||o;return n?r.createElement(g,i(i({ref:t},u),{},{components:n})):r.createElement(g,i({ref:t},u))}));function g(e,t){var n=arguments,a=t&&t.mdxType;if("string"==typeof e||a){var o=n.length,i=new Array(o);i[0]=d;var l={};for(var s in t)hasOwnProperty.call(t,s)&&(l[s]=t[s]);l.originalType=e,l[m]="string"==typeof e?e:a,i[1]=l;for(var p=2;p<o;p++)i[p]=n[p];return r.createElement.apply(null,i)}return r.createElement.apply(null,n)}d.displayName="MDXCreateElement"},688:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>s,contentTitle:()=>i,default:()=>c,frontMatter:()=>o,metadata:()=>l,toc:()=>p});var r=n(7462),a=(n(7294),n(3905));const o={},i="A Quick Example: Live Stream Alert",l={unversionedId:"getting-started/streaming",id:"getting-started/streaming",title:"A Quick Example: Live Stream Alert",description:"A quick example to get used to setting up detectors and asking good questions: set up a monitor on a live stream.",source:"@site/docs/getting-started/5-streaming.md",sourceDirName:"getting-started",slug:"/getting-started/streaming",permalink:"/python-sdk/docs/getting-started/streaming",draft:!1,editUrl:"https://github.com/groundlight/python-sdk/tree/main/docs/docs/getting-started/5-streaming.md",tags:[],version:"current",sidebarPosition:5,frontMatter:{},sidebar:"tutorialSidebar",previous:{title:"A Fun Example: Dog-on-Couch Detector",permalink:"/python-sdk/docs/getting-started/dog-on-couch"},next:{title:"Building Applications",permalink:"/python-sdk/docs/building-applications/"}},s={},p=[{value:"Requirements",id:"requirements",level:2},{value:"Installation",id:"installation",level:2},{value:"Creating the Application",id:"creating-the-application",level:2}],u={toc:p},m="wrapper";function c(e){let{components:t,...n}=e;return(0,a.kt)(m,(0,r.Z)({},u,n,{components:t,mdxType:"MDXLayout"}),(0,a.kt)("h1",{id:"a-quick-example-live-stream-alert"},"A Quick Example: Live Stream Alert"),(0,a.kt)("p",null,"A quick example to get used to setting up detectors and asking good questions: set up a monitor on a live stream. "),(0,a.kt)("h2",{id:"requirements"},"Requirements"),(0,a.kt)("ul",null,(0,a.kt)("li",{parentName:"ul"},(0,a.kt)("a",{parentName:"li",href:"/docs/installation/"},"Groundlight SDK")," with Python 3.7 or higher"),(0,a.kt)("li",{parentName:"ul"},"The video ID of a YouTube live stream you'd like to monitor")),(0,a.kt)("h2",{id:"installation"},"Installation"),(0,a.kt)("p",null,"Ensure you have Python 3.7 or higher installed, and then install the Groundlight SDK and OpenCV library:"),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-bash"},"pip install groundlight pillow ffmpeg yt-dlp typer\n")),(0,a.kt)("h2",{id:"creating-the-application"},"Creating the Application"),(0,a.kt)("ol",null,(0,a.kt)("li",{parentName:"ol"},"Save this command as a shell script ",(0,a.kt)("inlineCode",{parentName:"li"},"get_latest_frame.sh"),":")),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre"},'#!/bin/bash\n\nffmpeg -i "$(yt-dlp -g $1 | head -n 1)" -vframes 1 last.jpg -y\n')),(0,a.kt)("p",null,"This will download the most recent frame from a YouTube live stream and save it to a local file ",(0,a.kt)("inlineCode",{parentName:"p"},"last.jpg"),". "),(0,a.kt)("ol",{start:2},(0,a.kt)("li",{parentName:"ol"},(0,a.kt)("p",{parentName:"li"},"Log in to the ",(0,a.kt)("a",{parentName:"p",href:"https://app.groundlight.ai"},"Groundlight application")," and get an ",(0,a.kt)("a",{parentName:"p",href:"api-tokens"},"API Token"),".")),(0,a.kt)("li",{parentName:"ol"},(0,a.kt)("p",{parentName:"li"},"Next, we'll write the Python script for the application."))),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-python",metastring:"notest",notest:!0},'import os\nimport subprocess\nimport typer\nfrom groundlight import Groundlight\nfrom PIL import Image\n\n\ndef main(*, video_id: str = None, detector_name: str = None, query: str = None, confidence: float = 0.75, wait: int = 60):\n    """\n    Run the script to get the stream\'s last frame as a subprocess, and submit result as an image query to a Groundlight detector\n    :param video_id: Video ID of the YouTube live stream (the URLs have the form https://www.youtube.com/watch?v=<VIDEO_ID>)\n    :param detector_name: Name for your Groundlight detector\n    :param query: Question you want to ask of the stream (we will alert on the answer of NO)\n    """\n    gl = Groundlight()\n    detector = gl.create_detector(name=detector_name, query=query, confidence_threshold=confidence)\n\n    while True:\n        p = subprocess.run(["./get_latest_frame.sh", video_id])\n        if p.returncode != 0:\n            raise RuntimeError(f"Could not get image from video ID: {video_id}. Process exited with return code {p.returncode}.")\n        \n        image = Image.open("last.jpg").convert("RGB")\n        response = gl.submit_image_query(detector=detector, image=image, wait=wait)\n\n        if response.result.label == "NO":\n            os.system("say \'Alert!\'") # this may not work on all operating systems\n\n\nif __name__ == "__main__":\n    typer.run(main)\n\n')),(0,a.kt)("ol",{start:4},(0,a.kt)("li",{parentName:"ol"},"Save the script as ",(0,a.kt)("inlineCode",{parentName:"li"},"streaming_alert.py")," in the same directory as ",(0,a.kt)("inlineCode",{parentName:"li"},"get_latest_frame.sh")," above and run it:")),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-bash"},"python streaming_alert.py <VIDEO_ID> --detector_name <DETECTOR_NAME> --query <QUERY IN QUOTATION MARKS>\n")))}c.isMDXComponent=!0}}]);