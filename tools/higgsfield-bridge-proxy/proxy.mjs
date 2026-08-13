// Local reverse proxy for https://bridge.higgsfield.ai
//
// Why this exists: the bridge answers the optional MCP "GET /mcp" SSE probe with
// HTTP 404. Per the MCP spec a server without SSE support must answer 405. Cursor
// treats repeated 404s on that stream as session termination and tombstones the
// transport after 5 attempts, so tool discovery never completes. This proxy is a
// transparent passthrough that rewrites only that one response.

import http from 'node:http';
import https from 'node:https';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const UPSTREAM_HOST = 'bridge.higgsfield.ai';
const UPSTREAM_PORT = 443;
const HOST = '127.0.0.1';

const args = process.argv.slice(2);
const argValue = (name, fallback) => {
  const i = args.indexOf(name);
  return i !== -1 && args[i + 1] ? args[i + 1] : fallback;
};

const PORT = Number(argValue('--port', process.env.HF_PROXY_PORT || 18777));
const HERE = path.dirname(fileURLToPath(import.meta.url));
const LOG_FILE = argValue('--log', process.env.HF_PROXY_LOG || path.join(HERE, 'proxy.log'));

// Cursor validates that the protected-resource metadata identifies the URL it
// actually connected to. Pure passthrough advertises "https://bridge.higgsfield.ai"
// and Cursor rejects it with:
//   Protected resource https://bridge.higgsfield.ai does not match expected
//   http://127.0.0.1:18777/mcp (or origin)
// So we rewrite two things, and only those two:
//   1. the `resource` field of /.well-known/oauth-protected-resource
//   2. the resource_metadata URL inside the 401 WWW-Authenticate header
// `authorization_servers`, the issuer, and the authorize/token endpoints are left
// pointing at Higgsfield, so the browser login still happens on the higgsfield.ai
// origin where the session cookies live. Disable with --no-rewrite-metadata.
const REWRITE_METADATA =
  !args.includes('--no-rewrite-metadata') && process.env.HF_PROXY_REWRITE_METADATA !== '0';

fs.mkdirSync(path.dirname(LOG_FILE), { recursive: true });
const logStream = fs.createWriteStream(LOG_FILE, { flags: 'a' });

function log(...parts) {
  const line = `[${new Date().toISOString()}] ${parts.join(' ')}\n`;
  logStream.write(line);
  process.stdout.write(line);
}

// Never let credentials reach the log file.
const SENSITIVE_HEADERS = new Set(['authorization', 'proxy-authorization', 'cookie', 'set-cookie']);

// RFC 7230 hop-by-hop headers must not be forwarded.
const HOP_BY_HOP = new Set([
  'connection',
  'keep-alive',
  'proxy-authenticate',
  'proxy-authorization',
  'te',
  'trailer',
  'transfer-encoding',
  'upgrade',
]);

function buildUpstreamHeaders(incoming) {
  const out = {};
  for (const [key, value] of Object.entries(incoming)) {
    const lower = key.toLowerCase();
    if (HOP_BY_HOP.has(lower)) continue;
    if (lower === 'host') continue;
    if (lower === 'content-length') continue; // recomputed from the body we actually send
    // Identity encoding keeps SSE frames unbuffered and avoids decompressing to rewrite JSON.
    if (lower === 'accept-encoding') continue;
    out[key] = value;
  }
  out.host = UPSTREAM_HOST;
  out['accept-encoding'] = 'identity';
  return out;
}

function buildClientHeaders(upstreamHeaders) {
  const out = {};
  for (const [key, value] of Object.entries(upstreamHeaders)) {
    const lower = key.toLowerCase();
    if (HOP_BY_HOP.has(lower)) continue;
    if (lower === 'content-length') continue; // may change if we rewrite the body
    out[key] = value;
  }
  return out;
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on('data', (c) => chunks.push(c));
    req.on('end', () => resolve(Buffer.concat(chunks)));
    req.on('error', reject);
  });
}

const isMcpPath = (url) => url === '/mcp' || url.startsWith('/mcp?') || url.startsWith('/mcp/');
const isProtectedResourcePath = (url) => url.startsWith('/.well-known/oauth-protected-resource');

const LOCAL_ORIGIN = `http://${HOST}:${PORT}`;
const UPSTREAM_ORIGIN = `https://${UPSTREAM_HOST}`;

// Point Cursor's resource-metadata lookup back at this proxy so it reads the
// rewritten `resource` instead of Higgsfield's original.
function rewriteWwwAuthenticate(headers) {
  const value = headers['www-authenticate'];
  if (typeof value !== 'string') return;
  headers['www-authenticate'] = value.replaceAll(UPSTREAM_ORIGIN, LOCAL_ORIGIN);
}

function rewriteProtectedResource(raw) {
  try {
    const doc = JSON.parse(raw);
    // Only the audience identifier changes. authorization_servers stays upstream.
    doc.resource = LOCAL_ORIGIN;
    return JSON.stringify(doc);
  } catch {
    return raw; // not JSON; forward untouched rather than corrupting the body
  }
}

const server = http.createServer(async (clientReq, clientRes) => {
  const started = Date.now();
  const method = clientReq.method || 'GET';
  const url = clientReq.url || '/';

  let body;
  try {
    body = await readBody(clientReq);
  } catch (err) {
    log('ERR', method, url, 'request body read failed:', err.message);
    clientRes.writeHead(400).end('bad request body');
    return;
  }

  const headers = buildUpstreamHeaders(clientReq.headers);
  if (body.length > 0) headers['content-length'] = String(body.length);

  const hasAuth = Boolean(clientReq.headers.authorization);
  const sessionId = clientReq.headers['mcp-session-id'] || '-';

  const upstreamReq = https.request(
    { host: UPSTREAM_HOST, port: UPSTREAM_PORT, method, path: url, headers, servername: UPSTREAM_HOST },
    (upstreamRes) => {
      const status = upstreamRes.statusCode || 502;

      // The one behavior change: turn the bogus 404 on the SSE probe into a spec-compliant 405.
      if (method === 'GET' && isMcpPath(url) && status === 404) {
        upstreamRes.resume();
        log('FIX', method, url, 'upstream 404 -> 405', `auth=${hasAuth}`, `session=${sessionId}`);
        clientRes.writeHead(405, {
          Allow: 'POST',
          'Content-Type': 'application/json',
          'Cache-Control': 'no-store',
        });
        clientRes.end(JSON.stringify({ error: 'Method Not Allowed', message: 'SSE stream not supported; use POST' }));
        return;
      }

      const outHeaders = buildClientHeaders(upstreamRes.headers);

      if (REWRITE_METADATA) rewriteWwwAuthenticate(outHeaders);

      if (REWRITE_METADATA && isProtectedResourcePath(url) && status === 200) {
        const chunks = [];
        upstreamRes.on('data', (c) => chunks.push(c));
        upstreamRes.on('end', () => {
          const buf = Buffer.from(rewriteProtectedResource(Buffer.concat(chunks).toString('utf8')), 'utf8');
          outHeaders['content-length'] = String(buf.length);
          clientRes.writeHead(status, outHeaders);
          clientRes.end(buf);
          log('RES', status, method, url, `${Date.now() - started}ms`, 'resource-rewritten');
        });
        return;
      }

      clientRes.writeHead(status, outHeaders);
      upstreamRes.pipe(clientRes);
      upstreamRes.on('end', () =>
        log('RES', status, method, url, `${Date.now() - started}ms`, `auth=${hasAuth}`, `session=${sessionId}`),
      );
    },
  );

  upstreamReq.on('error', (err) => {
    log('ERR', method, url, 'upstream error:', err.message);
    if (!clientRes.headersSent) clientRes.writeHead(502, { 'Content-Type': 'text/plain' });
    clientRes.end('upstream error');
  });

  clientReq.on('aborted', () => upstreamReq.destroy());
  if (body.length > 0) upstreamReq.write(body);
  upstreamReq.end();
});

// SSE and long-lived MCP streams must not be cut by the default idle timeouts.
server.timeout = 0;
server.headersTimeout = 0;
server.requestTimeout = 0;
server.keepAliveTimeout = 120000;

server.listen(PORT, HOST, () => {
  log(`listening on http://${HOST}:${PORT} -> https://${UPSTREAM_HOST}`, `rewriteMetadata=${REWRITE_METADATA}`);
  log(`sensitive headers never logged: ${[...SENSITIVE_HEADERS].join(', ')}`);
});

for (const sig of ['SIGINT', 'SIGTERM']) {
  process.on(sig, () => {
    log(`received ${sig}, shutting down`);
    server.close(() => {
      logStream.end();
      process.exit(0);
    });
    setTimeout(() => process.exit(0), 2000).unref();
  });
}

process.on('uncaughtException', (err) => log('FATAL uncaughtException:', err.stack || err.message));
process.on('unhandledRejection', (err) => log('FATAL unhandledRejection:', String(err)));
