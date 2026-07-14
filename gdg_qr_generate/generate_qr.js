// generate-qr.js
// Fancy GDG-branded QR for the "Know Your Terminal: Zero to Hero on Bash" invite.
// Usage:        node generate_qr.js
// Install deps: npm install qr-code-styling jsdom canvas

import { JSDOM } from "jsdom";
import nodeCanvas from "canvas";
import QRCodeStyling from "qr-code-styling";
import fs from "node:fs/promises";
import path from "node:path";

// ---- Config -----------------------------------------------------------------
const CONFIG = {
  data: "https://meet.google.com/gps-ejck-wbb",
  logoPath: "branding/gdg_logo.png",
  outputSvg: "gdg_qr_generate/output/qr-output.svg",
  size: 1024, // high-res for posters/social
};

// GDG palette — keeping contrast high for scannability.
const GDG_BLUE = "#1A73E8";
const GDG_GREEN = "#0F9D58";
const GDG_RED = "#EA4335";
const GDG_YELLOW = "#FBBC05";
// -----------------------------------------------------------------------------

async function loadLogoAsDataUri(logoPath) {
  if (/^https?:\/\//.test(logoPath)) return logoPath;
  const buf = await fs.readFile(logoPath);
  const ext = path.extname(logoPath).slice(1).toLowerCase() || "png";
  return `data:image/${ext};base64,${buf.toString("base64")}`;
}

async function generate() {
  // qr-code-styling expects a DOM; jsdom + node-canvas give it one.
  const dom = new JSDOM("<!DOCTYPE html><html><body></body></html>");
  global.window = dom.window;
  global.document = dom.window.document;

  const logoData = await loadLogoAsDataUri(CONFIG.logoPath);

  const dotsGradient = {
    type: "linear",
    rotation: Math.PI / 4, // 45°
    colorStops: [
      { offset: 0, color: GDG_BLUE },
      { offset: 1, color: GDG_GREEN },
    ],
  };

  const cornersGradient = {
    type: "linear",
    rotation: Math.PI / 4,
    colorStops: [
      { offset: 0, color: GDG_RED },
      { offset: 1, color: GDG_YELLOW },
    ],
  };

  const qr = new QRCodeStyling({
    jsdom: JSDOM,
    nodeCanvas,
    width: CONFIG.size,
    height: CONFIG.size,
    type: "canvas",
    data: CONFIG.data,
    image: logoData,
    margin: 16,
    qrOptions: {
      errorCorrectionLevel: "H", // required when overlaying a logo
    },
    dotsOptions: {
      type: "classy-rounded", // square | dots | rounded | classy | classy-rounded | extra-rounded
      gradient: dotsGradient,
    },
    backgroundOptions: {
      color: "#ffffff",
    },
    cornersSquareOptions: {
      type: "extra-rounded",
      gradient: cornersGradient,
    },
    cornersDotOptions: {
      type: "dot",
      color: GDG_BLUE,
    },
    imageOptions: {
      crossOrigin: "anonymous",
      margin: 10, // breathing room around logo
      imageSize: 0.28, // ≤ 0.4 to stay scannable; 0.28 looks balanced
      hideBackgroundDots: true,
    },
  });

  // SVG (vector — for posters, vector editors, infinite-scale prints)
  const svgBuffer = await qr.getRawData("svg");
  await fs.writeFile(CONFIG.outputSvg, svgBuffer);
  console.log(`✓ SVG saved → ${CONFIG.outputSvg}`);
  console.log(`→ Encoded URL: ${CONFIG.data}`);
}

generate().catch((err) => {
  console.error("Failed to generate QR:", err);
  process.exit(1);
});
