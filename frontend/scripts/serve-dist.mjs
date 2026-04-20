import { createServer } from 'node:http';
import { createReadStream, existsSync } from 'node:fs';
import { stat } from 'node:fs/promises';
import { extname, join, normalize, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const rootDir = resolve(fileURLToPath(new URL('..', import.meta.url)));
const distDir = join(rootDir, 'dist');
const host = process.env.HOST || '127.0.0.1';
const port = Number(process.env.PORT || 3000);
const backendOrigin = (process.env.BACKEND_ORIGIN || 'http://127.0.0.1:8000').replace(/\/+$/, '');

const contentTypes = {
  '.css': 'text/css; charset=utf-8',
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.map': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.webp': 'image/webp'
};

function safePath(urlPath) {
  const decodedPath = decodeURIComponent(urlPath.split('?')[0]);
  const normalizedPath = normalize(decodedPath).replace(/^(\.\.[/\\])+/, '');
  const filePath = join(distDir, normalizedPath);
  return filePath.startsWith(distDir) ? filePath : join(distDir, 'index.html');
}

async function proxyRequest(req, res) {
  const target = new URL(req.url, backendOrigin);
  const headers = new Headers();
  Object.entries(req.headers).forEach(([key, value]) => {
    if (value) {
      headers.set(key, Array.isArray(value) ? value.join(', ') : value);
    }
  });
  headers.set('host', target.host);

  try {
    const upstream = await fetch(target, {
      method: req.method,
      headers,
      body: ['GET', 'HEAD'].includes(req.method || 'GET') ? undefined : req,
      duplex: 'half'
    });

    res.writeHead(upstream.status, Object.fromEntries(upstream.headers));
    if (!upstream.body) {
      res.end();
      return;
    }

    const reader = upstream.body.getReader();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      res.write(Buffer.from(value));
    }
    res.end();
  } catch (error) {
    res.writeHead(502, { 'content-type': 'application/json; charset=utf-8' });
    res.end(JSON.stringify({ detail: `Backend proxy failed: ${error.message}` }));
  }
}

async function serveFile(req, res) {
  let filePath = safePath(req.url || '/');
  if (!existsSync(filePath) || (await stat(filePath)).isDirectory()) {
    filePath = join(distDir, 'index.html');
  }

  const type = contentTypes[extname(filePath)] || 'application/octet-stream';
  res.writeHead(200, { 'content-type': type });
  createReadStream(filePath).pipe(res);
}

const server = createServer((req, res) => {
  if (req.url?.startsWith('/api') || req.url?.startsWith('/auth')) {
    proxyRequest(req, res);
    return;
  }

  serveFile(req, res).catch((error) => {
    res.writeHead(500, { 'content-type': 'text/plain; charset=utf-8' });
    res.end(error.message);
  });
});

server.listen(port, host, () => {
  console.log(`LiveMirror frontend ready at http://${host}:${port}`);
  console.log(`Proxying API requests to ${backendOrigin}`);
});
