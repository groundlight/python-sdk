"use strict";(self.webpackChunkweb=self.webpackChunkweb||[]).push([[614],{3905:(t,e,n)=>{n.d(e,{Zo:()=>u,kt:()=>f});var i=n(7294);function r(t,e,n){return e in t?Object.defineProperty(t,e,{value:n,enumerable:!0,configurable:!0,writable:!0}):t[e]=n,t}function a(t,e){var n=Object.keys(t);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(t);e&&(i=i.filter((function(e){return Object.getOwnPropertyDescriptor(t,e).enumerable}))),n.push.apply(n,i)}return n}function o(t){for(var e=1;e<arguments.length;e++){var n=null!=arguments[e]?arguments[e]:{};e%2?a(Object(n),!0).forEach((function(e){r(t,e,n[e])})):Object.getOwnPropertyDescriptors?Object.defineProperties(t,Object.getOwnPropertyDescriptors(n)):a(Object(n)).forEach((function(e){Object.defineProperty(t,e,Object.getOwnPropertyDescriptor(n,e))}))}return t}function l(t,e){if(null==t)return{};var n,i,r=function(t,e){if(null==t)return{};var n,i,r={},a=Object.keys(t);for(i=0;i<a.length;i++)n=a[i],e.indexOf(n)>=0||(r[n]=t[n]);return r}(t,e);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(t);for(i=0;i<a.length;i++)n=a[i],e.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(t,n)&&(r[n]=t[n])}return r}var s=i.createContext({}),p=function(t){var e=i.useContext(s),n=e;return t&&(n="function"==typeof t?t(e):o(o({},e),t)),n},u=function(t){var e=p(t.components);return i.createElement(s.Provider,{value:e},t.children)},c="mdxType",d={inlineCode:"code",wrapper:function(t){var e=t.children;return i.createElement(i.Fragment,{},e)}},m=i.forwardRef((function(t,e){var n=t.components,r=t.mdxType,a=t.originalType,s=t.parentName,u=l(t,["components","mdxType","originalType","parentName"]),c=p(n),m=r,f=c["".concat(s,".").concat(m)]||c[m]||d[m]||a;return n?i.createElement(f,o(o({ref:e},u),{},{components:n})):i.createElement(f,o({ref:e},u))}));function f(t,e){var n=arguments,r=e&&e.mdxType;if("string"==typeof t||r){var a=n.length,o=new Array(a);o[0]=m;var l={};for(var s in e)hasOwnProperty.call(e,s)&&(l[s]=e[s]);l.originalType=t,l[c]="string"==typeof t?t:r,o[1]=l;for(var p=2;p<a;p++)o[p]=n[p];return i.createElement.apply(null,o)}return i.createElement.apply(null,n)}m.displayName="MDXCreateElement"},4686:(t,e,n)=>{n.r(e),n.d(e,{assets:()=>s,contentTitle:()=>o,default:()=>d,frontMatter:()=>a,metadata:()=>l,toc:()=>p});var i=n(7462),r=(n(7294),n(3905));const a={},o="Installation",l={unversionedId:"installation/installation",id:"installation/installation",title:"Installation",description:"Welcome to the Groundlight SDK installation guide. In this guide, you'll find step-by-step instructions on how to install and set up the Groundlight SDK on various platforms.",source:"@site/docs/installation/installation.md",sourceDirName:"installation",slug:"/installation/",permalink:"/python-sdk/docs/installation/",draft:!1,editUrl:"https://github.com/groundlight/python-sdk/tree/main/docs/docs/installation/installation.md",tags:[],version:"current",frontMatter:{},sidebar:"tutorialSidebar",previous:{title:"Industrial and Manufacturing Applications",permalink:"/python-sdk/docs/building-applications/industrial"},next:{title:"Numpy, PIL, OpenCV - using common libraries",permalink:"/python-sdk/docs/installation/libraries-numpy-pil"}},s={},p=[{value:"Platform-specific Installation Guides",id:"platform-specific-installation-guides",level:2}],u={toc:p},c="wrapper";function d(t){let{components:e,...n}=t;return(0,r.kt)(c,(0,i.Z)({},u,n,{components:e,mdxType:"MDXLayout"}),(0,r.kt)("h1",{id:"installation"},"Installation"),(0,r.kt)("p",null,"Welcome to the Groundlight SDK installation guide. In this guide, you'll find step-by-step instructions on how to install and set up the Groundlight SDK on various platforms."),(0,r.kt)("h2",{id:"platform-specific-installation-guides"},"Platform-specific Installation Guides"),(0,r.kt)("p",null,"Choose your platform from the list below and follow the instructions in the corresponding guide:"),(0,r.kt)("ul",null,(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("a",{parentName:"li",href:"/python-sdk/docs/installation/linux-windows-mac"},"Linux")),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("a",{parentName:"li",href:"/python-sdk/docs/installation/linux-windows-mac"},"macOS")),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("a",{parentName:"li",href:"/python-sdk/docs/installation/linux-windows-mac"},"Windows")),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("a",{parentName:"li",href:"/python-sdk/docs/installation/raspberry-pi-jetson"},"Raspberry Pi")),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("a",{parentName:"li",href:"/python-sdk/docs/installation/raspberry-pi-jetson"},"NVIDIA Jetson")),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("a",{parentName:"li",href:"https://github.com/groundlight/esp32cam"},"Arduino"))),(0,r.kt)("p",null,"After completing the installation process for your platform, you'll be ready to start ",(0,r.kt)("a",{parentName:"p",href:"/docs/building-applications/"},"building visual applications")," using the Groundlight SDK."))}d.isMDXComponent=!0}}]);