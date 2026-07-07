import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import * as path from 'path';
import * as fs from 'fs';
import { fileURLToPath } from 'url';
import { runOverviewScript } from 'mycelium-mind/build/utils/overview-runner.js';
import { getMockTimelineGraph } from './mock-data.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const TEST_ROOT = path.resolve(__dirname, '..', '..', '..', 'temp-timeline-script-tests');

describe('Local timeline.js script tests', () => {
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

  it('should execute timeline script successfully and write expected pages', async () => {
    const sessionGraph = getMockTimelineGraph();
    const scriptPath = path.resolve(__dirname, '..', 'timeline.js');

    await runOverviewScript(scriptPath, wikiDir, sessionGraph);

    const timelineFile = path.join(wikiDir, 'overviews', 'timeline.md');
    const timelineGraphicFile = path.join(wikiDir, 'overviews', 'timeline-graphic.md');

    expect(fs.existsSync(timelineFile)).toBe(true);
    expect(fs.existsSync(timelineGraphicFile)).toBe(true);

    const timelineContent = fs.readFileSync(timelineFile, 'utf8');
    expect(timelineContent).toContain('## 2011');
    expect(timelineContent).toContain('[[Principles of Credit Ratings]]');

    const graphicContent = fs.readFileSync(timelineGraphicFile, 'utf8');
    expect(graphicContent).toContain('data-events=');
    expect(graphicContent).toContain('mermaid');
  });
});
