const fs = require('fs');
const path = require('path');

const srcDir = path.join(__dirname, 'backend', 'src');

function walk(dir) {
  let results = [];
  const list = fs.readdirSync(dir);
  list.forEach(file => {
    file = path.join(dir, file);
    const stat = fs.statSync(file);
    if (stat && stat.isDirectory()) {
      results = results.concat(walk(file));
    } else {
      if (file.endsWith('.js') && !file.includes('database.js')) {
        results.push(file);
      }
    }
  });
  return results;
}

const files = walk(srcDir);
let changedFiles = 0;

files.forEach(file => {
  let content = fs.readFileSync(file, 'utf8');
  let originalContent = content;

  // Transform route handlers to async if they aren't already
  content = content.replace(/router\.(get|post|put|delete)\(['"](.*?)['"],\s*(?:async\s*)?\((req, res)\) => {/g, 'router.$1(\'$2\', async (req, res) => {');
  
  // Replace db.prepare chaining with await db.prepare
  // Matches: db.prepare(...).run(...) or .get(...) or .all(...)
  content = content.replace(/db\.prepare\((.*?)\)\.(get|all|run)\((.*?)\)/gs, 'await db.prepare($1).$2($3)');

  // Also replace `const something = db.prepare('...').get();` cases
  // Actually, the previous regex covers it, but we need to ensure the parent function is async.
  
  // Specific fix for logApiCall
  if (content.includes('function logApiCall')) {
    content = content.replace('function logApiCall', 'async function logApiCall');
    content = content.replace('logApiCall(', 'await logApiCall('); // if called within the same file
  }

  // Update triggerWebhook if used in workers
  if (content.includes('triggerWebhook')) {
    content = content.replace('function triggerWebhook', 'async function triggerWebhook');
    content = content.replace(/triggerWebhook\(/g, 'await triggerWebhook(');
  }

  if (content !== originalContent) {
    fs.writeFileSync(file, content, 'utf8');
    changedFiles++;
    console.log('Refatored:', file);
  }
});

console.log('Total files refactored:', changedFiles);
