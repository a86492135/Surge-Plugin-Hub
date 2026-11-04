const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
function run(file, url, body) {
  const result = { done: [], logs: [] };
  const context = vm.createContext({
    $request: { url }, $response: { body },
    $done: value => result.done.push(JSON.parse(JSON.stringify(value))),
    console: { log: value => result.logs.push(value) },
  });
  vm.runInContext(fs.readFileSync(path.join(__dirname, '../scripts/', file), 'utf8'), context, {timeout: 1000});
  assert.equal(result.done.length, 1);
  return result;
}
let result = run('weibo-launch.js', 'https://sdkapp.uve.weibo.com/interface/sdk/sdkad.php', JSON.stringify({ads:[1],show_push_splash_ad:true,account:'keep'})+'OK');
assert.equal(result.done[0].body, '{"ads":[],"show_push_splash_ad":false,"account":"keep"}OK');
result = run('weibo-launch.js', 'https://wbapp.uve.weibo.com/wbapplua/wbpullad.lua', '{"cached_ad":{"ads":[1],"other":2},"keep":3}');
assert.deepEqual(JSON.parse(result.done[0].body), {cached_ad:{ads:[],other:2},keep:3});
for (const body of ['not-json','null','[]']) {
  assert.deepEqual(run('weibo-launch.js','https://wbapp.uve.weibo.com/wbapplua/wbpullad.lua',body).done[0],{});
}
result = run('amap-inspect.js','https://m5.amap.com/ws/shield/frogserver/aocs/updatable/26?token=DO_NOT_LOG', JSON.stringify({data:{example:{title:'扫街榜2026',account:'PRIVATE_ACCOUNT',latitude:'PRIVATE_LOCATION'}}}));
assert.deepEqual(result.done[0],{});
assert(result.logs[0].includes('$.data.example.title'));
for (const secret of ['PRIVATE_ACCOUNT','PRIVATE_LOCATION','DO_NOT_LOG','扫街榜2026']) assert(!result.logs.join('').includes(secret));
assert.deepEqual(run('amap-inspect.js','https://m5.amap.com/test','binary-data').done[0],{});
console.log('Local script fixtures passed; unknown payloads pass through and private values are not logged.');
