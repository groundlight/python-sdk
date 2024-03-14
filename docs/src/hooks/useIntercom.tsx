import React, { useEffect } from "react";

const useIntercom = () => {
  useEffect(() => {
    const loadIntercom = () => {
      const w = window;
      const ic = w.Intercom;
      if (typeof ic === "function") {
        ic("reattach_activator");
        ic("update", w.intercomSettings);
      } else {
        const i = function () {
          i.c(arguments);
        };
        i.q = [];
        i.c = function (args) {
          i.q.push(args);
        };
        w.Intercom = i;

        const s = document.createElement("script");
        s.type = "text/javascript";
        s.async = true;
        s.src = "https://widget.intercom.io/widget/fu9pkks5";
        document.body.appendChild(s);
      }
    };

    if (document.readyState === "complete") {
      loadIntercom();
    } else {
      window.addEventListener("load", loadIntercom);
    }

    return () => window.removeEventListener("load", loadIntercom);
  }, []);

  useEffect(() => {
    if (typeof window.Intercom === "function") {
      window.Intercom("boot", {
        api_base: "https://api-iam.intercom.io",
        app_id: "fu9pkks5",
      });
    }

    if (typeof window.Intercom === "function") {
      window.Intercom("update", window.intercomSettings);
    }
  }, []);
};

export default useIntercom;
