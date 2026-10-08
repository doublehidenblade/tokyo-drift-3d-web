/* Godot 4.7.2 static-pack transport. No service worker, external host or persistent partial cache. */
(() => {
  'use strict';
  const MAX_PACK = 512 * 1024 * 1024;
  const CHUNK = 8 * 1024 * 1024;
  const hex = bytes => Array.from(new Uint8Array(bytes), b => b.toString(16).padStart(2, '0')).join('');
  const digest = async bytes => hex(await crypto.subtle.digest('SHA-256', bytes));
  const fail = message => { throw new Error(message); };
  const validHash = value => typeof value === 'string' && /^[a-f0-9]{64}$/.test(value);
  const pause = ms => new Promise(resolve => setTimeout(resolve, ms));

  async function readExact(url, size, signal, progress, timeoutMs) {
    const cancel = new AbortController();
    const abort = () => cancel.abort();
    signal.addEventListener('abort', abort, {once: true});
    const timer = setTimeout(abort, timeoutMs);
    let reader, response;
    try {
      if (signal.aborted) abort();
      response = await fetch(url, {cache: 'no-cache', credentials: 'same-origin', signal: cancel.signal});
      if (!response.ok || response.type === 'opaque') fail(`Download failed (${response.status}): ${url.pathname}`);
      reader = response.body.getReader();
      const bytes = new Uint8Array(size);
      let offset = 0;
      while (true) {
        const {done, value} = await reader.read();
        if (done) break;
        if (offset + value.byteLength > size) fail('Download exceeds declared length');
        bytes.set(value, offset); offset += value.byteLength; progress?.(offset);
      }
      if (offset !== size) fail(`Incomplete download: ${offset}/${size}`);
      return bytes;
    } finally {
      clearTimeout(timer); signal.removeEventListener('abort', abort);
      // Abort even when status validation failed before acquiring a reader.
      cancel.abort();
      await (reader ? reader.cancel() : response?.body?.cancel())?.catch(() => {});
    }
  }

  async function initializeEngine(engine, config, signal) {
    // Godot's exported preloader has no AbortSignal API and retries failed fetches.
    // Scope interception to this engine's Wasm URL; preserve every other fetch.
    const wasmURL = new URL(`${config.executable}.wasm`, location.href).href;
    const originalFetch = window.fetch;
    const cancel = new AbortController();
    const guardedFetch = function(input, options) {
      const url = new URL(input instanceof Request ? input.url : input, location.href).href;
      if (url !== wasmURL) return originalFetch.call(this, input, options);
      return originalFetch.call(this, input, {...options, signal: cancel.signal});
    };
    window.fetch = guardedFetch;
    let timer, onAbort;
    const stopped = new Promise((resolve, reject) => {
      onAbort = () => { cancel.abort(); reject(new Error('Engine initialization cancelled. Reload to retry.')); };
      signal.addEventListener('abort', onAbort, {once: true});
      timer = setTimeout(() => {
        cancel.abort(); reject(new Error('Engine initialization timed out after 60 seconds. Reload to retry.'));
      }, 60000);
      if (signal.aborted) onAbort();
    });
    try {
      const pending = engine.init(config.executable);
      // A late engine resolution must not leave a running instance after cancellation.
      pending.then(() => { if (cancel.signal.aborted) engine.requestQuit(); }, () => {});
      await Promise.race([pending, stopped]);
      if (window.fetch === guardedFetch) window.fetch = originalFetch;
    } catch (error) {
      cancel.abort(); engine.requestQuit(); engine.unload();
      // Keep the cancelled URL guard until reload: Godot may schedule delayed retries.
      // Restoring fetch here would let those retries reopen uncancellable requests.
      throw error;
    } finally {
      clearTimeout(timer); signal.removeEventListener('abort', onAbort);
    }
  }

  function validate(manifest, releaseId) {
    if (manifest.schema !== 1 || manifest.release !== releaseId || !/^[a-f0-9]{40}$/.test(manifest.source_sha)) fail('Invalid release manifest');
    const pack = manifest.pack;
    if (!pack || pack.path !== 'index.pck' || !Number.isSafeInteger(pack.bytes) || pack.bytes <= 0 || pack.bytes > MAX_PACK || !validHash(pack.sha256)) fail('Invalid pack bounds/hash');
    if (!Array.isArray(pack.chunks) || pack.chunks.length !== Math.ceil(pack.bytes / CHUNK)) fail('Invalid chunk count');
    let offset = 0;
    for (const [i, chunk] of pack.chunks.entries()) {
      if (chunk.offset !== offset || chunk.bytes !== Math.min(CHUNK, pack.bytes - offset) || !validHash(chunk.sha256) || chunk.path !== `pck/${String(i).padStart(4, '0')}-${chunk.sha256}.bin`) fail('Invalid chunk ordering/path/bounds');
      offset += chunk.bytes;
    }
    if (offset !== pack.bytes) fail('Invalid pack length');
    return pack;
  }

  async function startGame(engine, config, selection) {
    const state = {schema: 1, release: selection.release, phase: 'manifest', verifiedBytes: 0, attempts: [], samples: [], status: 'loading'};
    window.__tdDelivery = state;
    const sample = phase => {
      state.phase = phase;
      state.samples.push({phase, timeMs: performance.now(), jsHeapBytes: performance.memory?.usedJSHeapSize ?? null});
      window.dispatchEvent(new CustomEvent('td-delivery-phase', {detail: phase}));
    };
    const controller = new AbortController();
    window.addEventListener('pagehide', () => controller.abort(), {once: true});
    const signal = controller.signal;
    const report = (value, text) => window.tdLoadProgress?.(value, text);
    let assembled = null;
    try {
      if (!validHash(selection.manifestSha256) || !Number.isSafeInteger(selection.manifestBytes) || selection.manifestBytes < 1 || selection.manifestBytes > 65536) fail('Invalid pinned manifest');
      const manifestURL = new URL(selection.manifestUrl, location.href);
      if (manifestURL.origin !== location.origin || !manifestURL.pathname.endsWith('/pack-manifest.json')) fail('Manifest must be in this release');
      const manifestBytes = await readExact(manifestURL, selection.manifestBytes, signal, null, 30000);
      if (await digest(manifestBytes) !== selection.manifestSha256) fail('Manifest SHA256 mismatch');
      const manifest = JSON.parse(new TextDecoder().decode(manifestBytes));
      const pack = validate(manifest, selection.release);
      state.source = manifest.source_sha; state.packSha256 = pack.sha256; state.packBytes = pack.bytes;
      assembled = new Uint8Array(pack.bytes);
      sample('download');
      for (const [i, chunk] of pack.chunks.entries()) {
        let verified = false;
        for (let attempt = 1; attempt <= 3; attempt++) {
          if (signal.aborted) throw new DOMException('Download cancelled', 'AbortError');
          const record = {chunk: i, attempt}; state.attempts.push(record);
          try {
            const bytes = await readExact(new URL(chunk.path, manifestURL), chunk.bytes, signal,
              loaded => report(.65 * (state.verifiedBytes + loaded) / pack.bytes, `Downloading game ${Math.floor((state.verifiedBytes + loaded) / 1048576)}/${Math.ceil(pack.bytes / 1048576)} MiB`), 60000);
            if (await digest(bytes) !== chunk.sha256) fail(`Chunk ${i} SHA256 mismatch`);
            assembled.set(bytes, chunk.offset);
            state.verifiedBytes += bytes.byteLength; record.ok = true; verified = true;
            sample(`chunk-${i}-verified`);
            break;
          } catch (error) {
            record.error = String(error);
            if (signal.aborted || attempt === 3) throw error;
            report(.65 * state.verifiedBytes / pack.bytes, `Retrying download (${attempt}/3)`);
            await pause(250 * attempt);
          }
        }
        if (!verified) fail(`Chunk ${i} was not verified`);
      }
      report(.66, 'Checking game files'); sample('pack-hash');
      if (await digest(assembled) !== pack.sha256) fail('Reassembled pack SHA256 mismatch');
      state.packVerified = true; sample('pack-verified');
      // Delay Wasm allocation until download + integrity work finishes. startGame would fetch index.pck again.
      report(.68, 'Starting engine'); sample('engine-init');
      await initializeEngine(engine, config, signal);
      sample('engine-initialized');
      await engine.preloadFile(assembled.buffer, 'index.pck');
      await engine.start({args: ['--main-pack', 'index.pck', ...(config.args || [])]});
      assembled = null;
      state.status = 'engine-started'; sample('engine-started');
      return engine;
    } catch (error) {
      assembled = null; controller.abort(); state.status = 'failed'; state.error = String(error); sample('failed');
      report(0, 'Game could not start. Reload to retry.');
      throw error;
    }
  }
  window.TDChunked = Object.freeze({startGame});
})();
