"use strict";(self.webpackChunkweb=self.webpackChunkweb||[]).push([[6986],{6901:(n,e,i)=>{i.r(e),i.d(e,{assets:()=>d,contentTitle:()=>r,default:()=>g,frontMatter:()=>s,metadata:()=>l,toc:()=>h});var o=i(5893),t=i(1151);const s={},r="Installing on Windows",l={id:"installation/windows",title:"Installing on Windows",description:"This guide will help you install the Groundlight SDK on Windows. The Groundlight SDK requires Python 3.7 or higher.",source:"@site/docs/installation/3-windows.md",sourceDirName:"installation",slug:"/installation/windows",permalink:"/docs/installation/windows",draft:!1,unlisted:!1,editUrl:"https://github.com/groundlight/tree/main/docs/docs/installation/3-windows.md",tags:[],version:"current",sidebarPosition:3,frontMatter:{},sidebar:"tutorialSidebar",previous:{title:"Installing on macOS",permalink:"/docs/installation/macos"},next:{title:"Installing on Raspberry Pi",permalink:"/docs/installation/raspberry-pi"}},d={},h=[{value:"Prerequisites",id:"prerequisites",level:2},{value:"Basic Installation",id:"basic-installation",level:2},{value:"Installing Groundlight SDK",id:"installing-groundlight-sdk",level:3},{value:"Checking Groundlight SDK Version",id:"checking-groundlight-sdk-version",level:3},{value:"Upgrading Groundlight SDK",id:"upgrading-groundlight-sdk",level:3},{value:"Getting the right Python Version",id:"getting-the-right-python-version",level:2},{value:"Upgrading Python on Windows",id:"upgrading-python-on-windows",level:3},{value:"Ready to go!",id:"ready-to-go",level:2}];function a(n){const e={a:"a",code:"code",h1:"h1",h2:"h2",h3:"h3",li:"li",p:"p",pre:"pre",ul:"ul",...(0,t.a)(),...n.components};return(0,o.jsxs)(o.Fragment,{children:[(0,o.jsx)(e.h1,{id:"installing-on-windows",children:"Installing on Windows"}),"\n",(0,o.jsx)(e.p,{children:"This guide will help you install the Groundlight SDK on Windows. The Groundlight SDK requires Python 3.7 or higher."}),"\n",(0,o.jsx)(e.h2,{id:"prerequisites",children:"Prerequisites"}),"\n",(0,o.jsx)(e.p,{children:"Ensure that you have the following installed on your system:"}),"\n",(0,o.jsxs)(e.ul,{children:["\n",(0,o.jsx)(e.li,{children:"Python 3.7 or higher"}),"\n",(0,o.jsx)(e.li,{children:"pip (Python package installer)"}),"\n"]}),"\n",(0,o.jsx)(e.h2,{id:"basic-installation",children:"Basic Installation"}),"\n",(0,o.jsx)(e.p,{children:"Assuming you have Python 3.7 or higher installed on your system, you can proceed with the following steps to install or upgrade the Groundlight SDK:"}),"\n",(0,o.jsx)(e.h3,{id:"installing-groundlight-sdk",children:"Installing Groundlight SDK"}),"\n",(0,o.jsx)(e.p,{children:"To install the Groundlight SDK using pip, run the following command in your Command Prompt:"}),"\n",(0,o.jsx)(e.pre,{children:(0,o.jsx)(e.code,{className:"language-bash",children:"pip install groundlight\n"})}),"\n",(0,o.jsxs)(e.p,{children:["If you're also using ",(0,o.jsx)(e.code,{children:"python2"})," on your system, you might need to use ",(0,o.jsx)(e.code,{children:"pip3"})," instead:"]}),"\n",(0,o.jsx)(e.pre,{children:(0,o.jsx)(e.code,{className:"language-bash",children:"pip3 install groundlight\n"})}),"\n",(0,o.jsx)(e.p,{children:"The Groundlight SDK is now installed and ready for use."}),"\n",(0,o.jsx)(e.h3,{id:"checking-groundlight-sdk-version",children:"Checking Groundlight SDK Version"}),"\n",(0,o.jsx)(e.p,{children:"To check if the Groundlight SDK is installed and to display its version, you can use the following Python one-liner:"}),"\n",(0,o.jsx)(e.pre,{children:(0,o.jsx)(e.code,{className:"language-bash",children:'python -c "import groundlight; print(groundlight.__version__)"\n'})}),"\n",(0,o.jsx)(e.h3,{id:"upgrading-groundlight-sdk",children:"Upgrading Groundlight SDK"}),"\n",(0,o.jsx)(e.p,{children:"If you need to upgrade the Groundlight SDK to the latest version, use the following pip command:"}),"\n",(0,o.jsx)(e.pre,{children:(0,o.jsx)(e.code,{className:"language-bash",children:"pip install --upgrade groundlight\n"})}),"\n",(0,o.jsxs)(e.p,{children:["Or, if you're using ",(0,o.jsx)(e.code,{children:"pip3"}),":"]}),"\n",(0,o.jsx)(e.pre,{children:(0,o.jsx)(e.code,{className:"language-bash",children:"pip3 install --upgrade groundlight\n"})}),"\n",(0,o.jsx)(e.p,{children:'After upgrading, you can use the Python one-liner mentioned in the "Checking Groundlight SDK Version" section to verify that the latest version is now installed.'}),"\n",(0,o.jsx)(e.h2,{id:"getting-the-right-python-version",children:"Getting the right Python Version"}),"\n",(0,o.jsx)(e.p,{children:"To check your installed Python version, open a Command Prompt and run:"}),"\n",(0,o.jsx)(e.pre,{children:(0,o.jsx)(e.code,{className:"language-bash",children:"python --version\n"})}),"\n",(0,o.jsx)(e.p,{children:'If you see a version number starting with "3.7" or higher (e.g., "3.7.5" or "3.9.0"), you\'re good to go. If not, you might need to upgrade Python on your system.'}),"\n",(0,o.jsx)(e.h3,{id:"upgrading-python-on-windows",children:"Upgrading Python on Windows"}),"\n",(0,o.jsxs)(e.p,{children:["Download the latest Python installer from the ",(0,o.jsx)(e.a,{href:"https://www.python.org/downloads/windows/",children:"official Python website"})," and run it."]}),"\n",(0,o.jsxs)(e.p,{children:["After upgrading, verify the Python version by running ",(0,o.jsx)(e.code,{children:"python --version"})," or ",(0,o.jsx)(e.code,{children:"python3 --version"}),", as described earlier."]}),"\n",(0,o.jsx)(e.h2,{id:"ready-to-go",children:"Ready to go!"}),"\n",(0,o.jsxs)(e.p,{children:["You're now ready to start using the Groundlight SDK in your projects. For more information on using the SDK, refer to the ",(0,o.jsx)(e.a,{href:"/docs/getting-started/api-tokens",children:"API Tokens"})," and ",(0,o.jsx)(e.a,{href:"/docs/building-applications",children:"Building Applications"})," documentation pages."]})]})}function g(n={}){const{wrapper:e}={...(0,t.a)(),...n.components};return e?(0,o.jsx)(e,{...n,children:(0,o.jsx)(a,{...n})}):a(n)}},1151:(n,e,i)=>{i.d(e,{Z:()=>l,a:()=>r});var o=i(7294);const t={},s=o.createContext(t);function r(n){const e=o.useContext(s);return o.useMemo((function(){return"function"==typeof n?n(e):{...e,...n}}),[e,n])}function l(n){let e;return e=n.disableParentContext?"function"==typeof n.components?n.components(t):n.components||t:r(n.components),o.createElement(s.Provider,{value:e},n.children)}}}]);