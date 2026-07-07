import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import * as path from 'path';
import * as fs from 'fs';
import { fileURLToPath } from 'url';
import { runOverviewScript } from 'mycelium-mind/build/utils/overview-runner.js';
import { getMockSocialGraph } from './mock-data.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const TEST_ROOT = path.resolve(__dirname, '..', '..', '..', 'temp-social-graph-script-tests');

describe('Local social-graph.js script tests', () => {
  const wikiPath = path.join(TEST_ROOT, 'TestWiki');
  const wikiDir = path.join(wikiPath, 'wiki');

  beforeEach(() => {
    fs.mkdirSync(TEST_ROOT, { recursive: true });
    fs.mkdirSync(wikiDir, { recursive: true });
    fs.mkdirSync(path.join(wikiDir, 'overviews'), { recursive: true });
  });

  afterEach(() => {
    fs.rmSync(TEST_ROOT, { recursive: true, force: true });
  });

  it('should execute social-graph script successfully and write expected pages', async () => {
    const sessionGraph = getMockSocialGraph();
    const scriptPath = path.resolve(__dirname, '..', 'social-graph.js');

    await runOverviewScript(scriptPath, wikiDir, sessionGraph);

    const socialFile = path.join(wikiDir, 'overviews', 'social-graph.md');
    const socialGraphicFile = path.join(wikiDir, 'overviews', 'social-graph-graphic.md');

    expect(fs.existsSync(socialFile)).toBe(true);
    expect(fs.existsSync(socialGraphicFile)).toBe(true);

    const socialContent = fs.readFileSync(socialFile, 'utf8');
    expect(socialContent).toContain('| [[Alex Stomper]] | lectured on | [[Financial Economics]] |');

    const graphicContent = fs.readFileSync(socialGraphicFile, 'utf8');
    expect(graphicContent).toContain('mermaid');
    expect(graphicContent).toContain('flowchart LR');
  });
});
