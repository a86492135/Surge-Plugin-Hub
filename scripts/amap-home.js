// Belief: targeted homepage cleanup. Field references are documented in THIRD_PARTY_NOTICES.md.
(() => {
  if (typeof $response === "undefined") {
    try {
      const raw = typeof $request.body === "string" ? $request.body : "";
      const safeKey = key => /^[A-Za-z_][A-Za-z0-9_-]{0,63}$/.test(key) ? key : "[key]";
      let format = raw ? "opaque" : "empty-or-binary", keys = [], parsed;
      try { parsed = JSON.parse(raw); format = "json"; keys = Object.keys(parsed || {}).map(safeKey).slice(0, 30); } catch (_) {
        if (/^[A-Za-z_][A-Za-z0-9_-]*=/.test(raw)) {
          format = "form";
          parsed = {};
          for (const pair of raw.split("&").slice(0, 80)) {
            const index = pair.indexOf("=");
            if (index < 0) continue;
            const key = decodeURIComponent(pair.slice(0, index));
            keys.push(safeKey(key));
            parsed[key] = decodeURIComponent(pair.slice(index + 1));
          }
        }
      }
      const tabPaths = [];
      let visited = 0;
      function find(value, path, depth) {
        if (++visited > 3000 || depth > 8) return;
        if (typeof value === "string" && value.length < 300000 && /^\s*[\[{]/.test(value)) {
          try { find(JSON.parse(value), path + ".$json", depth + 1); } catch (_) {}
        } else if (value && typeof value === "object") for (const key of Object.keys(value)) {
          const child = (path + "." + (Array.isArray(value) ? "[]" : safeKey(key))).slice(0, 180);
          if (key === "amapHomeTabConfig") tabPaths.push({path: child, type: typeof value[key], keys: value[key] && typeof value[key] === "object" ? Object.keys(value[key]).slice(0, 12).map(safeKey) : []});
          find(value[key], child, depth + 1);
        }
      }
      find(parsed, "$", 0);
      console.log("[Belief][AMap Tabs Request] " + JSON.stringify({diagnosticVersion: 2, format, keys: keys.slice(0, 30), tabPaths: tabPaths.slice(0, 10)}));
    } catch (_) { console.log("[Belief][AMap Tabs Request] metadata unavailable"); }
    return $done({});
  }
  // Temporary read-only layout diagnostics for AMap 17.01.1.2014.
  // Only structural keys, types and the five fixed tab labels may be logged.
  function inspectTabs(data) {
    const labels = new Set(["首页", "我的", "探索", "长按说话", "打车"]);
    const safeKey = key => /^[A-Za-z_][A-Za-z0-9_-]{0,63}$/.test(key) ? key : "[key]";
    const tabKey = /tab.?bar|bottom.?(?:tab|bar|nav)|(?:main|home).?tab|tab.?config|footer|redesign/i;
    const matches = [], structures = [];
    let visited = 0, shaped = 0;
    function shape(value, depth) {
      if (++shaped > 600 || depth > 5) return "[limit]";
      if (typeof value === "string") {
        if (labels.has(value)) return value;
        if (value.length < 300000 && /^\s*[\[{]/.test(value)) {
          try { return {$json: shape(JSON.parse(value), depth + 1)}; } catch (_) {}
        }
        return value.length ? "[string]" : "[empty]";
      }
      if (Array.isArray(value)) return {length: value.length, sample: value.slice(0, 6).map(v => shape(v, depth + 1))};
      if (value && typeof value === "object") return Object.fromEntries(Object.keys(value).slice(0, 20).map(k => [safeKey(k), shape(value[k], depth + 1)]));
      return value === null ? "[null]" : "[" + typeof value + "]";
    }
    function visit(value, path, depth) {
      if (++visited > 5000 || depth > 9) return;
      if (typeof value === "string") {
        if (labels.has(value) && matches.length < 30) matches.push({path, label: value});
        if (value.length < 300000 && /^\s*[\[{]/.test(value)) {
          try { visit(JSON.parse(value), path + ".$json", depth + 1); } catch (_) {}
        }
      } else if (value && typeof value === "object") {
        for (const key of Object.keys(value)) {
          const childPath = (path + "." + (Array.isArray(value) ? "[]" : safeKey(key))).slice(0, 180);
          if (tabKey.test(key) && structures.length < 8) structures.push({path: childPath, shape: shape(value[key], 0)});
          visit(value[key], childPath, depth + 1);
        }
      }
    }
    visit(data, "$.data", 0);
    const keys = Object.keys(data);
    const endpoint = ($request.url.match(/^https:\/\/[^/]+([^?#]*)/) || [])[1] || "[unknown]";
    const tab = data.amapHomeTabConfig;
    const tabState = tab && typeof tab === "object" ? {status: typeof tab.status === "number" ? tab.status : "[other]", emptyVersion: tab.version === "", emptyValue: tab.value === ""} : null;
    console.log("[Belief][AMap Tabs] " + JSON.stringify({diagnosticVersion: 2, endpoint, tabState, dataKeys: keys.slice(0, 45).map(safeKey), candidateKeys: keys.filter(k => /tab|bottom|layout|redesign|home|speech|voice|ai_/i.test(k)).slice(0, 80).map(safeKey), labels: matches, structures}));
  }
  try {
    const obj = JSON.parse($response.body);
    if (!obj || typeof obj !== "object" || Array.isArray(obj) || !obj.data || typeof obj.data !== "object") return $done({});
    const data = obj.data;
    if (/\/ws\/shield\/frogserver\/aocs\/updatable\/(?:1|26)(?:\?|$)/.test($request.url)) {
      inspectTabs(data);
      return $done({});
    }
    let changed = false, iconsDisabled = 0, toolsRemoved = 0;
    if (/\/ws\/faas\/amap-navigation\/main-page(?:-assets|-aiqs)?(?:\?|$)/.test($request.url)) {
      inspectTabs(data);
      if (Array.isArray(data.mapBizList)) for (const card of data.mapBizList) {
        const icon = card && card.dataKey === "UserAssetsVirtualCard" && card.bizData && card.bizData.newIcon;
        if (icon && typeof icon === "object" && !Array.isArray(icon)) {
          Object.assign(icon, {switch: "0", lottieUrl: "", icon: "", scheme: ""});
          changed = true;
          iconsDisabled++;
        }
      }
    } else if (/\/ws\/opc\/tools\/list(?:\?|$)/.test($request.url)) {
      const clean = list => list.filter(item => {
        const remove = item && typeof item === "object" && typeof item.name === "string" && /扫街榜|扫街帮/.test(item.name);
        if (remove) { toolsRemoved++; changed = true; }
        return !remove;
      });
      if (Array.isArray(data.category)) for (const category of data.category) {
        if (category && Array.isArray(category.tools)) category.tools = clean(category.tools);
      }
      for (const key of ["default", "recommend"]) if (Array.isArray(data[key])) data[key] = clean(data[key]);
    } else return $done({});
    // Counts only: no account, coordinates, URL parameters or response values.
    console.log("[Belief][AMap Home] " + JSON.stringify({iconsDisabled, toolsRemoved}));
    $done(changed ? {body: JSON.stringify(obj)} : {});
  } catch (_) { $done({}); }
})();
