// Belief: temporary structure-only diagnostics. No outbound requests or payload values.
(() => {
  const marker = /扫街榜|扫街帮|sao?jie|street.?rank/i;
  const safeKey = key => /^[A-Za-z_][A-Za-z0-9_-]{0,63}$/.test(key) ? key : "[key]";
  const safePath = path => path.slice(0, 240);
  try {
    const obj = JSON.parse($response.body);
    const data = obj && obj.data && typeof obj.data === "object" ? obj.data : {};
    const matches = new Set();
    let count = 0;
    function scan(value, path, depth) {
      if (++count > 5000 || depth > 10) return;
      if (marker.test(path)) matches.add(safePath(path));
      if (typeof value === "string") {
        if (marker.test(value)) matches.add(safePath(path));
        if (value.length < 300000 && /^\s*[\[{]/.test(value)) {
          try { scan(JSON.parse(value), path + ".$json", depth + 1); } catch (_) {}
        }
      } else if (value && typeof value === "object") {
        for (const key of Object.keys(value)) {
          scan(value[key], path + (Array.isArray(value) ? ".[]" : "." + safeKey(key)), depth + 1);
        }
      }
    }
    const priorities = ["MaphomeOperateConfig", "amap_basemap_config", "cloud_resouce", "nearby_config", "c3_portal", "homepage_resource_config"];
    const shapes = {};
    let shapeCount = 0;
    function shape(value, depth) {
      if (++shapeCount > 800 || depth > 6) return "[limit]";
      if (typeof value === "string") {
        if (value.length < 300000 && /^\s*[\[{]/.test(value)) {
          try { return {$json: shape(JSON.parse(value), depth + 1)}; } catch (_) {}
        }
        return marker.test(value) ? "[campaign string]" : (value.length ? "[string]" : "[empty]");
      }
      if (Array.isArray(value)) return {arrayLength: value.length, sample: value.slice(0, 4).map(v => shape(v, depth + 1))};
      if (value && typeof value === "object") {
        const result = {};
        for (const key of Object.keys(value).slice(0, 50)) result[safeKey(key)] = shape(value[key], depth + 1);
        return result;
      }
      return value === null ? "[null]" : "[" + typeof value + "]";
    }
    // Scan the homepage configuration first, before a large cloud response can exhaust the budget.
    for (const key of priorities) {
      if (Object.prototype.hasOwnProperty.call(data, key)) {
        scan(data[key], "$.data." + key, 0);
        shapes[key] = shape(data[key], 0);
      }
    }
    scan(obj, "$", 0);
    // Only expand campaign-matching startup resource records, never their raw values.
    const memo = data.app_conf_init && data.app_conf_init.datas && data.app_conf_init.datas.memo;
    if (Array.isArray(memo)) {
      shapeCount = 0;
      shapes.startupCampaignResources = memo.filter(record => marker.test(JSON.stringify(record))).slice(0, 5).map(record => shape(record, 0));
    }
    const match = $request.url.match(/^https?:\/\/([^/?#]+)([^?#]*)/);
    const endpoint = match ? match[1] + match[2].replace(/\d{4,}/g, "[n]") : "[unknown]";
    console.log("[Belief][AMap] " + JSON.stringify({diagnosticVersion: 3, endpoint, rootKeys: Object.keys(obj || {}).slice(0, 20).map(safeKey), dataKeys: Object.keys(data).slice(0, 100).map(safeKey), campaignPaths: [...matches].slice(0, 30), homepageShapes: shapes}));
  } catch (_) { console.log("[Belief][AMap] diagnosticVersion=3 response is not readable JSON"); }
  $done({});
})();
