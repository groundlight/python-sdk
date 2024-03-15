import React from 'react';
import OriginalLayout from '@theme-original/Layout';
import useIntercom from '@site/src/hooks/useIntercom';

function Layout(props) {
  useIntercom();

  return <OriginalLayout {...props} />;
}

export default Layout;