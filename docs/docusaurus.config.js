// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

// Libraries that support mathematics in documentation
import rehypeKatex from 'rehype-katex';
import remarkMath from 'remark-math';

// Options: https://github.com/FormidableLabs/prism-react-renderer/tree/master/src/themes
const lightCodeTheme = require("prism-react-renderer").themes.github;
const darkCodeTheme = require("prism-react-renderer").themes.vsDark;

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: "Groundlight",
  tagline: "Computer Vision powered by Natural Language",
  favicon: "img/favicon.ico",

  // Set the production url of your site here
  url: "https://code.groundlight.ai",
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: "/python-sdk/",

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: "groundlight", // Usually your GitHub org/user name.
  projectName: "python-sdk", // Usually your repo name.
  deploymentBranch: "gh-pages", // Branch that GitHub pages will deploy from.
  trailingSlash: false,

  onBrokenLinks: "throw",
  onBrokenMarkdownLinks: "throw",

  // Even if you don't use internalization, you can use this field to set useful
  // metadata like html lang. For example, if your site is Chinese, you may want
  // to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: "en",
    locales: ["en"],
  },

  presets: [
    [
      "classic",
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve("./sidebars.js"),
          editUrl:
            // Remove this to remove the "edit this page" links.
            "https://github.com/groundlight/python-sdk/tree/main/docs/",
          // the first "docs" is the branch
          // the second "docs" is the subdir within the repo
          // there will be a third one for real URLs.  :)
        },
        gtag: {
          trackingID: 'G-WG1Q5X6F6L',
        },
        blog: {
          showReadingTime: true,
          remarkPlugins: [remarkMath],
          rehypePlugins: [rehypeKatex],
          editUrl:
            "https://github.com/groundlight/python-sdk/tree/main/docs/blog/",
        },
        theme: {
          customCss: require.resolve("./src/css/custom.css"),
        },
      }),
    ],
  ],

  stylesheets: [
    {
      href: 'https://cdn.jsdelivr.net/npm/katex@0.13.24/dist/katex.min.css',
      type: 'text/css',
      integrity:
        'sha384-odtC+0UGzzFL/6PNoE8rX/SPcQDXBJ+uRepguP4QkPCm2LBxH3FA3y+fKSiJ+AmM',
      crossorigin: 'anonymous',
    },
  ],

  themes: [
    [
      // This adds a search bar to the docs.
      // For more details: https://github.com/easyops-cn/docusaurus-search-local
      // @ts-ignore
      require.resolve("@easyops-cn/docusaurus-search-local"),
      /** @type {import("@easyops-cn/docusaurus-search-local").PluginOptions} */
      // @ts-ignore
      ({
        // ... Your options.
        hashed: true,
        highlightSearchTermsOnTargetPage: true,
        explicitSearchResultPath: true,
        removeDefaultStemmer: true,
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // image is expected to be a "social card".  Logo for now.
      image: "img/gl-icon400.png",
      navbar: {
        title: "Groundlight",
        logo: {
          alt: "Groundlight Logo",
          src: "img/favicon-32x32.png",
          href: "/python-sdk/",
        },
        items: [
          {
            type: "docSidebar",
            sidebarId: "tutorialSidebar",
            position: "left",
            label: "Docs",
          },
          {
            to: "/docs/building-applications",
            label: "Applications",
            position: "left",
          },
          {
            href: "pathname:///python-sdk/api-reference-docs/",
            label: "API Reference",
            position: "left",
          },
          {
            href: "https://github.com/groundlight/python-sdk",
            label: "GitHub",
            position: "right",
          },
          {
            to: 'blog',
            label: 'Blog',
            position: 'left',
          },
        ],
      },
      footer: {
        style: "dark",
        links: [
          {
            title: "Documentation",
            items: [
              {
                label: "Getting Started",
                to: "/docs/getting-started",
              },
              {
                label: "Building Applications",
                to: "/docs/building-applications",
              },
              {
                label: "Installation",
                to: "/docs/installation",
              },
            ],
          },
          {
            title: "Company",
            items: [
              {
                label: "About",
                href: "https://www.groundlight.ai/",
              },
              {
                label: "Team",
                href: "https://www.groundlight.ai/team",
              },
              {
                label: "Careers",
                href: "https://www.groundlight.ai/careers",
              },
              {
                label: "Sign In",
                href: "https://app.groundlight.ai/",
              },
            ],
          },
          {
            title: "Code",
            items: [
              {
                label: "Github",
                href: "https://github.com/groundlight/",
              },
              {
                label: "Python SDK",
                href: "https://pypi.org/project/groundlight/",
              },
              {
                label: "Video streaming",
                href: "https://github.com/groundlight/stream",
              },
              {
                label: "Arduino",
                href: "https://github.com/groundlight/esp32cam",
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Groundlight AI.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
      },
    }),
  plugins: [
    [
      "@docusaurus/plugin-client-redirects",
      {
        redirects: [
          {
            to: "https://www.groundlight.ai/blog/reducing-data-labeling-costs-with-uncertainty-sampling", // new marketing site route
            from: "/blog/active-learning", // old blog route
          },
          {
            to: "https://www.groundlight.ai/blog/groundlight-ai-achieves-soc-2-type-2-compliance", // new marketing site route
            from: "/blog/groundlight-ai-achieves-soc-2-type-2-compliance", // old blog route
          },
          {
            to: "https://www.groundlight.ai/blog/navigating-ambiguity-with-groundlight-ai-detectors", // new marketing site route
            from: "/blog/dealing-with-unclear-images", // old blog route
          },
          {
            to: "https://www.groundlight.ai/blog/building-your-first-computer-vision-model-just-got-easier", // new marketing site route
            from: "/blog/getting-started", // old blog route
          },
          {
            to: "https://www.groundlight.ai/blog/introducing-groundlights-framegrab-library",
            from: "/blog/introducing-framegrab"
          },
          {
            to: "https://www.groundlight.ai/blog/best-practices-for-best-results-with-groundlight",
            from: "/blog/best-practices"
          },
          {
            to: "https://www.groundlight.ai/blog/linux-os-images-for-computer-vision-on-raspberry-pi",
            from: "/blog/raspberry-pi-computer-vision"
          },
        ],
      },
    ],
  ],
};

module.exports = config;