"use strict";(self.webpackChunkcode_groundlight_ai=self.webpackChunkcode_groundlight_ai||[]).push([[2260],{2326:(e,t,a)=>{a.r(t),a.d(t,{assets:()=>l,contentTitle:()=>s,default:()=>u,frontMatter:()=>r,metadata:()=>n,toc:()=>c});var n=a(7395),o=a(4848),i=a(8453);const r={title:"Tales from the Binomial Tail: Confidence intervals for balanced accuracy",description:"How we assess and report detector accuracy",slug:"confidence-intervals-for-balanced-accuracy",authors:[{name:"Ted Sandler",title:"Senior Applied Scientist at Groundlight",image_url:"https://a-us.storyblok.com/f/1015187/1000x1000/efc35da152/sandlert.jpg"},{name:"Leo Dirac",title:"CTO and Co-founder at Groundlight",image_url:"https://a-us.storyblok.com/f/1015187/284x281/602a9c95c5/diracl.png"}],tags:["metrics","math","deep dive"],image:"./images/binomial-tails/binomial_confidence_intervals__muted_theme__social.png",hide_table_of_contents:!1},s=void 0,l={image:a(526).A,authorsImageUrls:[void 0,void 0]},c=[];function d(e){const t={p:"p",...(0,i.R)(),...e.components};return(0,o.jsx)(t.p,{children:"At Groundlight, we put careful thought into measuring the correctness of our machine learning detectors. In the simplest case, this means measuring detector accuracy. But our customers have vastly different performance needs since our platform allows them to train an ML model for nearly any Yes/No visual question-answering task. A single metric like accuracy is unlikely to provide adequate resolution for all such problems. Some customers might care more about false positive mistakes (precision) whereas others might care more about false negatives (recall)."})}function u(e={}){const{wrapper:t}={...(0,i.R)(),...e.components};return t?(0,o.jsx)(t,{...e,children:(0,o.jsx)(d,{...e})}):d(e)}},526:(e,t,a)=>{a.d(t,{A:()=>n});const n=a.p+"assets/images/binomial_confidence_intervals__muted_theme__social-09daf0e36a38cbc8c59558ab6f1c455b.png"},8453:(e,t,a)=>{a.d(t,{R:()=>r,x:()=>s});var n=a(6540);const o={},i=n.createContext(o);function r(e){const t=n.useContext(i);return n.useMemo((function(){return"function"==typeof e?e(t):{...t,...e}}),[t,e])}function s(e){let t;return t=e.disableParentContext?"function"==typeof e.components?e.components(o):e.components||o:r(e.components),n.createElement(i.Provider,{value:t},e.children)}},7395:e=>{e.exports=JSON.parse('{"permalink":"/python-sdk/blog/confidence-intervals-for-balanced-accuracy","editUrl":"https://github.com/groundlight/python-sdk/tree/main/docs/blog/blog/2024-01-16-binomial-tails.md","source":"@site/blog/2024-01-16-binomial-tails.md","title":"Tales from the Binomial Tail: Confidence intervals for balanced accuracy","description":"How we assess and report detector accuracy","date":"2024-01-16T00:00:00.000Z","tags":[{"inline":true,"label":"metrics","permalink":"/python-sdk/blog/tags/metrics"},{"inline":true,"label":"math","permalink":"/python-sdk/blog/tags/math"},{"inline":true,"label":"deep dive","permalink":"/python-sdk/blog/tags/deep-dive"}],"readingTime":23.39,"hasTruncateMarker":true,"authors":[{"name":"Ted Sandler","title":"Senior Applied Scientist at Groundlight","image_url":"https://a-us.storyblok.com/f/1015187/1000x1000/efc35da152/sandlert.jpg","imageURL":"https://a-us.storyblok.com/f/1015187/1000x1000/efc35da152/sandlert.jpg","socials":{},"key":null,"page":null},{"name":"Leo Dirac","title":"CTO and Co-founder at Groundlight","image_url":"https://a-us.storyblok.com/f/1015187/284x281/602a9c95c5/diracl.png","imageURL":"https://a-us.storyblok.com/f/1015187/284x281/602a9c95c5/diracl.png","socials":{},"key":null,"page":null}],"frontMatter":{"title":"Tales from the Binomial Tail: Confidence intervals for balanced accuracy","description":"How we assess and report detector accuracy","slug":"confidence-intervals-for-balanced-accuracy","authors":[{"name":"Ted Sandler","title":"Senior Applied Scientist at Groundlight","image_url":"https://a-us.storyblok.com/f/1015187/1000x1000/efc35da152/sandlert.jpg","imageURL":"https://a-us.storyblok.com/f/1015187/1000x1000/efc35da152/sandlert.jpg"},{"name":"Leo Dirac","title":"CTO and Co-founder at Groundlight","image_url":"https://a-us.storyblok.com/f/1015187/284x281/602a9c95c5/diracl.png","imageURL":"https://a-us.storyblok.com/f/1015187/284x281/602a9c95c5/diracl.png"}],"tags":["metrics","math","deep dive"],"image":"./images/binomial-tails/binomial_confidence_intervals__muted_theme__social.png","hide_table_of_contents":false},"unlisted":false,"prevItem":{"title":"The Grime Guardian: Building Stateful Multi-camera applications with Groundlight","permalink":"/python-sdk/blog/grime-guardian"}}')}}]);