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
result = run('amap-inspect.js','https://m5-x.amap.com/ws/home?token=SECRET_TOKEN', JSON.stringify({data:{MaphomeOperateConfig:JSON.stringify({entry:{title:'扫街榜2026',url:'PRIVATE_URL',enabled:true}})}}));
assert.deepEqual(result.done[0],{});
const diagnostic = JSON.parse(result.logs[0].replace('[Belief][AMap] ',''));
assert.equal(diagnostic.diagnosticVersion,3);
assert(diagnostic.campaignPaths.includes('$.data.MaphomeOperateConfig.$json.entry.title'));
assert.equal(diagnostic.homepageShapes.MaphomeOperateConfig.$json.entry.enabled,'[boolean]');
for (const secret of ['PRIVATE_URL','SECRET_TOKEN','扫街榜2026']) assert(!result.logs.join('').includes(secret));
result = run('amap-inspect.js','https://m5.amap.com/ws/shield/dsp/app/startup/init',JSON.stringify({data:{app_conf_init:{datas:{memo:[{para1:'saojie',fileDesc:[{title:'扫街榜2026',url:'PRIVATE_ASSET'}]},{para1:'other'}]}}}}));
const startupDiagnostic = JSON.parse(result.logs[0].replace('[Belief][AMap] ',''));
assert.equal(startupDiagnostic.homepageShapes.startupCampaignResources.length,1);
assert.equal(startupDiagnostic.homepageShapes.startupCampaignResources[0].fileDesc.sample[0].title,'[campaign string]');
assert(!result.logs.join('').includes('PRIVATE_ASSET'));
const homepage = {data:{mapBizList:[{dataKey:'UserAssetsVirtualCard',bizData:{newIcon:{switch:'1',lottieUrl:'animation',icon:'image',scheme:'link',other:'preserve'},balance:'preserve'}},{dataKey:'FindCarVirtualCard',bizData:{keep:true}}],cardList:[{dataKey:'ContinueNavigationCard'}]}};
result = run('amap-home.js','https://m5.amap.com/ws/faas/amap-navigation/main-page-assets?token=PRIVATE_TOKEN',JSON.stringify(homepage));
const cleanedHome = JSON.parse(result.done[0].body);
assert.deepEqual(cleanedHome.data.mapBizList[0].bizData.newIcon,{switch:'0',lottieUrl:'',icon:'',scheme:'',other:'preserve'});
assert.equal(cleanedHome.data.mapBizList[0].bizData.balance,'preserve');
assert.deepEqual(cleanedHome.data.mapBizList[1],homepage.data.mapBizList[1]);
assert.deepEqual(cleanedHome.data.cardList,homepage.data.cardList);
assert(!result.logs.join('').includes('PRIVATE_TOKEN'));
result = run('amap-home.js','https://sns.amap.com/ws/opc/tools/list?x=1',JSON.stringify({data:{category:[{tools:[{name:'扫街榜2026'},{name:'公交'},null]}],default:[{name:'扫街榜'},{name:'地铁'}],recommend:[{name:'高德扫街榜2026'}],other:'keep'}}));
assert.deepEqual(JSON.parse(result.done[0].body),{data:{category:[{tools:[{name:'公交'},null]}],default:[{name:'地铁'}],recommend:[],other:'keep'}});
for (const body of ['not-json','null','[]','{"data":{"other":1}}']) assert.deepEqual(run('amap-home.js','https://m5.amap.com/ws/faas/amap-navigation/main-page',body).done[0],{});
result = run('amap-home.js','https://m5.amap.com/ws/shield/frogserver/aocs/updatable/1?token=DO_NOT_LOG',JSON.stringify({data:{home_tab_config:{value:JSON.stringify({tabBar:[{title:'首页'},{title:'探索',account:'PRIVATE_ACCOUNT'},{title:'长按说话'},{title:'打车'},{title:'我的',location:'PRIVATE_LOCATION'}]})},other:'PRESERVE'}}));
assert.deepEqual(result.done[0],{});
const tabDiagnostic = JSON.parse(result.logs.find(line => line.startsWith('[Belief][AMap Tabs] ')).replace('[Belief][AMap Tabs] ',''));
assert(tabDiagnostic.labels.some(item => item.label === '长按说话'));
assert(tabDiagnostic.candidateKeys.includes('home_tab_config'));
for (const secret of ['PRIVATE_ACCOUNT','PRIVATE_LOCATION','DO_NOT_LOG','PRESERVE']) assert(!result.logs.join('').includes(secret));
const requestResults = {done:[],logs:[]};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../scripts/amap-home.js'),'utf8'),{
  $request:{url:'https://m5.amap.com/ws/shield/frogserver/aocs/updatable/1?secret=HIDDEN',body:'config='+encodeURIComponent(JSON.stringify({amapHomeTabConfig:'PRIVATE_VERSION',account:'PRIVATE_ACCOUNT'}))},
  $done:value=>requestResults.done.push(JSON.parse(JSON.stringify(value))),console:{log:value=>requestResults.logs.push(value)}
},{timeout:1000});
assert.deepEqual(requestResults.done,[{}]);
const requestMeta=JSON.parse(requestResults.logs[0].replace('[Belief][AMap Tabs Request] ',''));
assert.equal(requestMeta.format,'form');
assert.equal(requestMeta.tabPaths[0].path,'$.config.$json.amapHomeTabConfig');
for (const secret of ['PRIVATE_ACCOUNT','PRIVATE_VERSION','HIDDEN']) assert(!requestResults.logs.join('').includes(secret));
console.log('Local script fixtures passed; unknown payloads pass through and private values are not logged.');
