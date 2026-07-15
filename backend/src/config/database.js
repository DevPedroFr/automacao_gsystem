const Database = require('better-sqlite3');
const path = require('path');
const fs = require('fs');

const dbPath = path.join(__dirname, '..', '..', 'database.sqlite');
const db = new Database(dbPath);

// Create tables (SQLite syntax)
const schema = `
CREATE TABLE IF NOT EXISTS campaigns (
  id TEXT PRIMARY KEY,
  niche TEXT NOT NULL,
  location TEXT NOT NULL,
  status TEXT DEFAULT 'processing',
  total_leads INTEGER DEFAULT 0,
  error_message TEXT,
  created_at DATETIME DEFAULT (datetime('now')),
  updated_at DATETIME DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS leads (
  id TEXT PRIMARY KEY,
  campaign_id TEXT,
  name TEXT NOT NULL,
  category TEXT,
  phone TEXT,
  website TEXT,
  address TEXT,
  city TEXT,
  google_rating REAL,
  google_reviews_count INTEGER DEFAULT 0,
  has_website INTEGER DEFAULT 0,
  pagespeed_score INTEGER,
  lcp_ms INTEGER,
  inp_ms INTEGER,
  cls REAL,
  seo_score INTEGER,
  has_instagram INTEGER DEFAULT 0,
  instagram_url TEXT,
  has_facebook INTEGER DEFAULT 0,
  has_linkedin INTEGER DEFAULT 0,
  social_last_post_days INTEGER,
  dms INTEGER DEFAULT 0,
  cos INTEGER DEFAULT 0,
  priority TEXT DEFAULT 'C',
  commercial_status TEXT DEFAULT 'new',
  source_provider TEXT DEFAULT 'mock',
  raw_data_path TEXT,
  image_url TEXT,
  created_at DATETIME DEFAULT (datetime('now')),
  FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS diagnostics (
  id TEXT PRIMARY KEY,
  lead_id TEXT UNIQUE,
  observed_facts TEXT,
  inferences TEXT,
  recommendations TEXT,
  email_draft TEXT,
  whatsapp_draft TEXT,
  instagram_draft TEXT,
  stitch_prompt TEXT,
  diagnostic_status TEXT DEFAULT 'completed',
  error_message TEXT,
  generated_at DATETIME DEFAULT (datetime('now')),
  FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY,
  value TEXT
);

CREATE TABLE IF NOT EXISTS api_call_logs (
  id TEXT PRIMARY KEY,
  provider TEXT NOT NULL,
  service_type TEXT NOT NULL,
  endpoint TEXT NOT NULL,
  status_code INTEGER,
  response_time_ms INTEGER,
  success INTEGER DEFAULT 1,
  error_message TEXT,
  created_at DATETIME DEFAULT (datetime('now'))
);
`;

db.exec(schema);
console.log('✅ Banco de dados local SQLite inicializado com sucesso.');

// Helper para converter PostgreSQL syntax ($1) de volta para SQLite (?) se necessário.
// Mas nosso refactor anterior manteve o padrão (?) do SQLite! 
// Isso porque o wrapper do pg é quem converteu ? para $1.
// Então podemos usar as queries exatamente como estão (usando ?, ou @params).

class AsyncDBWrapper {
  constructor(db) {
    this.db = db;
  }

  async ready() {
    return this;
  }

  // Permite que as chamadas com await continuem funcionando perfeitamente
  prepare(sql) {
    // Corrige funções do Postgres que injetamos antes de volta para SQLite
    sql = sql.replace(/CURRENT_TIMESTAMP/g, "datetime('now')");
    sql = sql.replace(/CURRENT_DATE/g, "date('now')");
    sql = sql.replace(/date_trunc\('month', CURRENT_DATE\)/g, "date('now', 'start of month')");
    
    const stmt = this.db.prepare(sql);
    
    return {
      async run(...args) {
        // Fallback for named parameters passed as single object
        if (args.length === 1 && typeof args[0] === 'object' && !Array.isArray(args[0])) {
           return stmt.run(args[0]);
        }
        return stmt.run(...args);
      },
      async get(...args) {
        if (args.length === 1 && typeof args[0] === 'object' && !Array.isArray(args[0])) {
           return stmt.get(args[0]);
        }
        return stmt.get(...args);
      },
      async all(...args) {
        if (args.length === 1 && typeof args[0] === 'object' && !Array.isArray(args[0])) {
           return stmt.all(args[0]);
        }
        return stmt.all(...args);
      }
    };
  }

  async exec(sql) {
    this.db.exec(sql);
  }
}

module.exports = new AsyncDBWrapper(db);
