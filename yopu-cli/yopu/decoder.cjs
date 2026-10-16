/**
 * Standalone Node.js decompressor bridge for Yopu score binary payloads.
 * Supports v1 (legacy single-chunk Brotli) and v2 (length-prefixed dual-chunk metadata + score).
 */
const fs = require('fs');
const path = require('path');

global.self = global;
const arPath = path.join(__dirname, 'ar_decompressor.js');
eval(fs.readFileSync(arPath, 'utf8'));

const U = 'ə\vĀ';
const H = U.charCodeAt(0);
const G = U.charCodeAt(1);
const K = U.charCodeAt(2) * U.charCodeAt(2);

function nt(t, n) {
  const e = t % n;
  return e < 0 ? e + n : e;
}

const V_const = (function(t, n) {
  let [e, i] = [n, nt(t, n)], [o, r] = [0, 1];
  for (; 0 !== i;) {
    const t = (e / i) | 0;
    [e, i] = [i, e - t * i];
    [o, r] = [r, o - t * r];
  }
  return nt(o, n);
})(H, K);

function tt(t, n, e) {
  let i = 1, o = t = nt(t, e);
  for (; n > 0;) {
    const t = nt(n, 2);
    n = (n / 2) | 0;
    if (1 === t) i = nt(i * o, e);
    o = nt(o * o, e);
  }
  return i;
}

function Q_v2(t = 1) {
  let n = nt(t, K);
  return {
    S: () => n / K,
    k: () => { n = nt(H * n + G, K); },
    X: () => { n = nt(V_const * (n - G), K); },
    T: (t) => {
      const e = ((tt(H, t, H * K - K) - 1) / (H - 1)) * G;
      const i = tt(H, t, K) * n;
      n = nt(e + i, K);
    }
  };
}

function Z(t, n, e) {
  const i = (e * (n + 1)) | 0;
  [t[n], t[i]] = [t[i], t[n]];
}

function Y_v2(t) {
  const n = t.length, e = Q_v2(n);
  e.T(n);
  for (let i = 1; i < n; i++) {
    e.X();
    Z(t, i, e.S());
  }
}

// Legacy v1 functions
let o_v1 = 0, a_v1 = 1;
const W_v1 = (function(t, n) {
  let e = [n, nt(t, n)], r = e[0], i = e[1];
  o_v1 = 0; a_v1 = 1;
  while (i !== 0) {
    let u = (r / i) | 0;
    let s = [i, r - u * i];
    r = s[0];
    i = s[1];
    let c = [a_v1, o_v1 - u * a_v1];
    o_v1 = c[0];
    a_v1 = c[1];
  }
  return nt(o_v1, n);
})(H, K);

function Y_v1(t) {
  let e = nt(t !== undefined ? t : 1, K);
  return {
    S: () => e / K,
    k: () => { e = nt(H * e + G, K); },
    T: () => { e = nt(W_v1 * (e - G), K); },
    X: (n) => {
      let t_val = ((tt(H, n, H * K - K) - 1) / (H - 1)) * G;
      let r_val = tt(H, n, K) * e;
      e = nt(t_val + r_val, K);
    }
  };
}

function V_v1(t) {
  let n = t.length;
  let e = Y_v1(n);
  e.X(n);
  for (let r = 1; r < n; r++) {
    e.T();
    Z(t, r, e.S());
  }
}

function decodePayload(rawBuffer) {
  const arr = new Uint8Array(rawBuffer);

  // 1. Try v2 decoding (length-prefixed chunks)
  try {
    const arrV2 = new Uint8Array(arr);
    Y_v2(arrV2);
    if (arrV2.length >= 4) {
      const splitIdx = 4 + ((arrV2[0] | (arrV2[1] << 8) | (arrV2[2] << 16) | (arrV2[3] << 24)) >>> 0);
      if (splitIdx > 4 && splitIdx <= arrV2.length) {
        const chunk1 = arrV2.subarray(4, splitIdx);
        const chunk2 = splitIdx === arrV2.length ? null : arrV2.subarray(splitIdx);
        const metaStr = new TextDecoder().decode(self.q7(chunk1));
        const meta = JSON.parse(metaStr);
        if (chunk2) {
          const scoreStr = new TextDecoder().decode(self.q7(chunk2));
          try {
            meta.score = JSON.parse(scoreStr);
          } catch {
            meta.score = scoreStr;
          }
        }
        return JSON.stringify(meta);
      }
    }
  } catch (err) {
    // Continue to legacy fallback
  }

  // 2. Legacy v1 decoding
  try {
    const arrV1 = new Uint8Array(arr);
    V_v1(arrV1);
    const decompressed = self.q7(arrV1);
    return new TextDecoder().decode(decompressed);
  } catch (err) {
    throw new Error(`Failed to decode payload (both v2 and v1 attempts failed): ${err.message}`);
  }
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
