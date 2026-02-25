/**
 * Google Play 榜单爬虫（Node.js）
 * 使用 google-play-scraper 包，输出 JSON 到 stdout
 * 由 Python 主程序调用：node scrapers/googleplay_scraper.js > /tmp/gplay_data.json
 */

const gplay = require('google-play-scraper').default;

const REGIONS = {
  us: { country: 'us', lang: 'en', name: '美国' },
  gb: { country: 'gb', lang: 'en', name: '英国' },
  de: { country: 'de', lang: 'de', name: '德国' },
  fr: { country: 'fr', lang: 'fr', name: '法国' },
  jp: { country: 'jp', lang: 'ja', name: '日本' },
  kr: { country: 'kr', lang: 'ko', name: '韩国' },
  id: { country: 'id', lang: 'id', name: '印度尼西亚' },
  th: { country: 'th', lang: 'th', name: '泰国' },
  sg: { country: 'sg', lang: 'en', name: '新加坡' },
  vn: { country: 'vn', lang: 'vi', name: '越南' },
};

const CHARTS = [
  { collection: 'TOP_FREE', name: '免费游戏榜' },
  { collection: 'TOP_PAID', name: '付费游戏榜' },
  { collection: 'GROSSING',  name: '畅销榜' },
];

const today = new Date().toISOString().slice(0, 10);

// 延迟函数
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function fetchChart(regionCode, chartCfg) {
  const region = REGIONS[regionCode];
  try {
    const results = await gplay.list({
      collection: gplay.collection[chartCfg.collection],
      category: gplay.category.GAME,
      country: region.country,
      lang: region.lang,
      num: 100,
      fullDetail: false,
    });

    return results.map((app, i) => ({
      rank: i + 1,
      app_id: app.appId,
      name: app.title,
      artist: app.developer,
      genre: app.genre || 'GAME',
      genre_id: app.genreId || 'GAME',
      url: app.url,
      artwork: app.icon,
      score: app.score,
      ratings: app.ratings,
      installs: app.installs,
      price: app.price,
      region: regionCode,
      region_name: region.name,
      chart_type: chartCfg.collection,
      chart_name: chartCfg.name,
      store: 'google_play',
      fetch_date: today,
      fetch_ts: new Date().toISOString(),
    }));
  } catch (e) {
    process.stderr.write(`[GooglePlay] 失败 ${region.name} ${chartCfg.name}: ${e.message}\n`);
    return [];
  }
}

async function main() {
  const allData = [];

  for (const regionCode of Object.keys(REGIONS)) {
    for (const chartCfg of CHARTS) {
      process.stderr.write(`[GooglePlay] 拉取 ${REGIONS[regionCode].name} ${chartCfg.name}...\n`);
      const apps = await fetchChart(regionCode, chartCfg);
      allData.push(...apps);
      process.stderr.write(`  → 获取 ${apps.length} 条\n`);
      await sleep(1500); // 避免请求过快
    }
  }

  process.stderr.write(`\n[GooglePlay] 总计 ${allData.length} 条\n`);
  // 结果输出到 stdout，Python 读取
  process.stdout.write(JSON.stringify(allData));
}

main();
