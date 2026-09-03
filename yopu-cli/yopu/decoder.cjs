/**
 * Standalone Node.js decompressor bridge for Yopu score binary payloads.
 * Runs inverse permutation V(e) and Brotli custom dictionary decompression q7(e).
 * Reads raw binary from stdin, outputs decoded JSON to stdout.
 */
const fs = require('fs');
const path = require('path');

global.self = global;
const arPath = path.join(__dirname, 'ar_decompressor.js');
eval(fs.readFileSync(arPath, 'utf8'));

const y = 'ə\vĀ';
const H = y.charCodeAt(0);
const G = y.charCodeAt(1);
const J = y.charCodeAt(2) * y.charCodeAt(2);

function tt(t, n) {
  let e = t % n;
  return e < 0 ? e + n : e;
}

let o = 0, a = 1;
const W = (function(t, n) {
  let e = [n, tt(t, n)], r = e[0], i = e[1];
  o = 0; a = 1;
  while (i !== 0) {
    let u = (r / i) | 0;
    let s = [i, r - u * i];
    r = s[0];
    i = s[1];
    let c = [a, o - u * a];
    o = c[0];
    a = c[1];
  }
  return tt(o, n);
})(H, J);

function Z(t, n, e) {
  let r = 1;
  let i = tt(t, e);
  let n_curr = n;
  while (n_curr > 0) {
    let o_val = tt(n_curr, 2);
    n_curr = (n_curr / 2) | 0;
    if (o_val === 1) r = tt(r * i, e);
    i = tt(i * i, e);
  }
  return r;
}

function Y(t) {
  let e = tt(t !== undefined ? t : 1, J);
  return {
    S: () => e / J,
    k: () => { e = tt(H * e + G, J); },
    T: () => { e = tt(W * (e - G), J); },
    X: (n) => {
      let t_val = ((Z(H, n, H * J - J) - 1) / (H - 1)) * G;
      let r_val = Z(H, n, J) * e;
      e = tt(t_val + r_val, J);
    }
  };
}

function Q(t, n, e) {
  let r = (e * (n + 1)) | 0;
  let i = [t[r], t[n]];
  t[n] = i[0];
  t[r] = i[1];
}

function V(t) {
  let n = t.length;
  let e = Y(n);
  e.X(n);
  for (let r = 1; r < n; r++) {
    e.T();
    Q(t, r, e.S());
  }
}

function decodePayload(rawBuffer) {
  const arr = new Uint8Array(rawBuffer);
  V(arr);
  const decompressed = self.q7(arr);
  return new TextDecoder().decode(decompressed);
}

function main() {
  if (process.argv[2]) {
    const raw = fs.readFileSync(process.argv[2]);
    process.stdout.write(decodePayload(raw));
    return;
  }
  const chunks = [];
  process.stdin.on('data', chunk => chunks.push(chunk));
  process.stdin.on('end', () => {
    const buf = Buffer.concat(chunks);
    if (buf.length === 0) {
      process.exit(1);
    }
    process.stdout.write(decodePayload(buf));
  });
}

main();
