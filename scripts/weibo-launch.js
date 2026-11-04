// Belief · splash payload cleanup. Returns the original payload on unknown input.
(() => {
  try {
    const raw = $response.body;
    const wrapped = $request.url.includes("/interface/sdk/sdkad.php");
    const first = raw.indexOf("{");
    const last = raw.lastIndexOf("}");
    const data = JSON.parse(wrapped && first >= 0 ? raw.slice(first, last + 1) : raw);
    if (!data || typeof data !== "object" || Array.isArray(data)) return $done({});
    if (Array.isArray(data.ads)) data.ads = [];
    if (Object.prototype.hasOwnProperty.call(data, "show_push_splash_ad")) data.show_push_splash_ad = false;
    if (data.cached_ad && Array.isArray(data.cached_ad.ads)) data.cached_ad.ads = [];
    $done({body: JSON.stringify(data) + (wrapped && /OK\s*$/.test(raw) ? "OK" : "")});
  } catch (_) { $done({}); }
})();
