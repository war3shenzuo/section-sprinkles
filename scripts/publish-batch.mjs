import { readFileSync, statSync } from 'node:fs';
import { relative, resolve, sep } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname } from 'node:path';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const repository = process.env.GITHUB_REPOSITORY || 'war3shenzuo/section-sprinkles';
const args = process.argv.slice(2);
const dryRunIndex = args.indexOf('--dry-run');
const dryRun = dryRunIndex !== -1;
if (dryRun) args.splice(dryRunIndex, 1);

const messageIndex = args.indexOf('--message');
if (messageIndex === -1 || !args[messageIndex + 1]) {
  throw new Error('Usage: publish-batch.mjs --message "Commit message" [--dry-run] <file>...');
}
const message = args[messageIndex + 1];
args.splice(messageIndex, 2);

if (args.length === 0) {
  throw new Error('At least one file is required.');
}

const files = args.map((input) => {
  const absolute = resolve(root, input);
  const path = relative(root, absolute).split(sep).join('/');
  if (path.startsWith('../') || path === '..') {
    throw new Error(`File is outside the repository: ${input}`);
  }
  if (!statSync(absolute).isFile()) {
    throw new Error(`Not a file: ${input}`);
  }
  return { absolute, path };
});

if (dryRun) {
  console.log(JSON.stringify({ repository, message, files: files.map(({ path }) => path) }, null, 2));
  process.exit(0);
}

function gh(endpoint, { method = 'GET', body } = {}) {
  const command = ['api', endpoint, '--method', method];
  if (body) {
    command.push('--input', '-');
  }
  const result = spawnSync('gh', command, {
    input: body ? JSON.stringify(body) : undefined,
    encoding: 'utf8',
    maxBuffer: 1024 * 1024 * 32
  });
  if (result.status !== 0) {
    throw new Error(result.stderr || result.stdout || `gh api failed: ${endpoint}`);
  }
  return result.stdout ? JSON.parse(result.stdout) : null;
}

const ref = gh(`repos/${repository}/git/ref/heads/main`);
const parent = ref.object.sha;
const baseCommit = gh(`repos/${repository}/git/commits/${parent}`);

const tree = [];
for (const file of files) {
  const content = readFileSync(file.absolute).toString('base64');
  const blob = gh(`repos/${repository}/git/blobs`, {
    method: 'POST',
    body: { content, encoding: 'base64' }
  });
  tree.push({ path: file.path, mode: '100644', type: 'blob', sha: blob.sha });
  console.log(`Uploaded blob: ${file.path}`);
}

const nextTree = gh(`repos/${repository}/git/trees`, {
  method: 'POST',
  body: { base_tree: baseCommit.tree.sha, tree }
});
const commit = gh(`repos/${repository}/git/commits`, {
  method: 'POST',
  body: { message, tree: nextTree.sha, parents: [parent] }
});
gh(`repos/${repository}/git/refs/heads/main`, {
  method: 'PATCH',
  body: { sha: commit.sha, force: false }
});

console.log(`Published ${files.length} files in commit ${commit.sha}`);
console.log(`https://github.com/${repository}/commit/${commit.sha}`);
