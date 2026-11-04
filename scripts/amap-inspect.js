// Belief · structure-only diagnostics. No outbound requests or raw-body logging.
(() => {
  try {
    const raw = $response.body;
    const obj = JSON.parse(raw);
    const matches = [];
    let visited = 0;
    function visit(value, path, depth) {
      if (++visited > 1800 || depth > 7) return;
      if (typeof value === "string") {
        if (/扫街榜|扫街帮|sa(?:(?:o|u))?jie|street.?rank/i.test(value)) matches.push(path);
        if (value.length < 300000 && /^[\s]*[\[{]/.test(value)) {
          try { visit(JSON.parse(value), path + ".$json", depth + 1); } catch (_) {}
        }
      } else if (value && typeof value === "object") {
        for (const key of Object.keys(value)) {
          // Report key names only; never log their values.
          visit(value[key], path + "." + (Array.isArray(value) ? "[]" : key), depth + 1);
        }
      }
    }
    visit(obj, "$", 0);
    const data = obj && typeof obj.data === "object" && obj.data ? obj.data : {};
    // Paths alone can include server-chosen map keys: emit only identifier-like keys.
    const safe = x => x.replace(/[^a-zA-Z0-9_.$\[\]-]/g, "_").slice(0, 220);
    console.log("[Belief][AMap] " + JSON.stringify({json: true, dataKeys: Object.keys(data).slice(0, 60).map(safe), campaignPaths: [...new Set(matches)].slice(0, 20).map(safe)}));
  } catch (_) { console.log("[Belief][AMap] response is not readable JSON"); }
  $done({});
})();
