const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const fs = require('fs-extra');
const path = require('path');
const https = require('https');

const app = express();
const PORT = 3000;
const DB_FILE = path.join(__dirname, 'db.json');

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(express.static(__dirname));

// Initialize local database
async function initDB() {
    if (!await fs.pathExists(DB_FILE)) {
        const initialData = {
            users: [],
            affiliates: [],
            sales: [],
            config: {
                lastUpdate: new Date().toISOString()
            }
        };
        await fs.writeJson(DB_FILE, initialData, { spaces: 2 });
        console.log('Local database initialized.');
    }
}

// Database Helpers
async function readDB() {
    return await fs.readJson(DB_FILE);
}

async function writeDB(data) {
    await fs.writeJson(DB_FILE, data, { spaces: 2 });
}

// API Routes
app.get('/api/db', async (req, res) => {
    try {
        const db = await readDB();
        res.json(db);
    } catch (error) {
        res.status(500).json({ error: 'Failed to read database' });
    }
});

app.post('/api/save', async (req, res) => {
    try {
        const { collection, data } = req.body;
        const db = await readDB();
        
        if (!db[collection]) {
            db[collection] = [];
        }
        
        db[collection].push({
            ...data,
            id: Date.now(),
            createdAt: new Date().toISOString()
        });
        
        await writeDB(db);
        res.json({ success: true, item: db[collection][db[collection].length - 1] });
    } catch (error) {
        res.status(500).json({ error: 'Failed to save to database' });
    }
});

// Affiliate Mock API
app.post('/api/affiliate', async (req, res) => {
    try {
        const { action, code, item_id, item_name, item_price, token, buyer_uid } = req.body;
        const db = await readDB();
        
        if (action === 'create_session') {
            const newToken = `local_session_${Date.now()}`;
            db.sales.push({
                token: newToken,
                code,
                item_id,
                item_name,
                item_price,
                status: 'pending',
                createdAt: new Date().toISOString()
            });
            await writeDB(db);
            return res.json({ token: newToken });
        }
        
        if (action === 'confirm_purchase') {
            const saleIndex = db.sales.findIndex(s => s.token === token);
            if (saleIndex !== -1) {
                db.sales[saleIndex].status = 'confirmed';
                db.sales[saleIndex].buyer_uid = buyer_uid;
                db.sales[saleIndex].confirmedAt = new Date().toISOString();
                await writeDB(db);
                return res.json({ ok: true, commission: (db.sales[saleIndex].item_price * 0.1).toFixed(2) });
            }
            return res.status(404).json({ ok: false, reason: 'Session not found' });
        }
        
        res.status(400).json({ error: 'Invalid action' });
    } catch (error) {
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Proxy Route for Roblox APIs (to avoid CORS and Supabase dependency locally)
app.get('/api/proxy', async (req, res) => {
    try {
        const targetUrl = req.query.url;
        if (!targetUrl) return res.status(400).json({ error: 'Missing url parameter' });

        const response = await fetch(targetUrl);
        const data = await response.json();
        res.json(data);
    } catch (error) {
        console.error('Proxy error:', error);
        res.status(500).json({ error: 'Failed to fetch from Roblox API' });
    }
});

// Serve index.html for all other routes
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Start Server
initDB().then(() => {
    app.listen(PORT, '0.0.0.0', () => {
        console.log(`Server running on http://0.0.0.0:${PORT}`);
    });
});
