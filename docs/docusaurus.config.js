// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

// Options: https://github.com/FormidableLabs/prism-react-renderer/tree/master/src/themes
const lightCodeTheme = require("prism-react-renderer").themes.github;
const darkCodeTheme = require("prism-react-renderer").themes.vsDark;

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: "Groundlight",
  tagline: "Computer Vision powered by Natural Language",
  favicon: "img/favicon.ico",

  // Set the production url of your site here
  url: "https://www.groundlight.ai",
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: "/",

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
            "https://github.com/groundlight/tree/main/docs/",
          // the first "docs" is the branch
          // the second "docs" is the subdir within the repo
          // there will be a third one for real URLs.  :)
        },
        theme: {
          customCss: require.resolve("./src/css/custom.css"),
        },
      }),
    ],
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
      // Replace with your project's social card
      image: "img/docusaurus-social-card.jpg",
      navbar: {
        title: "Groundlight",
        logo: {
          alt: "Groundlight Logo",
          src: "img/favicon-32x32.png",
          href: "https://code.groundlight.ai/",
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
            href: "pathname:///api-reference-docs/",
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
};

module.exports = config;
