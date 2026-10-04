// Zet scripts/cv-pdf/.build/cv-*.html om naar de pdf's op de site.
// Eerst: python3 scripts/cv-pdf/build.py
const path = require('path');
let pw;
try { pw = require('playwright'); }
catch { pw = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright'); }

const root = path.resolve(__dirname, '..', '..');
const jobs = [['cv-nl.html', 'nl/cv/jimmy-rentmeester-cv.pdf'], ['cv-en.html', 'cv/jimmy-rentmeester-cv-en.pdf']];

(async () => {
  const browser = await pw.chromium.launch();
  for (const [src, out] of jobs) {
    const page = await browser.newPage();
    await page.goto('file://' + path.join(__dirname, '.build', src), { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    await page.pdf({ path: path.join(root, out), preferCSSPageSize: true, printBackground: true });
    await page.close();
    console.log('geschreven:', out);
  }
  await browser.close();
})();
