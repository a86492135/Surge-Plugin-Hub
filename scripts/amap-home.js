// Belief: targeted homepage cleanup. Field references are documented in THIRD_PARTY_NOTICES.md.
(() => {
  try {
    const obj = JSON.parse($response.body);
    if (!obj || typeof obj !== "object" || Array.isArray(obj) || !obj.data || typeof obj.data !== "object") return $done({});
    const data = obj.data;
    let changed = false, iconsDisabled = 0, toolsRemoved = 0;
    if (/\/ws\/faas\/amap-navigation\/main-page(?:-assets|-aiqs)?(?:\?|$)/.test($request.url)) {
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
