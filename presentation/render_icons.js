const React = require('react');
const ReactDOMServer = require('react-dom/server');
const sharp = require('sharp');
const fs = require('fs');
const Fa = require('react-icons/fa');
const Md = require('react-icons/md');

// icon name -> [library, componentName, hexColor]
const icons = {
  upload: [Fa, 'FaFileUpload', '0B3D62'],
  extract: [Fa, 'FaFileAlt', '0B3D62'],
  chunk: [Fa, 'FaCut', '0B3D62'],
  embed: [Fa, 'FaProjectDiagram', '0B3D62'],
  search: [Fa, 'FaSearch', '0B3D62'],
  robot: [Fa, 'FaRobot', '0B3D62'],
  check: [Fa, 'FaCheckCircle', '0F6E56'],
  bolt: [Fa, 'FaBolt', '0B3D62'],
  python: [Fa, 'FaPython', '0B3D62'],
  database: [Fa, 'FaDatabase', '0B3D62'],
  brain: [Fa, 'FaBrain', '0B3D62'],
  chat: [Fa, 'FaComments', '0B3D62'],
  target: [Fa, 'FaBullseye', '0B3D62'],
  warning: [Fa, 'FaExclamationTriangle', '7F77DD'],
  future: [Fa, 'FaRocket', '0F6E56'],
  book: [Fa, 'FaBook', '0B3D62'],
  layer: [Md, 'MdLayers', '0B3D62'],
  cloud: [Fa, 'FaCloud', '0B3D62'],
};

async function renderAll() {
  for (const [name, [lib, comp, color]] of Object.entries(icons)) {
    const Icon = lib[comp];
    const svgString = ReactDOMServer.renderToStaticMarkup(
      React.createElement(Icon, { size: 256, color: `#${color}` })
    );
    const fullSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="256" height="256">${svgString.match(/<svg[^>]*>(.*)<\/svg>/s)[1]}</svg>`;
    await sharp(Buffer.from(fullSvg)).png().toFile(`icons_${name}.png`);
  }
  console.log('Rendered', Object.keys(icons).length, 'icons');
}

renderAll();
